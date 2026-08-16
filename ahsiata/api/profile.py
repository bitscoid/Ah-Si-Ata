"""Profile, balance, tiering, and dashboard-segments endpoints."""
from __future__ import annotations

import json

from ahsiata.config import CONFIG
from ahsiata.constants import Endpoint, LANG_EN
from ahsiata.api.client import send_api_request


def get_profile(api_key: str, access_token: str, id_token: str) -> dict:
    """Fetch user profile (subscriber_id, subscription_type)."""
    payload = {
        "access_token": access_token,
        "app_version": CONFIG.app_version,
        "is_enterprise": False,
        "lang": LANG_EN,
    }
    print("Fetching profile...")
    res = send_api_request(api_key, Endpoint.PROFILE, payload, id_token, "POST")
    if isinstance(res, dict):
        return res.get("data")
    return None


def get_tiering_info(api_key: str, tokens: dict) -> dict:
    """Fetch loyalty points and tier."""
    payload = {"is_enterprise": False, "lang": LANG_EN}
    print("Fetching tiering info...")
    res = send_api_request(api_key, Endpoint.TIERING_INFO, payload, tokens["id_token"], "POST")
    if isinstance(res, dict):
        return res.get("data", {})
    return {}


def login_info(api_key: str, tokens: dict, is_enterprise: bool = False) -> dict | None:
    payload = {
        "access_token": tokens["access_token"],
        "is_enterprise": is_enterprise,
        "lang": LANG_EN,
    }
    res = send_api_request(api_key, Endpoint.LOGIN, payload, tokens["id_token"], "POST")
    if "data" not in res:
        print(json.dumps(res, indent=2))
        print("Error getting package:", res.get("error", "Unknown error"))
        return None
    return res["data"]


def dashboard_segments(api_key: str, tokens: dict) -> dict:
    payload = {"access_token": tokens["access_token"]}
    return send_api_request(api_key, Endpoint.DASHBOARD_SEGMENTS, payload, tokens["id_token"], "POST")
