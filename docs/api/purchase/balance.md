# ahsiata/api/purchase/balance.py — settlement saldo (PULSA)

Settlement `payment_method: "BALANCE"` + logika decoy terpusat.

## Ringkasan

Menangani pembelian dengan saldo/pulsa, termasuk error `Bizz-err.Amount.Total` yang membawa jumlah koreksi dari server. `settle_with_decoy` menambahkan paket decoy lalu menyesuaikan `total_amount`; jika server membalas error koreksi, settlement diulang sekali dengan jumlah koreksi tersebut.

## Fungsi

- `append_decoy_item(items: list[PaymentItem], decoy_detail: dict) -> None` — append `PaymentItem` dari `decoy_detail["package_option"]` (`item_code`, `item_price`, `item_name`) + `decoy_detail["token_confirmation"]`; `product_type` dan `tax` = `0`/`""`.
- `settle_with_decoy(api_key, tokens, items, payment_for, decoy_detail, token_confirmation_idx=0) -> dict | str | None` — jika `decoy_detail is None`: delegasi `settlement_balance(..., ask_overwrite=True)`. Jika ada: append decoy, `total = items[0]["item_price"] + decoy price`, settlement dengan `overwrite_amount=total`; jika luaran `status != "SUCCESS"` dan `"Bizz-err.Amount.Total"` ada di `message`: ekstrak angka (`int(msg.split("=")[1].strip())`) dan ulang sekali dengan angka itu.
- `settlement_balance(api_key, tokens, items, payment_for, ask_overwrite, overwrite_amount=-1, token_confirmation_idx=0, amount_idx=-1, topup_number="", stage_token="")` — alur lengkap (lihat bawah). Return respons didekripsi; non-`SUCCESS` dicetak `fail`.

## Alur/Detail penting — `settlement_balance`

1. Validasi: `overwrite_amount == -1 && not ask_overwrite` → `fail` + `None`.
2. `token_confirmation = items[token_confirmation_idx]["token_confirmation"]`; `payment_targets = join_item_codes(items)`.
3. `resolve_amount(...)` → `amount_int`.
4. `intercept_page(api_key, tokens, items[0]["item_code"], False)`.
5. `fetch_payment_token(...)` atas item `token_confirmation_idx` → `(token_payment, ts_to_sign)`.
6. Payload `POST payments/api/v8/settlement-multipayment` (`Endpoint.SETTLEMENT_MULTIPAYMENT`), ~40 kunci — yang penting: `payment_method: "BALANCE"`, `total_amount`, `items`, `timestamp = ts_to_sign`, `token_payment`, `encrypted_payment_token`/`encrypted_authentication_id` (dari `build_encrypted_field(urlsafe_b64=True)`), `additional_data` (mis. `original_price: items[-1]["item_price"]`, `balance_type: "PREPAID_BALANCE"`), `access_token`.
7. Signature `make_payment_signature(...)` (path = SETTLEMENT_MULTIPAYMENT), kirim via `post_signed_payload`.

## Catatan

- `token_confirmation_idx` berpindah dari item asli ke item decoy pada flow "V2" (decoy menjadi indeks 1) — lihat [ui/package/details.py](../../ui/package/details.md) opsi 4/5.
- Error `Bizz-err.InvalidProduct` (produk invalid) **tidak** di-handle di sini — tetap dicetak `fail` mentah.