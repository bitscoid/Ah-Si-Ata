"""Package catalog and detail endpoints."""
from __future__ import annotations

import json

from ahsiata.constants import Endpoint, LANG_EN, MigrationType
from ahsiata.api.client import send_api_request


def get_family(
    api_key: str,
    tokens: dict,
    family_code: str,
    is_enterprise: bool | None = None,
    migration_type: str | None = None,
) -> dict | None:
    """Brute-force (is_enterprise × migration_type) until a non-empty family is returned."""
    print("Mengambil family paket...")

    enterprise_choices = [False, True] if is_enterprise is None else [is_enterprise]
    migration_choices = list(MigrationType.ALL) if migration_type is None else [migration_type]

    id_token = tokens.get("id_token")
    family_data: dict | None = None

    for mt in migration_choices:
        if family_data is not None:
            break
        for ie in enterprise_choices:
            if family_data is not None:
                break
            print(f"Mencoba is_enterprise={ie}, migration_type={mt}.")
            payload = {
                "is_show_tagging_tab": True,
                "is_dedicated_event": True,
                "is_transaction_routine": False,
                "migration_type": mt,
                "package_family_code": family_code,
                "is_autobuy": False,
                "is_enterprise": ie,
                "is_pdlp": True,
                "referral_code": "",
                "is_migration": False,
                "lang": LANG_EN,
            }
            res = send_api_request(api_key, Endpoint.FAMILY_LIST, payload, id_token, "POST")
            if not isinstance(res, dict) or res.get("status") != "SUCCESS":
                continue
            family_name = res["data"]["package_family"].get("name", "")
            if family_name:
                family_data = res["data"]
                print(f"Berhasil dengan is_enterprise={ie}, migration_type={mt}. Nama family: {family_name}")

    if family_data is None:
        print(f"Gagal mendapatkan data family yang valid untuk {family_code}")
        return None
    return family_data


def get_package(
    api_key: str,
    tokens: dict,
    package_option_code: str,
    package_family_code: str = "",
    package_variant_code: str = "",
) -> dict | None:
    payload = {
        "is_transaction_routine": False,
        "migration_type": "NONE",
        "package_family_code": package_family_code,
        "family_role_hub": "",
        "is_autobuy": False,
        "is_enterprise": False,
        "is_shareable": False,
        "is_migration": False,
        "lang": LANG_EN,
        "package_option_code": package_option_code,
        "is_upsell_pdp": False,
        "package_variant_code": package_variant_code,
    }
    print("Mengambil paket...")
    res = send_api_request(api_key, Endpoint.PACKAGE_DETAIL, payload, tokens["id_token"], "POST")
    if not isinstance(res, dict) or "data" not in res:
        print(json.dumps(res, indent=2))
        print("Gagal mengambil paket:", res.get("error", "Error tidak diketahui") if isinstance(res, dict) else res)
        return None
    return res["data"]


def get_addons(api_key: str, tokens: dict, package_option_code: str) -> dict | None:
    payload = {"is_enterprise": False, "lang": LANG_EN, "package_option_code": package_option_code}
    print("Mengambil addon...")
    res = send_api_request(api_key, Endpoint.ADDONS, payload, tokens["id_token"], "POST")
    if not isinstance(res, dict) or "data" not in res:
        print("Gagal mengambil addon:", res.get("error", "Error tidak diketahui") if isinstance(res, dict) else res)
        return None
    return res["data"]


def get_package_details(
    api_key: str,
    tokens: dict,
    family_code: str,
    variant_code: str,
    option_order: int,
    is_enterprise: bool | None = None,
    migration_type: str | None = None,
) -> dict | None:
    """Resolve family → variant → option → package detail in one call."""
    family_data = get_family(api_key, tokens, family_code, is_enterprise, migration_type)
    if not family_data:
        print(f"Gagal mengambil data family untuk {family_code}.")
        return None

    option_code: str | None = None
    for variant in family_data["package_variants"]:
        if variant["package_variant_code"] != variant_code:
            continue
        for option in variant["package_options"]:
            if option["order"] == option_order:
                option_code = option["package_option_code"]
                break
        if option_code:
            break

    if option_code is None:
        print("Gagal menemukan opsi paket yang sesuai.")
        return None

    package_details_data = get_package(api_key, tokens, option_code)
    if not package_details_data:
        print("Gagal mengambil detail paket.")
        return None
    return package_details_data


def unsubscribe(
    api_key: str,
    tokens: dict,
    quota_code: str,
    product_domain: str,
    product_subscription_type: str,
) -> bool:
    payload = {
        "product_subscription_type": product_subscription_type,
        "quota_code": quota_code,
        "product_domain": product_domain,
        "is_enterprise": False,
        "unsubscribe_reason_code": "",
        "lang": LANG_EN,
        "family_member_id": "",
    }
    try:
        res = send_api_request(api_key, Endpoint.UNSUBSCRIBE, payload, tokens["id_token"], "POST")
        print(json.dumps(res, indent=4))
        return bool(res and isinstance(res, dict) and res.get("code") == "000")
    except Exception:
        return False
