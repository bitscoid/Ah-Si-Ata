"""Low-level HTTP client for the main backend (Engsel).

Handles encryption, signing, header construction, and decryption of responses.
Endpoint-specific callers live in dedicated modules (profile, packages, …).
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ahsiata.config import CONFIG
from ahsiata.constants import HttpHeader, LANG_EN
from ahsiata.api.encrypt import (
    decrypt_xdata,
    encryptsign_xdata,
    java_like_timestamp,
)

# Shared session: connection reuse + bounded retry on transient HTTP failures.
_SESSION = requests.Session()
_SESSION.mount(
    "https://",
    HTTPAdapter(max_retries=Retry(total=2, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504))),
)


def build_headers(path: str, id_token: str, xtime_ms: int, x_signature: str) -> dict:
    """Standard request headers shared by all main-backend calls."""
    sig_time_sec = xtime_ms // 1000
    now = datetime.now(timezone.utc).astimezone()
    return {
        HttpHeader.HOST: CONFIG.base_api_url.replace("https://", ""),
        HttpHeader.CONTENT_TYPE: "application/json; charset=utf-8",
        HttpHeader.USER_AGENT: CONFIG.ua,
        HttpHeader.X_API_KEY: CONFIG.api_key,
        HttpHeader.AUTHORIZATION: f"Bearer {id_token}",
        HttpHeader.X_HV: CONFIG.x_hv,
        HttpHeader.X_SIGNATURE_TIME: str(sig_time_sec),
        HttpHeader.X_SIGNATURE: x_signature,
        HttpHeader.X_REQUEST_ID: str(uuid.uuid4()),
        HttpHeader.X_REQUEST_AT: java_like_timestamp(now),
        HttpHeader.X_VERSION_APP: CONFIG.app_version,
    }


def post_encrypted(
    api_key: str,
    path: str,
    id_token: str,
    encrypted_payload: dict,
    x_signature: str | None = None,
) -> dict | str:
    """POST an already-encrypted body and return the decrypted response.

    `x_signature` overrides the payload's own signature (payment flows sign
    differently from the base `xdata` signature).
    """
    body = encrypted_payload["encrypted_body"]
    sig = x_signature or encrypted_payload["x_signature"]
    headers = build_headers(path, id_token, int(body["xtime"]), sig)
    url = f"{CONFIG.base_api_url}/{path}"
    resp = _SESSION.post(url, headers=headers, data=json.dumps(body), timeout=30)

    try:
        return decrypt_xdata(api_key, json.loads(resp.text))
    except Exception as e:
        print("[err dekripsi]", e)
        return resp.text


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
    return post_encrypted(api_key, path, id_token, encrypted_payload)


def _common_payload(**overrides) -> dict:
    """Build a common backend payload; callers override specific keys."""
    base = {"is_enterprise": False, "lang": LANG_EN}
    base.update(overrides)
    return base


def get_balance(api_key: str, id_token: str) -> dict | None:
    """Fetch balance and credit expiry."""
    from ahsiata.constants import Endpoint
    payload = _common_payload()
    print("Mengambil saldo…")
    res = send_api_request(api_key, Endpoint.BALANCE, payload, id_token, "POST")
    if isinstance(res, dict) and "data" in res and "balance" in res["data"]:
        return res["data"]["balance"]
    print("Gagal mengambil saldo:", res.get("error", "Error tidak diketahui") if isinstance(res, dict) else res)
    return None


def intercept_page(api_key: str, tokens: dict, option_code: str, is_enterprise: bool = False) -> None:
    from ahsiata.constants import Endpoint
    payload = _common_payload(
        is_enterprise=is_enterprise,
        package_option_code=option_code,
    )
    print("Mengambil halaman intercept…")
    res = send_api_request(api_key, Endpoint.INTERCEPT_PAGE, payload, tokens["id_token"], "POST")
    if isinstance(res, dict) and "status" in res:
        print(f"Status intercept: {res['status']}")
    else:
        print("Gagal intercept")