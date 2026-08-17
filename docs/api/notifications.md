# ahsiata/api/notifications.py — notifikasi & riwayat

Dua endpoint notifikasi.

## Ringkasan

Fungsi tipis di atas `send_api_request`; pada `status != "SUCCESS"` mencetak `fail` dan mengembalikan `None`.

## Fungsi

- `get_notifications(api_key, tokens)` — `api/v8/notification-non-grouping`; payload `{is_enterprise: False, lang: "en"}`. Return respons penuh.
- `get_notification_detail(api_key, tokens, notification_id)` — `api/v8/notification/detail`; payload `{notification_id, is_enterprise, lang}`.

## Alur/Detail penting

- Pemanggil UI [ui/notification.py](../ui/notification.md): daftar diambil `data.notifications[]` (kunci `is_read`, `brief_message`/`title`, `id`); opsi "tandai dibaca" memanggil `get_notification_detail` per notifikasi unread.

## Catatan

- `get_notification_detail` bertindak ganda sebagai penanda "dibaca" — tidak ada endpoint mark-read terpisah.