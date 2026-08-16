"""Settlement via QRIS."""
from __future__ import annotations

import base64

import qrcode

from ahsiata.api.client import intercept_page, send_api_request
from ahsiata.api.purchase.base import (
    fetch_payment_token,
    join_item_codes,
    make_payment_signature,
    post_signed_payload,
    resolve_amount,
)
from ahsiata.constants import Endpoint, LANG_EN, PaymentMethod
from ahsiata.type_dict import PaymentItem


QRIS_VIEWER_URL = "https://ki-ar-kod.netlify.app/?data={qris_b64}"


def settlement_qris(
    api_key: str,
    tokens: dict,
    items: list[PaymentItem],
    payment_for: str,
    ask_overwrite: bool,
    overwrite_amount: int = -1,
    token_confirmation_idx: int = 0,
    amount_idx: int = -1,
    topup_number: str = "",
    stage_token: str = "",
) -> str | None:
    """Returns the QRIS `transaction_code` (used by `get_qris_code`)."""
    if overwrite_amount == -1 and not ask_overwrite:
        print("Either ask_overwrite must be True or overwrite_amount must be set.")
        return None

    token_confirmation = items[token_confirmation_idx]["token_confirmation"]
    payment_targets = join_item_codes(items)
    amount_int = resolve_amount(
        items, overwrite_amount=overwrite_amount, ask_overwrite=ask_overwrite, amount_idx=amount_idx,
    )

    intercept_page(api_key, tokens, items[0]["item_code"], False)

    fetched = fetch_payment_token(api_key, tokens, items[token_confirmation_idx]["item_code"], token_confirmation)
    if fetched is None:
        return None
    token_payment, ts_to_sign = fetched

    path = Endpoint.SETTLEMENT_QRIS
    payload = {
        "akrab": {"akrab_members": [], "akrab_parent_alias": "", "members": []},
        "can_trigger_rating": False,
        "total_discount": 0,
        "coupon": "",
        "payment_for": payment_for,
        "topup_number": topup_number,
        "stage_token": stage_token,
        "is_enterprise": False,
        "autobuy": {
            "is_using_autobuy": False,
            "activated_autobuy_code": "",
            "autobuy_threshold_setting": {"label": "", "type": "", "value": 0},
        },
        "access_token": tokens["access_token"],
        "is_myxl_wallet": False,
        "additional_data": {
            "original_price": items[0]["item_price"],
            "is_spend_limit_temporary": False,
            "migration_type": "",
            "spend_limit_amount": 0,
            "is_spend_limit": False,
            "tax": 0,
            "benefit_type": "",
            "quota_bonus": 0,
            "cashtag": "",
            "is_family_plan": False,
            "combo_details": [],
            "is_switch_plan": False,
            "discount_recurring": 0,
            "has_bonus": False,
            "discount_promo": 0,
        },
        "total_amount": amount_int,
        "total_fee": 0,
        "is_use_point": False,
        "lang": LANG_EN,
        "items": items,
        "verification_token": token_payment,
        "payment_method": PaymentMethod.QRIS,
        "timestamp": ts_to_sign,
    }

    x_sig = make_payment_signature(
        tokens=tokens,
        ts_to_sign=ts_to_sign,
        payment_targets=payment_targets,
        token_payment=token_payment,
        payment_method=PaymentMethod.QRIS,
        payment_for=payment_for,
        path=path,
    )

    print("Sending settlement request...")
    res = post_signed_payload(api_key=api_key, tokens=tokens, path=path, payload=payload, signature=x_sig)

    if not isinstance(res, dict):
        return res
    if res.get("status") != "SUCCESS":
        print("Failed to initiate settlement.")
        print(f"Error: {res}")
        return None
    return res["data"]["transaction_code"]


def get_qris_code(api_key: str, tokens: dict, transaction_id: str) -> str | None:
    payload = {
        "transaction_id": transaction_id,
        "is_enterprise": False,
        "lang": LANG_EN,
        "status": "",
    }
    res = send_api_request(api_key, Endpoint.PENDING_DETAIL, payload, tokens["id_token"], "POST")
    if not isinstance(res, dict) or res.get("status") != "SUCCESS":
        print("Failed to fetch QRIS code.")
        print(f"Error: {res}")
        return None
    return res["data"]["qr_code"]


def show_qris_payment(
    api_key: str,
    tokens: dict,
    items: list[PaymentItem],
    payment_for: str,
    ask_overwrite: bool,
    overwrite_amount: int = -1,
    token_confirmation_idx: int = 0,
    amount_idx: int = -1,
    topup_number: str = "",
    stage_token: str = "",
) -> str | None:
    transaction_id = settlement_qris(
        api_key, tokens, items, payment_for, ask_overwrite, overwrite_amount,
        token_confirmation_idx, amount_idx, topup_number, stage_token,
    )
    if not transaction_id:
        print("Failed to create QRIS transaction.")
        return None

    print("Fetching QRIS code...")
    qris_code = get_qris_code(api_key, tokens, transaction_id)
    if not qris_code:
        print("Failed to get QRIS code.")
        return None
    print(f"QRIS data:\n{qris_code}")

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(qris_code)
    qr.make(fit=True)
    qr.print_ascii(invert=True)

    qris_b64 = base64.urlsafe_b64encode(qris_code.encode()).decode()
    print(f"Atau buka link berikut untuk melihat QRIS:\n{QRIS_VIEWER_URL.format(qris_b64=qris_b64)}")
    return qris_b64
