"""Settlement via e-wallet (DANA, ShopeePay, GoPay, OVO)."""
from __future__ import annotations


from ahsiata.api.client import intercept_page
from ahsiata.api.purchase.base import (
    fetch_payment_token,
    join_item_codes,
    make_payment_signature,
    post_signed_payload,
    resolve_amount,
)
from ahsiata.constants import Endpoint, LANG_EN
from ahsiata.type_dict import PaymentItem


def settlement_multipayment(
    api_key: str,
    tokens: dict,
    items: list[PaymentItem],
    wallet_number: str,
    payment_method: str,
    payment_for: str,
    ask_overwrite: bool,
    overwrite_amount: int = -1,
    token_confirmation_idx: int = 0,
    amount_idx: int = -1,
):
    if overwrite_amount == -1 and not ask_overwrite:
        print("ask_overwrite harus True atau overwrite_amount harus diisi.")
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

    path = Endpoint.SETTLEMENT_EWALLET
    payload = {
        "akrab": {"akrab_members": [], "akrab_parent_alias": "", "members": []},
        "can_trigger_rating": False,
        "total_discount": 0,
        "coupon": "",
        "payment_for": payment_for,
        "topup_number": "",
        "is_enterprise": False,
        "autobuy": {
            "is_using_autobuy": False,
            "activated_autobuy_code": "",
            "autobuy_threshold_setting": {"label": "", "type": "", "value": 0},
        },
        "cc_payment_type": "",
        "access_token": tokens["access_token"],
        "is_myxl_wallet": False,
        "wallet_number": wallet_number,
        "additional_data": {},
        "total_amount": amount_int,
        "total_fee": 0,
        "is_use_point": False,
        "lang": LANG_EN,
        "items": items,
        "verification_token": token_payment,
        "payment_method": payment_method,
        "timestamp": ts_to_sign,
    }

    x_sig = make_payment_signature(
        tokens=tokens,
        ts_to_sign=ts_to_sign,
        payment_targets=payment_targets,
        token_payment=token_payment,
        payment_method=payment_method,
        payment_for=payment_for,
        path=path,
    )

    print("Mengirim permintaan settlement…")
    return post_signed_payload(api_key=api_key, tokens=tokens, path=path, payload=payload, signature=x_sig)


def _validate_wallet_number(raw: str) -> bool:
    return raw.startswith("08") and raw.isdigit() and 10 <= len(raw) <= 13


def show_multipayment(
    api_key: str,
    tokens: dict,
    items: list[PaymentItem],
    payment_for: str,
    ask_overwrite: bool,
    overwrite_amount: int = -1,
    token_confirmation_idx: int = 0,
    amount_idx: int = -1,
):
    """Prompt for e-wallet choice + (optional) wallet number, then settle."""
    wallet_number = ""
    while True:
        print("Pilihan multipayment:")
        print("1. DANA\n2. ShopeePay\n3. GoPay\n4. OVO")
        choice = input("Pilih metode pembayaran: ")
        if choice == "1":
            payment_method = "DANA"
            wallet_number = input("Masukkan nomor DANA (contoh: 08123456789): ")
            if not _validate_wallet_number(wallet_number):
                print("Nomor DANA tidak valid. Pastikan nomor diawali dengan '08' dan memiliki panjang yang benar.")
                continue
            break
        if choice == "2":
            payment_method = "SHOPEEPAY"
            break
        if choice == "3":
            payment_method = "GOPAY"
            break
        if choice == "4":
            payment_method = "OVO"
            wallet_number = input("Masukkan nomor OVO (contoh: 08123456789): ")
            if not _validate_wallet_number(wallet_number):
                print("Nomor OVO tidak valid. Pastikan nomor diawali dengan '08' dan memiliki panjang yang benar.")
                continue
            break
        print("Pilihan tidak valid.")

    res = settlement_multipayment(
        api_key, tokens, items, wallet_number, payment_method, payment_for,
        ask_overwrite, overwrite_amount, token_confirmation_idx, amount_idx,
    )

    if not isinstance(res, dict) or res.get("status") != "SUCCESS":
        print("Gagal memulai settlement.")
        print(f"Error: {res}")
        return

    if payment_method != "OVO":
        deeplink = res.get("data", {}).get("deeplink", "")
        if deeplink:
            print(f"Silahkan selesaikan pembayaran melalui link berikut:\n{deeplink}")
    else:
        print("Silahkan buka aplikasi OVO Anda untuk menyelesaikan pembayaran.")
