# ahsiata/ui/account.py — menu login & kelola akun

Login OTP (SMS), daftar akun, ganti, tambah (`A`), hapus (`D<n>`).

## Ringkasan

`show_account_menu` adalah layar akun dari menu utama (CLI kode `1`). Jika belum ada user aktif atau user memilih tambah akun, jalankan flow login OTP; selain itu tampilkan daftar akun dari `SESSION.refresh_tokens` dengan indikator akun aktif.

## Fungsi

- `_login_prompt(api_key: str) -> tuple[str, str] | None` — banner "Login MyXL"; normalisasi input (`0…` → `62…`), validasi `628` + panjang 10–14; `get_otp(phone)` → kirim SMS; loop **5 percobaan** kode 6 digit → `submit_otp(api_key, "SMS", phone, otp)`; return `(phone_number, refresh_token)`.
- `show_account_menu() -> int | None` — loop: tidak ada user aktif / `add_user` → login & `SESSION.add_refresh_token(int(number), refresh_token)`. Dengan user: daftar `# / Nomor / Tipe / Status (✅ aktif, 💾 tersimpan)`; kunci:
  - `B` — kembali, return nomor aktif.
  - `A` — tambah akun.
  - `<n>` — pilih akun, return nomor.
  - `D` / `D<n>` — hapus akun (konfirmasi `y`); akun aktif & nomor urut invalid ditolak.

## Alur/Detail penting

- Hasil pemilihan dipakai `cli._run()` → `SESSION.set_active_user(number)`.
- Pesan/emoji seluruhnya Bahasa Indonesia dari [ui/style.py](style.md).
- `SESSION.load_tokens()` dipanggil ulang setelah tambah/hapus agar daftar sinkron.

## Catatan

- OTP hanya bisa `SMS` di sini; alur `DEVICEID` (`extend_session`) dipakai otomatis oleh [api/auth.py](../api/auth.md) `get_new_token` saat refresh gagal.
- `pause()` dipakai pada hampir semua error — alur interaktif murni, tidak cocok untuk scripting.