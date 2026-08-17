# ahsiata/api/transactions.py — riwayat transaksi

Satu endpoint riwayat pembayaran.

## Ringkasan

Fungsi tipis yang mengembalikan `data` dari respons (daftar transaksi). Dipakai [ui/payment.py](../ui/payment.md) `show_transaction_history` (menu `7`).

## Fungsi

- `get_transaction_history(api_key, tokens) -> dict | None` — `payments/api/v8/transaction-history`; payload `{is_enterprise: False, lang: "en"}`; return `res["data"]` jika dict, else `None`.

## Alur/Detail penting

- UI membaca `data["list"]` dengan kunci per item: `timestamp` (epoch), `title`, `price`, `payment_method_label`, `payment_status`.

## Catatan

- Tidak ada validasi `status`/print error di sini; kegagalan hanya mengembalikan `None`.