# ahsiata/ui/notification.py — menu notifikasi

Daftar notifikasi + tandai semua dibaca.

## Ringkasan

`show_notification_menu` (CLI `N`) mengambil `get_notifications`, menampilkan total & jumlah unread, lalu `S` memanggil `get_notification_detail` untuk setiap notifikasi unread (endpoint detail berperan sebagai penanda dibaca).

## Fungsi

- `show_notification_menu() -> None` — loop:
  - `B` — kembali.
  - `S` — untuk tiap notifikasi dengan `is_read is False`: `get_notification_detail(api_key, tokens, n["id"])`; lalu `ok("Semua notifikasi ditandai dibaca")`.

## Alur/Detail penting

- Data: `res["data"]["notifications"]`; per item dipakai `is_read`, `brief_message`/`title`, `id`.
- Gagal ambil notifikasi → `fail` + return.

## Catatan

- Tidak ada menu detail per-notifikasi; hanya "mark all read".