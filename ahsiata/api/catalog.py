"""Store catalog endpoints: segments, family list, packages, redeemables."""
from __future__ import annotations

from ahsiata.ui.style import fail
from ahsiata.constants import Endpoint, LANG_EN
from ahsiata.api.client import send_api_request


def get_segments(api_key: str, tokens: dict, is_enterprise: bool = False) -> dict | None:
    payload = {"is_enterprise": is_enterprise, "lang": LANG_EN}
    res = send_api_request(api_key, Endpoint.STORE_SEGMENTS, payload, tokens["id_token"], "POST")
    if not isinstance(res, dict) or res.get("status") != "SUCCESS":
        print(fail(f"Gagal mengambil segments: {res}"))
        return None
    return res


def get_family_list(
    api_key: str,
    tokens: dict,
    subs_type: str = "PREPAID",
    is_enterprise: bool = False,
) -> dict | None:
    payload = {"is_enterprise": is_enterprise, "subs_type": subs_type, "lang": LANG_EN}
    res = send_api_request(api_key, Endpoint.FAMILY_LIST_SEARCH, payload, tokens["id_token"], "POST")
    if not isinstance(res, dict) or res.get("status") != "SUCCESS":
        print(fail(f"Gagal mengambil family list: {res}"))
        return None
    return res


def get_store_packages(
    api_key: str,
    tokens: dict,
    subs_type: str = "PREPAID",
    is_enterprise: bool = False,
) -> dict | None:
    payload = {
        "is_enterprise": is_enterprise,
        "filters": [
            {"unit": "THOUSAND", "id": "FIL_SEL_P", "type": "PRICE", "items": []},
            {"unit": "GB", "id": "FIL_SEL_MQ", "type": "DATA_TYPE", "items": []},
            {"unit": "PACKAGE_NAME", "id": "FIL_PKG_N", "type": "PACKAGE_NAME",
             "items": [{"id": "", "label": ""}]},
            {"unit": "DAY", "id": "FIL_SEL_V", "type": "VALIDITY", "items": []},
        ],
        "substype": subs_type,
        "text_search": "",
        "lang": LANG_EN,
    }
    res = send_api_request(api_key, Endpoint.STORE_PACKAGES_SEARCH, payload, tokens["id_token"], "POST")
    if not isinstance(res, dict) or res.get("status") != "SUCCESS":
        print(fail(f"Gagal mengambil paket toko: {res}"))
        return None
    return res


def get_redeemables(api_key: str, tokens: dict, is_enterprise: bool = False) -> dict | None:
    payload = {"is_enterprise": is_enterprise, "lang": LANG_EN}
    res = send_api_request(api_key, Endpoint.REDEEMABLES, payload, tokens["id_token"], "POST")
    if not isinstance(res, dict) or res.get("status") != "SUCCESS":
        print(fail(f"Gagal mengambil redeemable: {res}"))
        return None
    return res
