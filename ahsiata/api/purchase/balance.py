"""Settlement via PULSA / prepaid balance."""
from __future__ import annotations

from ahsiata.ui.style import fail, info, ok

import time

from ahsiata.api.client import intercept_page
from ahsiata.api.encrypt import build_encrypted_field
from ahsiata.api.purchase.base import (
    fetch_payment_token,
    join_item_codes,
    make_payment_signature,
    post_signed_payload,
    resolve_amount,
)
from ahsiata.constants import Endpoint, LANG_EN, PaymentMethod
from ahsiata.type_dict import PaymentItem


def append_decoy_item(items: list[PaymentItem], decoy_detail: dict) -> None:
    """Add a decoy package to the payment items list."""
    items.append(PaymentItem(
        item_code=decoy_detail["package_option"]["package_option_code"],
        product_type="",
        item_price=decoy_detail["package_option"]["price"],
        item_name=decoy_detail["package_option"]["name"],
        tax=0,
        token_confirmation=decoy_detail["token_confirmation"],
    ))


def settle_with_decoy(
    api_key: str,
    tokens: dict,
    items: list[PaymentItem],
    payment_for: str,
    decoy_detail: dict | None,
    token_confirmation_idx: int = 0,
) -> dict | str | None:
    """Settle `items` with an optional decoy appended; retry once with the
    server-corrected total when the API rejects `Bizz-err.Amount.Total`."""
    if decoy_detail is None:
        return settlement_balance(
            api_key, tokens, items, payment_for, True,
            token_confirmation_idx=token_confirmation_idx,
        )

    append_decoy_item(items, decoy_detail)
    total = items[0]["item_price"] + decoy_detail["package_option"]["price"]
    res = settlement_balance(
        api_key, tokens, items, payment_for, False,
        overwrite_amount=total, token_confirmation_idx=token_confirmation_idx,
    )
    if isinstance(res, dict) and res.get("status") != "SUCCESS":
        error_msg = res.get("message", "")
        if "Bizz-err.Amount.Total" in error_msg:
            try:
                valid_amount = int(error_msg.split("=")[1].strip())
            except (IndexError, ValueError):
                return res
            print(info(f"Total jumlah disesuaikan menjadi: {valid_amount}"))
            return settlement_balance(
                api_key, tokens, items, payment_for, False,
                overwrite_amount=valid_amount, token_confirmation_idx=token_confirmation_idx,
            )
    return res


def settlement_balance(
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
):
    if overwrite_amount == -1 and not ask_overwrite:
        print(fail("ask_overwrite harus True atau overwrite_amount harus diisi."))
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

    path = Endpoint.SETTLEMENT_MULTIPAYMENT
    payload = {
        "total_discount": 0,
        "is_enterprise": False,
        "payment_token": "",
        "token_payment": token_payment,
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
        "timestamp": int(time.time()),
        "points_gained": 0,
        "can_trigger_rating": False,
        "akrab_members": [],
        "akrab_parent_alias": "",
        "referral_unique_code": "",
        "coupon": "",
        "payment_for": payment_for,
        "with_upsell": False,
        "topup_number": topup_number,
        "stage_token": stage_token,
        "authentication_id": "",
        "encrypted_payment_token": build_encrypted_field(urlsafe_b64=True),
        "token": "",
        "token_confirmation": "",
        "access_token": tokens["access_token"],
        "wallet_number": "",
        "encrypted_authentication_id": build_encrypted_field(urlsafe_b64=True),
        "additional_data": {
            "original_price": items[-1]["item_price"],
            "is_spend_limit_temporary": False,
            "migration_type": "",
            "akrab_m2m_group_id": "false",
            "spend_limit_amount": 0,
            "is_spend_limit": False,
            "mission_id": "",
            "tax": 0,
            "quota_bonus": 0,
            "cashtag": "",
            "is_family_plan": False,
            "combo_details": [],
            "is_switch_plan": False,
            "discount_recurring": 0,
            "is_akrab_m2m": False,
            "balance_type": "PREPAID_BALANCE",
            "has_bonus": False,
            "discount_promo": 0,
        },
        "total_amount": amount_int,
        "is_using_autobuy": False,
        "items": items,
    }
    payload["timestamp"] = ts_to_sign

    x_sig = make_payment_signature(
        tokens=tokens,
        ts_to_sign=ts_to_sign,
        payment_targets=payment_targets,
        token_payment=token_payment,
        payment_method=PaymentMethod.BALANCE,
        payment_for=payment_for,
        path=path,
    )

    print("📤 Mengirim permintaan settlement…")
    res = post_signed_payload(api_key=api_key, tokens=tokens, path=path, payload=payload, signature=x_sig)

    if isinstance(res, dict) and res.get("status") != "SUCCESS":
        print(fail(f"Gagal memulai settlement: {res}"))
        return res
    if isinstance(res, dict):
        print(ok("Pembelian selesai."))
    return res
