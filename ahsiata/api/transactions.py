"""Transaction history endpoint."""
from __future__ import annotations

from ahsiata.constants import Endpoint, LANG_EN
from ahsiata.api.client import send_api_request


def get_transaction_history(api_key: str, tokens: dict) -> dict:
    payload = {"is_enterprise": False, "lang": LANG_EN}
    print("Mengambil riwayat transaksi…")
    res = send_api_request(api_key, Endpoint.TRANSACTION_HISTORY, payload, tokens["id_token"], "POST")
    return res.get("data") if isinstance(res, dict) else None
