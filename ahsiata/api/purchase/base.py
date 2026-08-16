"""Shared helpers for purchase/settlement flows.

All settlement variants (balance, qris, ewallet, bounty, loyalty) follow the
same skeleton: amount resolution → intercept → fetch payment-methods → encrypt
body → sign request → POST → decrypt response. Only the payload shape, signing
function, and endpoint path differ.
"""
from __future__ import annotations

from ahsiata.api.client import post_encrypted, send_api_request
from ahsiata.api.encrypt import encryptsign_xdata
from ahsiata.constants import Endpoint, LANG_EN
from ahsiata.core.crypto import (
    make_x_signature_bounty,
    make_x_signature_bounty_allotment,
    make_x_signature_loyalty,
    make_x_signature_payment,
)


def resolve_amount(
    items: list[dict],
    *,
    overwrite_amount: int,
    ask_overwrite: bool,
    amount_idx: int,
) -> int:
    """Pick the final amount: explicit overwrite > ask user > items[amount_idx].price."""
    if overwrite_amount != -1:
        amount_int = overwrite_amount
    elif amount_idx == -1:
        amount_int = items[amount_idx]["item_price"]
    else:
        amount_int = 0

    if ask_overwrite:
        print(f"Total jumlah adalah {amount_int}.\nMasukkan jumlah baru jika Anda ingin menimpa.")
        amount_str = input("Tekan enter untuk mengabaikan & gunakan jumlah default: ")
        if amount_str:
            try:
                amount_int = int(amount_str)
            except ValueError:
                print("Input overwrite tidak valid, menggunakan harga awal.")
    return amount_int


def join_item_codes(items: list[dict]) -> str:
    """`item1_code;item2_code;…` (server's payment-target format)."""
    return ";".join(item["item_code"] for item in items)


def fetch_payment_token(api_key: str, tokens: dict, item_code: str, token_confirmation: str) -> tuple[str, int] | None:
    """Return (token_payment, ts_to_sign) from the payment-methods endpoint."""
    payload = {
        "payment_type": "PURCHASE",
        "is_enterprise": False,
        "payment_target": item_code,
        "lang": LANG_EN,
        "is_referral": False,
        "token_confirmation": token_confirmation,
    }
    print("Mendapatkan metode pembayaran…")
    res = send_api_request(api_key, Endpoint.PAYMENT_METHODS_OPTION, payload, tokens["id_token"], "POST")
    if not isinstance(res, dict) or res.get("status") != "SUCCESS":
        print("Gagal mengambil metode pembayaran.")
        print(f"Error: {res}")
        return None
    data = res["data"]
    return data["token_payment"], int(data["timestamp"])


def post_signed_payload(
    *,
    api_key: str,
    tokens: dict,
    path: str,
    payload: dict,
    signature: str,
) -> dict | str:
    """Encrypt payload, attach payment signature, POST, return decrypted body."""
    encrypted = encryptsign_xdata(
        api_key=api_key,
        method="POST",
        path=path,
        id_token=tokens["id_token"],
        payload=payload,
    )
    return post_encrypted(api_key, path, tokens["id_token"], encrypted, x_signature=signature)


# -- Signature factories ------------------------------------------------------

def make_payment_signature(
    *,
    tokens: dict,
    ts_to_sign: int,
    payment_targets: str,
    token_payment: str,
    payment_method: str,
    payment_for: str,
    path: str,
) -> str:
    return make_x_signature_payment(
        tokens["access_token"], ts_to_sign, payment_targets, token_payment,
        payment_method, payment_for, path,
    )


def make_bounty_signature(
    *,
    tokens: dict,
    ts_to_sign: int,
    item_code: str,
    token_payment: str,
) -> str:
    return make_x_signature_bounty(tokens["access_token"], ts_to_sign, item_code, token_payment)


def make_loyalty_signature(
    *,
    ts_to_sign: int,
    item_code: str,
    token_confirmation: str,
    path: str,
) -> str:
    return make_x_signature_loyalty(ts_to_sign, item_code, token_confirmation, path)


def make_bounty_allotment_signature(
    *,
    ts_to_sign: int,
    item_code: str,
    token_confirmation: str,
    destination_msisdn: str,
    path: str,
) -> str:
    return make_x_signature_bounty_allotment(ts_to_sign, item_code, token_confirmation, path, destination_msisdn)