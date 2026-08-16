"""Low-level HTTP client for the main backend (Engsel).

Handles encryption, signing, header construction, and decryption of responses.
Endpoint-specific callers live in dedicated modules (profile, packages, ...).
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import requests

from ahsiata.config import CONFIG
from ahsiata.constants import HttpHeader, LANG_EN
from ahsiata.api.encrypt import (
    decrypt_xdata,
    encryptsign_xdata,
    java_like_timestamp,
)


def send_api_request(
    api_key: str,
    path: str,
    payload_dict: dict,
    id_token: str,
    method: str = "POST",
):
    """Encrypt payload, sign request, POST to backend, decrypt response."""
    encrypted_payload = encryptsign_xdata(
        api_key=api_key,
        method=method,
        path=path,
        id_token=id_token,
        payload=payload_dict,
    )

    xtime = int(encrypted_payload["encrypted_body"]["xtime"])
    sig_time_sec = xtime // 1000
    now = datetime.now(timezone.utc).astimezone()

    body = encrypted_payload["encrypted_body"]
    x_sig = encrypted_payload["x_signature"]

    headers = {
        HttpHeader.HOST: CONFIG.base_api_url.replace("https://", ""),
        HttpHeader.CONTENT_TYPE: "application/json; charset=utf-8",
        HttpHeader.USER_AGENT: CONFIG.ua,
        HttpHeader.X_API_KEY: CONFIG.api_key,
        HttpHeader.AUTHORIZATION: f"Bearer {id_token}",
        HttpHeader.X_HV: CONFIG.x_hv,
        HttpHeader.X_SIGNATURE_TIME: str(sig_time_sec),
        HttpHeader.X_SIGNATURE: x_sig,
        HttpHeader.X_REQUEST_ID: str(uuid.uuid4()),
        HttpHeader.X_REQUEST_AT: java_like_timestamp(now),
        HttpHeader.X_VERSION_APP: CONFIG.app_version,
    }

    url = f"{CONFIG.base_api_url}/{path}"
    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)

    try:
        return decrypt_xdata(api_key, json.loads(resp.text))
    except Exception as e:
        print("[decrypt err]", e)
        return resp.text


def _common_payload(**overrides) -> dict:
    """Build a common backend payload; callers override specific keys."""
    base = {"is_enterprise": False, "lang": LANG_EN}
    base.update(overrides)
    return base


def get_balance(api_key: str, id_token: str) -> dict | None:
    """Fetch balance and credit expiry."""
    from ahsiata.constants import Endpoint
    payload = _common_payload()
    print("Fetching balance...")
    res = send_api_request(api_key, Endpoint.BALANCE, payload, id_token, "POST")
    if isinstance(res, dict) and "data" in res and "balance" in res["data"]:
        return res["data"]["balance"]
    print("Error getting balance:", res.get("error", "Unknown error") if isinstance(res, dict) else res)
    return None


def intercept_page(api_key: str, tokens: dict, option_code: str, is_enterprise: bool = False) -> None:
    from ahsiata.constants import Endpoint
    payload = _common_payload(
        is_enterprise=is_enterprise,
        package_option_code=option_code,
    )
    print("Fetching intercept page...")
    res = send_api_request(api_key, Endpoint.INTERCEPT_PAGE, payload, tokens["id_token"], "POST")
    if isinstance(res, dict) and "status" in res:
        print(f"Intercept status: {res['status']}")
    else:
        print("Intercept error")
