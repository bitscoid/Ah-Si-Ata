# ahsiata/api/purchase/ewallet.py — settlement e-wallet

Settlement `payment_method` DANA/ShopeePay/GoPay/OVO + menu pemilihan wallet.

## Ringkasan

`settlement_multipayment` mengirim `POST payments/api/v8/settlement-multipayment/ewallet` dengan `wallet_number` dan `payment_method`; `show_multipayment` adalah front-end interaktif: pilih wallet, (untuk DANA/OVO) masukkan nomor valid, settle, lalu tampilkan `deeplink` pembayaran (kecuali OVO).

## Fungsi

- `settlement_multipayment(api_key, tokens, items, wallet_number, payment_method, payment_for, ask_overwrite, overwrite_amount=-1, token_confirmation_idx=0, amount_idx=-1)` — skeleton baku (resolve amount → `intercept_page` → `fetch_payment_token` → payload → `make_payment_signature` → `post_signed_payload`). Payload memakai `verification_token: token_payment` (seperti QRIS), plus `wallet_number`, `payment_method`; blok `akrab` dan `autobuy`.
- `_validate_wallet_number(raw: str) -> bool` — diawali `"08"`, digit semua, panjang 10–13.
- `show_multipayment(api_key, tokens, items, payment_for, ask_overwrite, overwrite_amount=-1, token_confirmation_idx=0, amount_idx=-1)` — menu `1 DANA` `2 ShopeePay` `3 GoPay` `4 OVO`. DANA/OVO wajib nomor valid (validasi ulang). Sukses: cetak `data.deeplink` untuk non-OVO; OVO hanya instruksi buka aplikasi.

## Alur/Detail penting

- `PaymentMethod` di [constants.py](../../ahsiata/constants.md) hanya berisi `BALANCE`/`QRIS`; nama wallet adalah string literal di sini.
- Tidak ada handling `Bizz-err.Amount.Total` — decoy tidak dipakai untuk e-wallet.

## Catatan

- `intercept_page` memakai `items[0]["item_code"]`; `fetch_payment_token` memakai item `token_confirmation_idx`.