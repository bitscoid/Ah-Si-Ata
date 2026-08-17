# ahsiata/cli.py — entry point & loop menu utama

`main()` (inisialisasi state + loop menu) plus menu utama dua kolom.

## Ringkasan

Entry point sebenarnya semua jalur peluncuran. `main()` memanggil `SESSION.initialize()` dan `BOOKMARK.initialize()` (satu-satunya tempat state disk dimuat), lalu `_run()`: loop tak hingga menampilkan menu utama dan memproses pilihan. Sebelum menu, setiap iterasi mengambil user aktif (auto-refresh token di dalam `SESSION.get_active_user()`), saldo, dan tiering poin untuk PREPAID.

## Konstanta

- `WIDTH = 55` — lebar tampilan.
- `MENU_ITEMS` — 18 pasangan `(kode, emoji, label)` untuk menu dua kolom.

## Fungsi

- `show_main_menu(profile: dict) -> None` — render banner `🔥 AH-SI-ATA 🔥`, nomor/tipe akun, saldo + tanggal kedaluwarsa, info poin/tier, lalu menu dua kolom.
- `_show_result(label: str, res) -> None` — render respons API sebagai baris ber-label (bukan JSON mentah); dict/list di-`json.dumps`.
- `_run() -> None` — loop utama; `menu code` diproses di sini.
- `main() -> None` — init state, panggil `_run()`, tangkap `KeyboardInterrupt` (print perpisahan, keluar bersih).

## Alur/Detail penting

Kode menu aktual (berbeda dari tabel lama di README):

| Kode | Aksi |
|---|---|
| `1` | Menu akun (`show_account_menu` → `set_active_user`) |
| `2` | `fetch_my_packages()` — paket saya |
| `3` | `show_hot_menu()` — paket HOT |
| `4` | Input option code → `show_package_details(..., False)` (kecuali `99`) |
| `5` | Input family code → `get_packages_by_family` (kecuali `99`) |
| `6` | Loop: family code, mulai, decoy (y/n), jeda (y/n), detik → `purchase_by_family` |
| `7` | `show_transaction_history` |
| `8` | `show_family_info` (Family Plan) |
| `9` | `show_circle_info` (Circle) |
| `P` | `show_store_segments_menu(is_enterprise?)` (Promo) |
| `F` | `show_family_list_menu(subs_type, is_enterprise?)` |
| `S` | `show_store_packages_menu(subs_type, is_enterprise?)` |
| `C` | `show_redeemables_menu(is_enterprise?)` (Claim) |
| `R` | Registrasi Dukcapil (input MSISDN/NIK/KK → `dukcapil`) |
| `V` | Validasi MSISDN (`validate_msisdn`) |
| `N` | `show_notification_menu` |
| `B` | `show_bookmark_menu` |
| `X` | Keluar (`sys.exit(0)`) |
| `t` | Shortcut testing: `pause()` |

Profil dikumpulkan tiap iterasi: `get_balance` → `remaining`/`expired_at`; jika `subscription_type == "PREPAID"` then `get_tiering_info` → `tier` + `current_point`.

## Catatan

- `ponytail:` di docstring `main()` — path state hardcoded relatif-CWD; pindah ke dir data (XDG) saat mode headless/terinstall dibutuhkan. Error `print` + `input` di `core/session.py` dibiarkan; ganti exception + `logging` saat otomasi diperlukan.
- Jika `show_account_menu()` mengembalikan falsy, dicetak "Gagal memuat user" lalu loop lagi.