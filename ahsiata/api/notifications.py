"""Notification and transaction-history endpoints."""
from __future__ import annotations

from ahsiata.constants import Endpoint, LANG_EN
from ahsiata.api.client import send_api_request
from ahsiata.ui.style import fail


def get_notifications(api_key: str, tokens: dict):
    payload = {"is_enterprise": False, "lang": LANG_EN}
    res = send_api_request(api_key, Endpoint.NOTIFICATIONS, payload, tokens["id_token"], "POST")
    if isinstance(res, dict) and res.get("status") != "SUCCESS":
        print(fail(f"Gagal mengambil notifikasi: {res.get('error', 'Error tidak diketahui')}"))
        return None
    return res


def get_notification_detail(api_key: str, tokens: dict, notification_id: str):
    payload = {
        "is_enterprise": False,
        "lang": LANG_EN,
        "notification_id": notification_id,
    }
    res = send_api_request(api_key, Endpoint.NOTIFICATION_DETAIL, payload, tokens["id_token"], "POST")
    if isinstance(res, dict) and res.get("status") != "SUCCESS":
        print(fail(f"Gagal mengambil detail notifikasi: {res.get('error', 'Error tidak diketahui')}"))
        return None
    return res
