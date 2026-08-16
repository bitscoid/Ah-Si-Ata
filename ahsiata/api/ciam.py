"""CIAM (OIDC) authentication endpoints.

Uses BASE_CIAM_URL. Token types: `SMS` (OTP flow), `DEVICEID` (session extend).
"""
from __future__ import annotations

import base64
import json
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import requests

from ahsiata.config import CONFIG
from ahsiata.constants import CIAMEndpoint, CIAMHeader, LANG_EN
from ahsiata.api.encrypt import (
    ax_api_signature,
    ax_device_id,
    java_like_timestamp,
    load_ax_fp,
    ts_gmt7_without_colon,
)


# Module-level device context (loaded once at import)
_AX_DEVICE_ID = ax_device_id()
_AX_FP = load_ax_fp()


def _ciam_headers(
    *,
    extra: dict | None = None,
    lowercase: bool = False,
    ts_override: str | None = None,
    include_signature: str | None = None,
    bearer_token: str | None = None,
) -> dict:
    """Build the standard CIAM header set.

    Set `lowercase=True` for `get_new_token` (server expects lowercase keys).
    Set `include_signature` to inject an `Ax-Api-Signature`.
    Set `bearer_token` to override the Basic auth with Bearer auth (auth-code flow).
    """
    now = datetime.now(timezone(timedelta(hours=7)))
    ts = ts_override or ts_gmt7_without_colon(now)
    request_id = str(uuid.uuid4())
    request_at = java_like_timestamp(now)

    h = CIAMHeader
    headers = {
        h.ACCEPT_ENCODING: "gzip, deflate, br",
        h.AX_DEVICE_ID: _AX_DEVICE_ID,
        h.AX_FINGERPRINT: _AX_FP,
        h.AX_REQUEST_AT: request_at,
        h.AX_REQUEST_DEVICE: CONFIG.device_manufacturer,
        h.AX_REQUEST_DEVICE_MODEL: CONFIG.device_model,
        h.AX_REQUEST_ID: request_id,
        h.AX_SUBSTYPE: CONFIG.default_substype,
        "Content-Type": "application/json",
        "Host": CONFIG.base_ciam_url.replace("https://", ""),
        "User-Agent": CONFIG.ua,
    }

    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    else:
        headers["Authorization"] = f"Basic {CONFIG.basic_auth}"

    if include_signature:
        headers[h.AX_API_SIGNATURE] = include_signature

    if lowercase:
        return {k.lower(): v for k, v in headers.items()}

    # _AX_REQUEST_AT gets overridden by ts for refresh-token flow
    headers[h.AX_REQUEST_AT] = ts
    return headers


def validate_contact(contact: str) -> bool:
    """XL MSISDN: starts with 628, length <= 14."""
    if not contact.startswith("628") or len(contact) > 14:
        print("Invalid number")
        return False
    return True


def get_otp(contact: str) -> str | None:
    """Send OTP via SMS; return subscriber_id on success."""
    if not validate_contact(contact):
        return None

    url = CONFIG.base_ciam_url + CIAMEndpoint.OTP
    params = {"contact": contact, "contactType": "SMS", "alternateContact": "false"}
    headers = _ciam_headers()

    print("Requesting OTP...")
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print("response body", response.text)
        json_body = json.loads(response.text)
        if "subscriber_id" not in json_body:
            print(json_body.get("error", "No error message in response"))
            raise ValueError("Subscriber ID not found in response")
        return json_body["subscriber_id"]
    except Exception as e:
        print(f"Error requesting OTP: {e}")
        return None


def extend_session(subscriber_id: str) -> str | None:
    """Extend session via DEVICEID flow; return exchange_code."""
    b64_subscriber_id = base64.b64encode(subscriber_id.encode()).decode()
    url = CONFIG.base_ciam_url + CIAMEndpoint.EXTEND_SESSION
    params = {"contact": b64_subscriber_id, "contactType": "DEVICEID"}
    headers = _ciam_headers()

    print("Extending session...")
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            print(f"Failed to extend session: {response.status_code} - {response.text}")
            return None
        return response.json().get("data", {}).get("exchange_code")
    except Exception as e:
        print(f"Error extending session: {e}")
        return None


