# ahsiata/api/purchase/base.py — helper bersama settlement

Resolver amount, penggabung item code, fetch payment token, POST payload bertanda, dan factory signature.

## Ringkasan

Skeleton semua settlement (balance, QRIS, e-wallet, bounty, loyalty) identik: resolve amount → intercept → fetch `token_payment` → enkripsi body → sign (signature khusus) → POST via `post_encrypted` (dengan `x_signature` menimpa signature `xdata`) → dekripsi. Modul ini menyediakan blok penyusun itu; tiap variant di [balance.py](balance.md), [qris.py](qris.md), [ewallet.py](ewallet.md), [redeem.py](redeem.md).

## Fungsi

- `resolve_amount(items, *, overwrite_amount: int, ask_overwrite: bool, amount_idx: int) -> int` — jika `overwrite_amount != -1` pakai itu; jika `amount_idx == -1` pakai `items[-1]["item_price"]` (item **terakhir**); else `0`. Jika `ask_overwrite`: tanya user (input kosong = pakai default, non-int = warn + harga awal).
- `join_item_codes(items: list[dict]) -> str` — `";".join(item["item_code"])` (format payment-target server).
- `fetch_payment_token(api_key, tokens, item_code, token_confirmation) -> tuple[str, int] | None` — `payments/api/v8/payment-methods-option`; payload `{payment_type: "PURCHASE", payment_target, token_confirmation, is_referral: False}`; return `(data.token_payment, int(data.timestamp))`.
- `post_signed_payload(*, api_key, tokens, path, payload, signature) -> dict | str` — `encryptsign_xdata` + `post_encrypted(..., x_signature=signature)`.
- `make_payment_signature(*, tokens, ts_to_sign, payment_targets, token_payment, payment_method, payment_for, path) -> str` — wrapper `make_x_signature_payment`.
- `make_bounty_signature(*, tokens, ts_to_sign, item_code, token_payment) -> str` — wrapper `make_x_signature_bounty`.
- `make_loyalty_signature(*, ts_to_sign, item_code, token_confirmation, path) -> str` — wrapper `make_x_signature_loyalty`.
- `make_bounty_allotment_signature(*, ts_to_sign, item_code, token_confirmation, destination_msisdn, path) -> str` — wrapper `make_x_signature_bounty_allotment`.

## Alur/Detail penting

- Seluruh settlement memakai `timestamp` hasil `fetch_payment_token` sebagai `ts_to_sign` (payload `timestamp` disamakan), bukan waktu lokal.
- Signature primitive ada di [core/crypto.py](../../core/crypto.md) — salt dari `CONFIG.payment_sign_salt`.

## Catatan

- Quirk `resolve_amount`: kondisi `elif amount_idx == -1` memakai `items[-1]` — artinya tanpa `amount_idx`, harga default yang dipakai adalah harga item **terakhir**, bukan pertama. (`ponytail:` perilaku ini dipertahankan — pemanggil menyusun `items` dengan decoy di akhir untuk memanfaatkannya.)