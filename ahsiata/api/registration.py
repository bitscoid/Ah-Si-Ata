"""Registration endpoints (Dukcapil)."""
from __future__ import annotations

from ahsiata.constants import Endpoint, LANG_EN
from ahsiata.api.client import send_api_request


def dukcapil(api_key: str, msisdn: str, kk: str, nik: str) -> dict:
    payload = {"msisdn": msisdn, "kk": kk, "nik": nik, "lang": LANG_EN}
    return send_api_request(api_key, Endpoint.DUKCAPIL, payload, "", "POST")