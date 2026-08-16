"""Circle (Family Hub) API."""
from __future__ import annotations

from ahsiata.constants import Endpoint, LANG_EN
from ahsiata.api.client import send_api_request
from ahsiata.api.encrypt import encrypt_circle_msisdn


def get_group_data(api_key: str, tokens: dict) -> dict:
    payload = {"is_enterprise": False, "lang": LANG_EN}
    print("Fetching group detail...")
    return send_api_request(api_key, Endpoint.CIRCLE_GROUP_STATUS, payload, tokens["id_token"], "POST")


def get_group_members(api_key: str, tokens: dict, group_id: str) -> dict:
    payload = {"group_id": group_id, "is_enterprise": False, "lang": LANG_EN}
    print("Fetching group members...")
    return send_api_request(api_key, Endpoint.CIRCLE_MEMBERS_INFO, payload, tokens["id_token"], "POST")


def validate_circle_member(api_key: str, tokens: dict, msisdn: str) -> dict:
    payload = {
        "msisdn": encrypt_circle_msisdn(api_key, msisdn),
        "is_enterprise": False,
        "lang": LANG_EN,
    }
    print(f"Validating {msisdn}...")
    return send_api_request(api_key, Endpoint.CIRCLE_MEMBERS_VALIDATE, payload, tokens["id_token"], "POST")


def invite_circle_member(
    api_key: str,
    tokens: dict,
    msisdn: str,
    name: str,
    group_id: str,
    member_id_parent: str,
) -> dict:
    payload = {
        "access_token": tokens["access_token"],
        "group_id": group_id,
        "is_enterprise": False,
        "members": [{"msisdn": encrypt_circle_msisdn(api_key, msisdn), "name": name}],
        "lang": LANG_EN,
        "member_id_parent": member_id_parent,
    }
    print(f"Inviting {msisdn}...")
    return send_api_request(api_key, Endpoint.CIRCLE_MEMBERS_INVITE, payload, tokens["id_token"], "POST")


def remove_circle_member(
    api_key: str,
    tokens: dict,
    member_id: str,
    group_id: str,
    member_id_parent: str,
    is_last_member: bool = False,
) -> dict:
    payload = {
        "member_id": member_id,
        "group_id": group_id,
        "is_enterprise": False,
        "is_last_member": is_last_member,
        "lang": LANG_EN,
        "member_id_parent": member_id_parent,
    }
    print(f"Removing member {member_id} from Circle...")
    return send_api_request(api_key, Endpoint.CIRCLE_MEMBERS_REMOVE, payload, tokens["id_token"], "POST")


def accept_circle_invitation(api_key: str, tokens: dict, group_id: str, member_id: str) -> dict:
    payload = {
        "access_token": tokens["access_token"],
        "group_id": group_id,
        "member_id": member_id,
        "is_enterprise": False,
        "lang": LANG_EN,
    }
    print(f"Accepting invitation to Circle {group_id}...")
    return send_api_request(api_key, Endpoint.CIRCLE_ACCEPT_INVITATION, payload, tokens["id_token"], "POST")


def create_circle(
    api_key: str,
    tokens: dict,
    parent_name: str,
    group_name: str,
    member_msisdn: str,
    member_name: str,
) -> dict:
    payload = {
        "access_token": tokens["access_token"],
        "parent_name": parent_name,
        "group_name": group_name,
        "is_enterprise": False,
        "members": [{"msisdn": encrypt_circle_msisdn(api_key, member_msisdn), "name": member_name}],
        "lang": LANG_EN,
    }
    print(f"Creating Circle with member {member_msisdn}...")
    return send_api_request(api_key, Endpoint.CIRCLE_GROUP_CREATE, payload, tokens["id_token"], "POST")


def spending_tracker(api_key: str, tokens: dict, parent_subs_id: str, family_id: str) -> dict:
    payload = {
        "is_enterprise": False,
        "parent_subs_id": parent_subs_id,
        "family_id": family_id,
        "lang": LANG_EN,
    }
    return send_api_request(api_key, Endpoint.CIRCLE_SPENDING_TRACKER, payload, tokens["id_token"], "POST")


def get_bonus_data(api_key: str, tokens: dict, parent_subs_id: str, family_id: str) -> dict:
    payload = {
        "is_enterprise": False,
        "parent_subs_id": parent_subs_id,
        "family_id": family_id,
        "lang": LANG_EN,
    }
    return send_api_request(api_key, Endpoint.CIRCLE_BONUS_LIST, payload, tokens["id_token"], "POST")
