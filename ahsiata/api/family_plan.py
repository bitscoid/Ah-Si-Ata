"""Family Plan (Akrab Organizer) API."""
from __future__ import annotations

from ahsiata.constants import Endpoint, LANG_EN
from ahsiata.api.client import send_api_request


def get_family_data(api_key: str, tokens: dict) -> dict:
    payload = {"group_id": 0, "is_enterprise": False, "lang": LANG_EN}
    print("Fetching family data...")
    return send_api_request(api_key, Endpoint.FAMILY_PLAN_MEMBER_INFO, payload, tokens["id_token"], "POST")


def validate_msisdn(api_key: str, tokens: dict, msisdn: str) -> dict:
    payload = {
        "with_bizon": True,
        "with_family_plan": True,
        "is_enterprise": False,
        "with_optimus": True,
        "lang": LANG_EN,
        "msisdn": msisdn,
        "with_regist_status": True,
        "with_enterprise": True,
    }
    print(f"Validating msisdn {msisdn}...")
    return send_api_request(api_key, Endpoint.FAMILY_PLAN_VALIDATE_MSISDN, payload, tokens["id_token"], "POST")


def change_member(
    api_key: str,
    tokens: dict,
    parent_alias: str,
    alias: str,
    slot_id: int,
    family_member_id: str,
    new_msisdn: str,
) -> dict:
    payload = {
        "parent_alias": parent_alias,
        "is_enterprise": False,
        "slot_id": slot_id,
        "alias": alias,
        "lang": LANG_EN,
        "msisdn": new_msisdn,
        "family_member_id": family_member_id,
    }
    print(f"Assigning slot {slot_id} to {new_msisdn}...")
    return send_api_request(api_key, Endpoint.FAMILY_PLAN_CHANGE_MEMBER, payload, tokens["id_token"], "POST")


def remove_member(api_key: str, tokens: dict, family_member_id: str) -> dict:
    payload = {
        "is_enterprise": False,
        "family_member_id": family_member_id,
        "lang": LANG_EN,
    }
    print(f"Removing family member {family_member_id}...")
    return send_api_request(api_key, Endpoint.FAMILY_PLAN_REMOVE_MEMBER, payload, tokens["id_token"], "POST")


def set_quota_limit(
    api_key: str,
    tokens: dict,
    original_allocation: int,
    new_allocation: int,
    family_member_id: str,
) -> dict:
    payload = {
        "is_enterprise": False,
        "member_allocations": [{
            "new_text_allocation": 0,
            "original_text_allocation": 0,
            "original_voice_allocation": 0,
            "original_allocation": original_allocation,
            "new_voice_allocation": 0,
            "message": "",
            "new_allocation": new_allocation,
            "family_member_id": family_member_id,
            "status": "",
        }],
        "lang": LANG_EN,
    }
    print(f"Setting quota limit for family member {family_member_id} to {new_allocation} bytes...")
    return send_api_request(api_key, Endpoint.FAMILY_PLAN_ALLOCATE_QUOTA, payload, tokens["id_token"], "POST")
