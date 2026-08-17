# Dokumentasi Ah-Si-Ata

Dokumentasi teknis per-file untuk seluruh codebase `Ah-Si-Ata` — CLI Python (Bahasa Indonesia) yang berinteraksi dengan backend MyXL (XL Axiata): browsing paket, pembelian (saldo/QRIS/e-wallet), trik decoy, Family Plan, Circle, store, dan bookmark.

## Organisasi

Setiap file sumber memiliki satu file `.md` yang mencerminkan layout paket:

| Folder docs | Isi |
|---|---|
| [docs/](README.md) | Entry point & paket inti (`main.py`, `ahsiata/`) |
| [docs/core/](core/) | Lapisan layanan/state: sesi, bookmark, decoy, kripto, log |
| [docs/api/](api/) | Lapisan klien API (endpoint, payload, enkripsi) |
| [docs/api/purchase/](api/purchase/) | Settlement pembelian (balance, QRIS, e-wallet, redeem) |
| [docs/ui/](ui/) | Lapisan menu interaktif (print + input) |
| [docs/ui/package/](ui/package/) · [docs/ui/purchase/](ui/purchase/) · [docs/ui/store/](ui/store/) · [docs/ui/circle/](ui/circle/) | Sub-menu UI |

Struktur per-file: `# path` + tujuan satu baris, `## Ringkasan`, `## Fungsi/Kelas`, `## Alur/Detail penting`, `## Catatan`.

## Daftar Isi

### Root — `main.py` & paket `ahsiata/`

- [main.py](main.md) — wrapper tipis jalur lama `python main.py`
- [ahsiata/__main__.py](ahsiata/__main__.md) — entry `python -m ahsiata`
- [ahsiata/cli.py](ahsiata/cli.md) — `main()` + loop menu utama
- [ahsiata/config.py](ahsiata/config.md) — `CONFIG` (frozen dataclass dari env)
- [ahsiata/constants.py](ahsiata/constants.md) — path endpoint & konstanta protokol
- [ahsiata/type_dict.py](ahsiata/type_dict.md) — kontrak `PaymentItem` (TypedDict)

### `ahsiata/core/` — layanan & state

- [bookmark.py](core/bookmark.md) — singleton `BOOKMARK` (`bookmark.json`)
- [crypto.py](core/crypto.md) — primitif AES-CBC & HMAC (xdata, signature)
- [decoy.py](core/decoy.md) — singleton `DECOY`, cache paket decoy (TTL 300 s)
- [log.py](core/log.md) — log diagnostik `ahsiata.log`
- [session.py](core/session.md) — singleton `SESSION` (multi-akun + rotasi token)

### `ahsiata/api/` — klien backend

- [auth.py](api/auth.md) — CIAM OIDC: OTP, extend-session, refresh token
- [catalog.py](api/catalog.md) — segments, family list, store packages, redeemables
- [circle.py](api/circle.md) — Circle / Family Hub (MSISDN terenkripsi)
- [client.py](api/client.md) — HTTP rendah: session + retry, header, enkripsi respons
- [encrypt.py](api/encrypt.md) — fingerprint `ax.fp`, `encryptsign_xdata`, timestamp
- [family_plan.py](api/family_plan.md) — Family Plan (member, kuota)
- [notifications.py](api/notifications.md) — notifikasi & detail
- [packages.py](api/packages.md) — family, package, addons, unsubscribe
- [profile.py](api/profile.md) — profil & tiering (poin)
- [registration.py](api/registration.md) — registrasi Dukcapil
- [transactions.py](api/transactions.md) — riwayat transaksi

### `ahsiata/api/purchase/` — settlement

- [base.py](api/purchase/base.md) — helper bersama: amount, token, signature
- [balance.py](api/purchase/balance.md) — settlement saldo + decoy (`Bizz-err.Amount.Total` retry)
- [qris.py](api/purchase/qris.md) — settlement QRIS + render QR terminal
- [ewallet.py](api/purchase/ewallet.md) — settlement e-wallet (DANA/ShopeePay/GoPay/OVO)
- [redeem.py](api/purchase/redeem.md) — bounty, loyalty (poin), bounty allotment

### `ahsiata/ui/` — menu

- [account.py](ui/account.md) — login OTP & kelola akun
- [bookmark.py](ui/bookmark.md) — menu bookmark
- [family_plan.py](ui/family_plan.md) — menu Family Plan
- [hot.py](ui/hot.md) — menu paket HOT + bundle HOT-2
- [notification.py](ui/notification.md) — menu notifikasi
- [payment.py](ui/payment.md) — riwayat transaksi
- [style.py](ui/style.md) — ANSI color & helper teks
- [utils.py](ui/utils.md) — clear screen, pause, HTML→teks, format kuota/harga

### `ahsiata/ui/package/` · `ui/purchase/` · `ui/store/` · `ui/circle/`

- [package/details.py](ui/package/details.md) — detail paket, opsi bayar, redeem; `fetch_my_packages`
- [package/list.py](ui/package/list.md) — daftar paket per family
- [purchase/loop.py](ui/purchase/loop.md) — beli semua paket dalam family
- [purchase/single.py](ui/purchase/single.md) — beli N kali via option code
- [store/redeemables.py](ui/store/redeemables.md) — menu redeemables
- [store/search.py](ui/store/search.md) — family list & store packages (paginasi)
- [store/segments.py](ui/store/segments.md) — menu segmen store
- [circle/info.py](ui/circle/info.md) — info Circle + bonus + buat Circle

## Alur Umum (Common Flows)

- **Pembelian paket**: `ui/package/details.md` (menu opsi bayar) → `api/purchase/base.md` (skeleton: amount → intercept → token → sign → POST) → salah satu dari [balance.md](api/purchase/balance.md), [qris.md](api/purchase/qris.md), [ewallet.md](api/purchase/ewallet.md), atau [redeem.md](api/purchase/redeem.md).
- **Trik decoy**: konsep & cache di [core/decoy.md](core/decoy.md); eksekusi (append item + retry `Bizz-err.Amount.Total`) di [api/purchase/balance.md](api/purchase/balance.md) (`settle_with_decoy`); pemicu menu di [ui/package/details.md](ui/package/details.md) (opsi 4–7).
- **Login & sesi**: [ui/account.md](ui/account.md) → [api/auth.md](api/auth.md) (CIAM OIDC) → [core/session.md](core/session.md) (multi-akun + auto-refresh 300 s).
- **Rotasi token otomatis**: `get_active_user()` di [core/session.md](core/session.md); fallback `extend_session` + `submit_otp(DEVICEID)` di [api/auth.md](api/auth.md).
