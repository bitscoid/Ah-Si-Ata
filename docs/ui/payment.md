# ahsiata/ui/payment.py — riwayat transaksi

Menampilkan riwayat pembayaran (CLI `7`).

## Ringkasan

Satu fungsi: `show_transaction_history` mengambil `get_transaction_history`, lalu mencetak setiap transaksi dengan waktu GMT+7 (Jakarta), judul, metode, status, dan harga terformat.

## Fungsi

- `show_transaction_history(api_key, tokens) -> None` — `res["list"]`; untuk tiap item: `timestamp` epoch → `datetime.fromtimestamp(ts, tz=GMT+7).strftime("%Y-%m-%d %H:%M:%S")`; `title`, `payment_method_label`, `payment_status`, `price` via `format_price` ([utils.md](utils.md)). Kosong → `info("Tidak ada transaksi")`.

## Alur/Detail penting

- Gagal ambil riwayat (`not isinstance(res, dict)`) → `fail` + return.
- Exit via satu `input(...)` (bukan loop).

## Catatan

- Tidak ada paginasi; semua transaksi dicetak sekaligus.