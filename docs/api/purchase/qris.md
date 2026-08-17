# ahsiata/api/purchase/qris.py — settlement QRIS

Settlement `payment_method: "QRIS"`, ambil kode QRIS, dan render QR di terminal.

## Ringkasan

Tiga langkah: `settlement_qris` membuat transaksi dan mengembalikan `transaction_code`, `get_qris_code` mengambil `qr_code` dari endpoint pending, `show_qris_payment` merender QR ASCII (`qrcode.print_ascii`) plus tautan viewer eksternal.

## Konstanta/Fungsi

- `QRIS_VIEWER_URL = "https://ki-ar-kod.netlify.app/?data={qris_b64}"` — viewer QRIS berbasis b64.
- `settlement_qris(api_key, tokens, items, payment_for, ask_overwrite, overwrite_amount=-1, token_confirmation_idx=0, amount_idx=-1, topup_number="", stage_token="") -> str | None` — alur sama dengan balance (`intercept_page` → `fetch_payment_token` → payload → `make_payment_signature`), tetapi `POST payments/api/v8/settlement-multipayment/qris` dengan `payment_method: "QRIS"` dan `verification_token: token_payment` (bukan `token_payment`/`encrypted_*`). `additional_data` lebih ringkas (tanpa `balance_type`/`akrab_*`, ada `benefit_type: ""`). Return `data.transaction_code`.
- `get_qris_code(api_key, tokens, transaction_id) -> str | None` — `payments/api/v8/pending-detail`; payload `{transaction_id, status: "", ...}`; return `data.qr_code`.
- `show_qris_payment(...) -> str | None` — `settlement_qris` → `get_qris_code` → render `qrcode.QRCode(version=1, ERROR_CORRECT_L, box_size=1, border=1)` via `print_ascii(invert=True)`; cetak `QRIS_VIEWER_URL.format(qris_b64=urlsafe_b64(qris_code))`. Return b64 (atau `None` saat gagal).

## Alur/Detail penting

- Opsi decoy QRIS (menu 6/7 di [ui/package/details.py](../../ui/package/details.md)) memakai `payment_for="SHARE_PACKAGE"`, `token_confirmation_idx=1`, dan amount diatur manual oleh user (trial & error; `0` = malformed).
- `verification_token` menggantikan `token_payment` yang dipakai balance.

## Catatan

- Bergantung paket `qrcode` (requirements) — render ASCII tidak butuh display server.