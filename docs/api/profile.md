# ahsiata/api/profile.py — profil, saldo & tiering

Endpoint profil pengguna dan info loyalitas (poin/tier).

## Ringkasan

Dua fungsi tipis. `get_profile` dipakai [core/session.py](../core/session.md) untuk memperoleh `subscriber_id`/`subscription_type` saat menambah/mengganti akun; `get_tiering_info` dipakai `cli.main()` untuk banner poin (hanya PREPAID).

## Fungsi

- `get_profile(api_key, access_token, id_token) -> dict` — `api/v8/profile`; payload `{access_token, app_version: CONFIG.app_version, is_enterprise: False, lang: "en"}`; return `res["data"]["profile"]` (dict kosong jika bukan dict).
- `get_tiering_info(api_key, tokens) -> dict` — `gamification/api/v8/loyalties/tiering/info`; payload `{is_enterprise: False, lang}`; return `res["data"]`.

## Alur/Detail penting

- Kunci profil yang dipakai: `subscriber_id`, `subscription_type`. Tiering: `tier`, `current_point`.

## Catatan

- `get_profile` butuh `access_token` DAN `id_token` terpisah — berbeda dengan mayoritas fungsi lain yang menerima `tokens` dict (lihat [api/packages.py](packages.md)).