# ahsiata/core/session.py — sesi & refresh token

Singleton `SESSION` untuk state multi-akun + rotasi token OIDC, disimpan di `refresh-tokens.json` dan `active.number` (relatif CWD).

## Ringkasan

Menyimpan daftar refresh token per nomor dan user aktif beserta token OIDC-nya. Tidak ada I/O saat import; state dimuat lewat `SESSION.initialize()` dari entry point. `get_active_user()` meng-*rotate* token otomatis jika melewati `TOKEN_REFRESH_INTERVAL` (default 300 detik).

## Kelas

- `Session` — singleton `__new__` + `_initialized`; `api_key` diisi `CONFIG.api_key` saat konstruksi (instance: `SESSION`).
  - `initialize() -> None` — muat `refresh-tokens.json` (buat `[]` jika belum ada) + `load_active_number()`; set `last_refresh_time`.
  - `load_tokens() -> None` — baca file; buang entri tanpa `number`/`refresh_token` (print peringatan).
  - `write_tokens_to_file() -> None` / `write_active_number() -> None` / `load_active_number() -> None` — persistensi (indent 4; `active.number` dihapus jika tidak ada user aktif).
  - `add_refresh_token(number: int, refresh_token: str) -> None` — update token existing; untuk nomor baru: `get_new_token` + `get_profile` untuk `subscriber_id`/`subscription_type`, append, simpan, set aktif.
  - `remove_refresh_token(number: int) -> None` — hapus dari list; jika akun aktif yang dihapus, pindah ke akun pertama tersisa (atau kosongkan).
  - `set_active_user(number: int) -> bool` — tukar token (`get_new_token`), ambil profil, set `active_user`, simpan file + `active.number`.
  - `renew_active_user_token() -> bool` — refresh token user aktif lalu `add_refresh_token`.
  - `get_active_user() -> dict | None` — jika belum ada user aktif, coba pakai token pertama; auto-`renew_active_user_token()` jika `last_refresh_time` kosong atau melebihi interval.
  - `get_active_tokens() -> dict | None` — helper → `active_user["tokens"]`.

## Alur/Detail penting

- Skema entri `refresh-tokens.json`: `{number, subscriber_id, subscription_type, refresh_token}`.
- Struktur `active_user`: `{number, subscriber_id, subscription_type, tokens: {refresh_token, access_token, id_token}}`.
- `remove_refresh_token` pada akun aktif mencetak prompt `input(...)` saat tidak ada user tersisa.
- Semua kegagalan token/profil dicetak `fail` + `input("Tekan enter…")` — blokir interaktif, tidak raise.

## Catatan

- `refresh-tokens.json` berisi refresh token = akses penuh akun; plaintext, jangan di-commit (sudah `.gitignore`).
- Bergantung pada [api/auth.py](../api/auth.md) (`get_new_token`) dan [api/profile.py](../api/profile.md) (`get_profile`).