def submit_otp(
    api_key: str,
    contact_type: str,
    contact: str,
    code: str,
) -> dict | None:
    """Exchange OTP (SMS) or exchange_code (DEVICEID) for OIDC tokens."""
    if contact_type == "SMS":
        if not validate_contact(contact):
            print("Invalid number")
            return None
        if not code or len(code) != 6:
            print("Invalid OTP code format")
            return None
        final_contact, final_code = contact, code
    elif contact_type == "DEVICEID":
        final_contact = base64.b64encode(contact.encode()).decode()
        final_code = code
    else:
        print("Unsupported contact type")
        return None

    now_gmt7 = datetime.now(timezone(timedelta(hours=7)))
    ts_for_sign = ts_gmt7_without_colon(now_gmt7)
    ts_header = ts_gmt7_without_colon(now_gmt7 - timedelta(minutes=5))
    signature = ax_api_signature(api_key, ts_for_sign, final_contact, code, contact_type)

    payload = (
        f"contactType={contact_type}&code={final_code}"
        f"&grant_type=password&contact={final_contact}&scope=openid"
    )

    headers = _ciam_headers(ts_override=ts_header, include_signature=signature)
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    url = CONFIG.base_ciam_url + CIAMEndpoint.TOKEN

    print("Submitting OTP...")
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        json_body = json.loads(response.text)
        if "error" in json_body:
            print(f"[Error submit_otp]: {json_body}")
            return None
        print("Login successful.")
        return json_body
    except requests.RequestException as e:
        print(f"[Error submit_otp]: {e}")
        return None


def get_new_token(api_key: str, refresh_token: str, subscriber_id: str) -> dict:
    """Refresh OIDC tokens; auto-extends session on `Session not active`."""
    url = CONFIG.base_ciam_url + CIAMEndpoint.TOKEN

    now = datetime.now(timezone(timedelta(hours=7)))
    ax_request_at = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0700"
    request_id = str(uuid.uuid4())

    headers = _ciam_headers(
        lowercase=True,
        ts_override=ax_request_at,
    )
    # Re-inject the per-call request id (lowercase path uses a fresh uuid)
    headers["ax-request-id"] = request_id
    headers["content-type"] = "application/x-www-form-urlencoded"

    data = {"grant_type": "refresh_token", "refresh_token": refresh_token}

    print("Refreshing token...")
    resp = requests.post(url, headers=headers, data=data, timeout=30)

    if resp.status_code == 400:
        if resp.json().get("error_description") != "Session not active":
            print(f"Failed to refresh token: {resp.status_code} - {resp.text}")
            return None

        if subscriber_id == "":
            raise ValueError("Subscriber ID is missing")

        exchange_code = extend_session(subscriber_id)
        if exchange_code is None:
            raise ValueError("Failed to get exchange code")

        extend_result = submit_otp(api_key, "DEVICEID", subscriber_id, exchange_code)
        if extend_result is None:
            if "Invalid refresh token" in resp.text:
                raise ValueError("Refresh token is invalid or expired. Please login again.")
            raise ValueError("Failed to submit OTP after extending session")
        return extend_result

    resp.raise_for_status()
    body = resp.json()

    if "id_token" not in body:
        raise ValueError("ID token not found in response")
    if "error" in body:
        raise ValueError(f"Error in response: {body['error']} - {body.get('error_description', '')}")
    return body


def get_auth_code(tokens: dict, pin: str, msisdn: str) -> str | None:
    """Generate authorization code for share-balance transactions."""
    url = CONFIG.base_ciam_url + CIAMEndpoint.AUTHORIZATION_TOKEN

    parsed = urlparse(CONFIG.base_ciam_url)
    host_header = parsed.netloc or CONFIG.base_ciam_url.replace("https://", "")

    now = datetime.now(timezone(timedelta(hours=7)))
    ax_request_at = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0700"
    request_id = str(uuid.uuid4())

    headers = {
        "Host": host_header,
        "Ax-Request-At": ax_request_at,
        "Ax-Device-Id": _AX_DEVICE_ID,
        "Ax-Request-Id": request_id,
        "Ax-Request-Device": CONFIG.device_manufacturer,
        "Ax-Request-Device-Model": CONFIG.device_model,
        "Ax-Fingerprint": _AX_FP,
        "Authorization": f"Bearer {tokens['access_token']}",
        "User-Agent": CONFIG.ua,
        "Ax-Substype": CONFIG.default_substype,
        "Content-Type": "application/json",
    }

    pin_b64 = base64.b64encode(pin.encode("utf-8")).decode("utf-8")
    body = {"pin": pin_b64, "transaction_type": "SHARE_BALANCE", "receiver_msisdn": msisdn}

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
    except requests.RequestException as e:
        print(f"[get_auth_code] Request error: {e}")
        return None

    if resp.status_code != 200:
        print(f"Failed to get auth code: {resp.status_code} - {resp.text}")
        return None

    try:
        data = resp.json()
    except ValueError:
        print(f"Invalid JSON response: {resp.text}")
        return None

    if not isinstance(data, dict):
        print(f"Unexpected response format: {data!r}")
        return None

    if data.get("status", "") != "Success":
        print(f"Error getting authorization code: {data.get('status')}")
        return None

    authorization_code = data.get("data", {}).get("authorization_code")
    if not authorization_code:
        print(f"Authorization code not found in response: {data}")
        return None
    return authorization_code
