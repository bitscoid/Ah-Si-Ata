"""Redeem flows: bounty (voucher), loyalty (points), bounty-allotment (gift)."""
from __future__ import annotations

from datetime import datetime

from ahsiata.api.encrypt import build_encrypted_field
from ahsiata.api.purchase.base import (
    make_bounty_allotment_signature,
    make_bounty_signature,
    make_loyalty_signature,
    post_signed_payload,
)
from ahsiata.constants import Endpoint, LANG_EN, PaymentFor, PaymentMethod


def settlement_bounty(
    api_key: str,
    tokens: dict,
    token_confirmation: str,
    ts_to_sign: int,
    payment_target: str,
    price: int,
    item_name: str = "",
):
    """Redeem a voucher/bounty via BALANCE method."""
    path = Endpoint.BOUNTIES_EXCHANGE
    payload = {
        "total_discount": 0,
        "is_enterprise": False,
        "payment_token": "",
        "token_payment": "",
        "activated_autobuy_code": "",
        "cc_payment_type": "",
        "is_myxl_wallet": False,
        "pin": "",
        "ewallet_promo_id": "",
        "members": [],
        "total_fee": 0,
        "fingerprint": "",
        "autobuy_threshold_setting": {"label": "", "type": "", "value": 0},
        "is_use_point": False,
        "lang": LANG_EN,
        "payment_method": PaymentMethod.BALANCE,
        "timestamp": ts_to_sign,
        "points_gained": 0,
        "can_trigger_rating": False,
        "akrab_members": [],
        "akrab_parent_alias": "",
        "referral_unique_code": "",
        "coupon": "",
        "payment_for": PaymentFor.REDEEM_VOUCHER,
        "with_upsell": False,
        "topup_number": "",
        "stage_token": "",
        "authentication_id": "",
        "encrypted_payment_token": build_encrypted_field(urlsafe_b64=True),
        "token": "",
        "token_confirmation": token_confirmation,
        "access_token": tokens["access_token"],
        "wallet_number": "",
        "encrypted_authentication_id": build_encrypted_field(urlsafe_b64=True),
        "additional_data": {
            "original_price": 0,
            "is_spend_limit_temporary": False,
            "migration_type": "",
            "akrab_m2m_group_id": "",
            "spend_limit_amount": 0,
            "is_spend_limit": False,
            "mission_id": "",
            "tax": 0,
            "benefit_type": "",
            "quota_bonus": 0,
            "cashtag": "",
            "is_family_plan": False,
            "combo_details": [],
            "is_switch_plan": False,
            "discount_recurring": 0,
            "is_akrab_m2m": False,
            "balance_type": "",
            "has_bonus": False,
            "discount_promo": 0,
        },
        "total_amount": 0,
        "is_using_autobuy": False,
        "items": [{
            "item_code": payment_target,
            "product_type": "",
            "item_price": price,
            "item_name": item_name,
            "tax": 0,
        }],
    }

    x_sig = make_bounty_signature(
        tokens=tokens,
        ts_to_sign=ts_to_sign,
        item_code=payment_target,
        token_payment=token_confirmation,
    )

    print("Sending bounty request...")
    res = post_signed_payload(api_key=api_key, tokens=tokens, path=path, payload=payload, signature=x_sig)
    if isinstance(res, dict):
        if res.get("status") != "SUCCESS":
            print("Failed to claim bounty.")
            print(f"Error: {res}")
            return None
        print(res)
    return res


def settlement_loyalty(
    api_key: str,
    tokens: dict,
    token_confirmation: str,
    ts_to_sign: int,
    payment_target: str,
    price: int,
):
    """Pay with loyalty points."""
    path = Endpoint.LOYALTIES_EXCHANGE
    payload = {
        "item_code": payment_target,
        "amount": 0,
        "partner": "",
        "is_enterprise": False,
        "item_name": "",
        "lang": LANG_EN,
        "points": price,
        "timestamp": ts_to_sign,
        "token_confirmation": token_confirmation,
    }

    x_sig = make_loyalty_signature(
        ts_to_sign=ts_to_sign,
        item_code=payment_target,
        token_confirmation=token_confirmation,
        path=path,
    )

    print("Sending loyalty request...")
    res = post_signed_payload(api_key=api_key, tokens=tokens, path=path, payload=payload, signature=x_sig)
    if isinstance(res, dict):
        if res.get("status") != "SUCCESS":
            print("Failed purchase.")
            print(f"Error: {res}")
            return None
        print(res)
    return res


def bounty_allotment(
    api_key: str,
    tokens: dict,
    ts_to_sign: int,
    destination_msisdn: str,
    item_name: str,
    item_code: str,
    token_confirmation: str,
):
    """Send a bounty/gift to another MSISDN."""
    path = Endpoint.BOUNTIES_ALLOTMENT
    payload = {
        "destination_msisdn": destination_msisdn,
        "item_code": item_code,
        "is_enterprise": False,
        "item_name": item_name,
        "lang": LANG_EN,
        "timestamp": ts_to_sign,
        "token_confirmation": token_confirmation,
    }

    x_sig = make_bounty_allotment_signature(
        ts_to_sign=ts_to_sign,
        item_code=item_code,
        token_confirmation=token_confirmation,
        destination_msisdn=destination_msisdn,
        path=path,
    )

    print("Sending bounty allotment request...")
    res = post_signed_payload(api_key=api_key, tokens=tokens, path=path, payload=payload, signature=x_sig)
    if isinstance(res, dict):
        if res.get("status") != "SUCCESS":
            print("Failed to claim bounty.")
            print(f"Error: {res}")
            return None
        print(res)
    return res
