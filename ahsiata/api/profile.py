"""Profile, balance, and tiering endpoints."""
from __future__ import annotations

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
    print("⏳ Mengambil profil…")
    res = send_api_request(api_key, Endpoint.PROFILE, payload, id_token, "POST")
    if isinstance(res, dict):
        return res.get("data")
    return None


def get_tiering_info(api_key: str, tokens: dict) -> dict:
    """Fetch loyalty points and tier."""
    payload = {"is_enterprise": False, "lang": LANG_EN}
    print("⏳ Mengambil info tiering…")
    res = send_api_request(api_key, Endpoint.TIERING_INFO, payload, tokens["id_token"], "POST")
    if isinstance(res, dict):
        return res.get("data", {})
    return {}