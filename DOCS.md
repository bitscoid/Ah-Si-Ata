# Dokumentasi Teknis — Ah-Si-Ata

Dokumen ini berisi dokumentasi teknis untuk seluruh codebase `Ah-Si-Ata`. Dokumentasi mencakup arsitektur, struktur direktori, alur autentikasi, protokol komunikasi API, kriptografi, alur pembelian, serta deskripsi setiap modul dan file pendukung.

> **Catatan**: Proyek ini adalah CLI client untuk salah satu penyedia layanan internet seluler Indonesia. Konten yang ada di sini murni untuk tujuan dokumentasi teknis. Seluruh pengguna bertanggung jawab atas kepatuhan terhadap hukum dan ketentuan yang berlaku (lihat README).

---

## Daftar Isi

1. [Ringkasan Proyek](#1-ringkasan-proyek)
2. [Arsitektur & Pola Desain](#2-arsitektur--pola-desain)
3. [Struktur Direktori](#3-struktur-direktori)
4. [Alur Eksekusi Aplikasi](#4-alur-eksekusi-aplikasi)
5. [Konfigurasi Lingkungan (`.env`)](#5-konfigurasi-lingkungan-env)
6. [Autentikasi & Manajemen Sesi](#6-autentikasi--manajemen-sesi)
7. [Protokol Komunikasi API](#7-protokol-komunikasi-api)
8. [Kriptografi & Penandaan (Signing)](#8-kriptografi--penandaan-signing)
9. [Lapisan Klien (Client Layer)](#9-lapisan-klien-client-layer)
10. [Lapisan Menu (UI Layer)](#10-lapisan-menu-ui-layer)
11. [Lapisan Layanan (Service Layer)](#11-lapisan-layanan-service-layer)
12. [Alur Pembelian & Metode Pembayaran](#12-alur-pembelian--metode-pembayaran)
13. [Paket Decoy](#13-paket-decoy)
14. [Bookmark Paket](#14-bookmark-paket)
15. [Paket HOT](#15-paket-hot)
16. [Data Files](#16-data-files)
17. [Dependensi](#17-dependensi)
18. [Setup & Menjalankan](#18-setup--menjalankan)
19. [Catatan Pengembangan](#19-catatan-pengembangan)

---

## 1. Ringkasan Proyek

`Ah-Si-Ata` adalah aplikasi **Python CLI** yang mensimulasikan perilaku klien aplikasi seluler MyXL (provider seluler XL Axiata) di sisi *backend*, memungkinkan pengguna untuk:

- Login menggunakan **OTP SMS** (OIDC flow) dan mempertahankan sesi via **refresh token**.
- Melihat profil, saldo, kuota, dan riwayat transaksi.
- Menjelajahi katalog paket berdasarkan **family code**, **option code**, **store segments**, dan **redeemables**.
- Membeli paket melalui beberapa metode pembayaran: **saldo/pulsa (BALANCE)**, **e-wallet** (DANA/ShopeePay/GoPay/OVO), dan **QRIS**.
- Membeli paket secara massal/loop dalam satu family.
- Mengelola **Family Plan** dan **Circle** (anggota, kuota, bonus).
- Menyimpan **bookmark** paket favorit.

Bahasa pemrograman: **Python 3** (>= 3.10, memakai type hints `dict | None` dan `TypedDict`).

---

## 2. Arsitektur & Pola Desain

Aplikasi menggunakan arsitektur berlapis sederhana:

```
┌────────────────────────────────────────────┐
│              main.py (entry point)          │
└──────────────┬─────────────────────────────┘
               │
┌──────────────▼─────────────────────────────┐
│         app/menus/  (UI / presentasi)       │
│   Menampilkan menu, membaca input,          │
│   memformat output (ASCII, HTML→text)       │
└──────────────┬─────────────────────────────┘
               │
┌──────────────▼─────────────────────────────┐
│        app/client/  (API client layer)      │
│   Memanggil endpoint, menyusun payload,     │
│   enkripsi/signature, parsing respons       │
└──────────────┬─────────────────────────────┘
               │
┌──────────────▼─────────────────────────────┐
│        app/service/  (service layer)        │
│   State: auth session, bookmark, decoy,     │
│   kriptografi inti                          │
└────────────────────────────────────────────┘
```

Pola desain yang digunakan:

| Pola | Penerapan |
|---|---|
| **Singleton** | `Auth` (`app/service/auth.py`), `Bookmark` (`app/service/bookmark.py`), `DecoyPackage` (`app/service/decoy.py`) — semuanya memakai `__new__` + flag `_initialized_` |
| **Facade / Gateway** | `app/client/ahsiata.py` — satu titik masuk `send_api_request()` untuk semua panggilan API utama |
| **TypedDict** | `app/type_dict.py` — kontrak struktur data `PaymentItem`, `PackageToBuy` |
| **Helper module** | `app/service/crypto_helper.py` — fungsi kripto murni yang di-re-export oleh `app/client/encrypt.py` |

---

## 3. Struktur Direktori

```
Ah-Si-Ata/
├── main.py                      # Entry point aplikasi
├── requirements.txt             # Dependensi Python
├── setup.sh                     # Script setup Linux (virtualenv + deps)
├── README.md                    # Panduan pengguna
├── .env                         # Variabel lingkungan (rahasia, tidak di-commit)
├── .env.template                # Template variabel lingkungan
├── .gitignore
├── ax.fp                        # Fingerprint perangkat (dihasilkan otomatis)
├── active.number                # Nomor akun aktif (dihasilkan otomatis)
├── refresh-tokens.json          # Penyimpanan refresh token (dihasilkan otomatis)
├── bookmark.json                # Bookmark paket (dihasilkan otomatis)
│
├── app/
│   ├── __init__.py
│   ├── type_dict.py             # Definisi TypedDict
│   │
│   ├── client/                  # Lapisan klien API
│   │   ├── ahsiata.py            # Klien API utama (profile, packages, dll.)
│   │   ├── ciam.py              # Klien autentikasi CIAM (OTP/OIDC)
│   │   ├── encrypt.py           # Enkripsi/signature (re-export crypto_helper)
│   │   ├── famplan.py           # Family Plan API
│   │   ├── circle.py            # Circle / Family Hub API
│   │   ├── registration.py      # Registrasi (dukcapil, validasi PUK)
│   │   ├── purchase/            # Settlement pembelian
│   │   │   ├── common.py        # Utility payment methods
│   │   │   ├── balance.py       # Pembayaran saldo/pulsa
│   │   │   ├── qris.py          # Pembayaran QRIS
│   │   │   ├── ewallet.py       # Pembayaran e-wallet
│   │   │   └── redeem.py        # Penukaran bounty/loyalty
│   │   └── store/               # Klien katalog store
│   │       ├── redeemables.py   # Redeemables
│   │       ├── search.py        # Family list & search paket
│   │       └── segments.py      # Store segments
│   │
│   ├── menus/                   # Lapisan UI
│   │   ├── util.py              # clear_screen, pause, HTML→text, format kuota
│   │   ├── account.py           # Login / kelola akun
│   │   ├── package.py           # Detail paket, my packages, family packages
│   │   ├── purchase.py          # Pembelian massal
│   │   ├── payment.py           # Riwayat transaksi
│   │   ├── hot.py               # Paket HOT & HOT-2
│   │   ├── bookmark.py          # Menu bookmark
│   │   ├── famplan.py           # Menu Family Plan
│   │   ├── circle.py            # Menu Circle
│   │   ├── notification.py      # Menu notifikasi
│   │   └── store/               # Menu store
│   │       ├── redeemables.py
│   │       ├── search.py
│   │       └── segments.py
│   │
│   └── service/                 # Lapisan layanan / state
│       ├── auth.py              # Singleton Auth (sesi & token)
│       ├── crypto_helper.py     # Implementasi kripto inti
│       ├── decoy.py             # Singleton DecoyPackage
│       └── bookmark.py          # Singleton Bookmark
│
├── decoy_data/                  # Konfigurasi paket decoy (JSON)
│   ├── decoy-default-{balance,qris,qris0}.json
│   └── decoy-prio-{balance,qris,qris0}.json
│
├── hot_data/                    # Data paket HOT (JSON)
│   ├── hot.json
│   └── hot2.json
```

---

## 4. Alur Eksekusi Aplikasi

`main.py` adalah titik masuk:

1. **Load `.env`** — `load_dotenv()`.
2. **Loop utama** — `main()` berjalan terus hingga keluar:
   - Ambil *active user* via `AuthInstance.get_active_user()`.
   - **Jika sudah login**: ambil saldo (`get_balance`), informasi tiering untuk PREPAID (`get_tiering_info`), tampilkan menu utama, lalu proses pilihan.
   - **Jika belum login**: masuk ke menu akun untuk memilih/menambah akun.

### Menu Utama (`show_main_menu`)

| Kode | Fungsi |
|---|---|
| `1` | Login / ganti akun (`show_account_menu`) |
| `2` | Lihat paket saya (`fetch_my_packages`) |
| `3` | Beli paket HOT (`show_hot_menu`) |
| `4` | Beli paket HOT-2 (`show_hot_menu2`) |
| `5` | Beli paket berdasarkan option code (`show_package_details`) |
| `6` | Lihat paket family (`get_packages_by_family`) |
| `7` | Beli semua paket di family (loop, `purchase_by_family`) |
| `8` | Riwayat transaksi (`show_transaction_history`) |
| `9` | Family Plan organizer (`show_family_info`) |
| `10` | Circle (`show_circle_info`) |
| `11` | Store segments (`show_store_segments_menu`) |
| `12` | Store family list (`show_family_list_menu`) |
| `13` | Store packages (`show_store_packages_menu`) |
| `14` | Redeemables (`show_redeemables_menu`) |
| `R` | Registrasi Dukcapil (`dukcapil`) |
| `V` | Validasi MSISDN (`validate_msisdn`) |
| `N` | Notifikasi (`show_notification_menu`) |
| `00` | Bookmark paket (`show_bookmark_menu`) |
| `99` | Keluar aplikasi |
| `t` | Shortcut testing (`pause`) |

---

## 5. Konfigurasi Lingkungan (`.env`)

Semua rahasia dan konfigurasi diambil dari environment variable. Template tersedia di `.env.template`. Aplikasi akan **gagal saat import** jika `BASE_API_URL` / `BASE_CIAM_URL` tidak diset.

| Variabel | Digunakan di | Keterangan |
|---|---|---|
| `BASE_API_URL` | `ahsiata.py`, `purchase/*` | Base URL API utama (contoh `https://xxx`) |
| `BASE_CIAM_URL` | `auth.py` | Base URL CIAM / OIDC provider |
| `BASIC_AUTH` | `auth.py` | Credential `Basic auth` (base64) untuk CIAM |
| `AX_FP_KEY` | `encrypt.py` | Kunci AES untuk fingerprint perangkat (32-hex ASCII) |
| `UA` | `ahsiata.py`, `auth.py`, `purchase/*` | User-Agent emulasi aplikasi |
| `API_KEY` | `encrypt.py`, `ahsiata.py` | `x-api-key` untuk API utama |
| `ENCRYPTED_FIELD_KEY` | `encrypt.py`, `crypto_helper.py` | Kunci AES untuk field terenkripsi & MSISDN Circle |
| `XDATA_KEY` | `crypto_helper.py` | Kunci AES untuk enkripsi body (`xdata`) |
| `AX_API_SIG_KEY` | `crypto_helper.py` | Kunci HMAC untuk `Ax-Api-Signature` |
| `X_API_BASE_SECRET` | `crypto_helper.py` | Secret dasar untuk semua `x-signature` |
| `CIRCLE_MSISDN_KEY` | *(template)* | Tercantum di template tapi **tidak dibaca** di kode (diganti `ENCRYPTED_FIELD_KEY`) |

> **Keamanan**: `X_API_BASE_SECRET`, `XDATA_KEY`, dan `BASIC_AUTH` adalah rahasia. Jangan commit nilai aslinya (`.env` sudah di-`.gitignore`).

---

## 6. Autentikasi & Manajemen Sesi

### 6.1 `ahsiata/api/auth.py` — CIAM / OIDC

Fungsi utama:

- **`validate_contact(contact)`** — Validasi nomor diawali `628`, panjang ≤ 14.
- **`get_otp(contact)`** — `GET /realms/xl-ciam/auth/otp?contact=...&contactType=SMS`. Mengirim OTP via SMS, mengembalikan `subscriber_id`. Header memuat `Ax-Device-Id`, `Ax-Fingerprint`, `Ax-Request-At`, `Ax-Request-Id`, `Ax-Substype: PREPAID`.
- **`extend_session(subscriber_id)`** — Memperpanjang sesi via `contactType=DEVICEID` (MSISDN di-*base64*). Mengembalikan `exchange_code`.
- **`submit_otp(api_key, contact_type, contact, code)`** — `POST /realms/xl-ciam/protocol/openid-connect/token` dengan `grant_type=password`. Mengirim OTP (SMS) atau exchange code (DEVICEID). Header memuat `Ax-Api-Signature` (dari `ax_api_signature`). Mengembalikan token OIDC `{access_token, id_token, refresh_token, ...}`.
- **`get_new_token(api_key, refresh_token, subscriber_id)`** — Flow *refresh token grant*:
  1. `POST .../token` dengan `grant_type=refresh_token`.
  2. Jika respons `400` + `error_description == "Session not active"`: memanggil `extend_session(subscriber_id)` lalu `submit_otp(..., "DEVICEID", subscriber_id, exchange_code)` untuk memperoleh token baru.
  3. Jika token tidak valid → `ValueError`.
- **`get_auth_code(tokens, pin, msisdn)`** — Membuat *authorization code* untuk transaksi *share balance* (`POST /ciam/auth/authorization-token/generate`). PIN di-*base64*. Kembali `authorization_code`.

### 6.2 `app/service/auth.py` — Singleton `Auth`

Menyimpan sesi aktif dan daftar refresh token.

**State (class-level)**:

- `api_key` — hardcode `"Noir1"` (placeholder, di-set di constructor `Auth.__init__`).
- `refresh_tokens` — daftar `{number, subscriber_id, subscription_type, refresh_token}`.
- `active_user` — `{number, subscriber_id, subscription_type, tokens}` dengan `tokens = {refresh_token, access_token, id_token}`.
- `last_refresh_time` — timestamp token terakhir di-refresh.

**Metode penting**:

| Metode | Peran |
|---|---|
| `load_tokens()` | Membaca `refresh-tokens.json`; hanya entry valid (`number` & `refresh_token`). |
| `add_refresh_token(number, refresh_token)` | Tambah/replace token; jika nomor baru, ambil profil via `get_profile` untuk `subscriber_id` & `subscription_type`; simpan file; set active user. |
| `remove_refresh_token(number)` | Hapus dari list; jika yang dihapus adalah akun aktif, otomatis pindah ke akun pertama yang tersisa. |
| `set_active_user(number)` | Tukar token (`get_new_token`), ambil profil, set `active_user`, simpan `active.number`. |
| `renew_active_user_token()` | Refresh token untuk akun aktif. |
| `get_active_user()` | Mengembalikan user aktif; **auto-renew setiap > 300 detik (5 menit)**. |
| `get_active_tokens()` | Helper → `active_user["tokens"]`. |
| `write_tokens_to_file()` / `write_active_number()` / `load_active_number()` | Persistensi ke `refresh-tokens.json` dan `active.number`. |

**Persistensi**:

- `refresh-tokens.json` — daftar token (indent 4).
- `active.number` — nomor akun aktif (plain text). Jika kosong, file dihapus.

### 6.3 `app/menus/account.py`

Alur login interaktif:

1. Input nomor (`628xxx`), validasi format.
2. `get_otp()` → kirim OTP.
3. Loop maksimal **5 percobaan** input OTP 6 digit → `submit_otp(api_key, "SMS", ...)`.
4. Token refresh disimpan via `AuthInstance.add_refresh_token()`.

Menu akun juga mendukung perpindahan akun, penambahan (`0`), dan penghapusan (`del <nomor>`) dengan proteksi akun aktif tidak bisa dihapus.

---

## 7. Protokol Komunikasi API

Semua panggilan API utama melewati **`send_api_request()`** di `app/client/ahsiata.py`:

1. **Enkripsi payload** — `encryptsign_xdata(api_key, method, path, id_token, payload)` menghasilkan:
   - `body = {"xdata": <AES-CBC urlsafe-b64>, "xtime": <ms>}`
   - `x_signature` (HMAC-SHA512).
2. **Header**:
   ```
   host                : BASE_API_URL tanpa skema
   content-type        : application/json; charset=utf-8
   user-agent          : UA
   x-api-key           : API_KEY
   authorization       : Bearer <id_token>
   x-hv                : v3
   x-signature-time    : xtime // 1000 (detik)
   x-signature         : x_signature
   x-request-id        : uuid4
   x-request-at        : timestamp gaya Java (java_like_timestamp)
   x-version-app       : 8.9.0
   ```
3. **Request** — `POST {BASE_API_URL}/{path}` dengan body JSON terenkripsi, timeout 30 detik.
4. **Dekripsi respons** — `decrypt_xdata(api_key, json.loads(resp.text))` → dict Python. Jika gagal, mengembalikan raw text respons.

`BASE_API_URL` dan `UA` di-import dari `ahsiata.py` oleh modul payment (mis. `balance.py`).

---

## 8. Kriptografi & Penandaan (Signing)

Implementasi inti ada di **`app/service/crypto_helper.py`**; wrapper untuk aplikasi ada di **`app/client/encrypt.py`**.

### 8.1 Enkripsi body (`xdata`)

```
IV   = SHA256(str(xtime_ms)) hexdigest → ambil 16 byte pertama (ASCII hex)
Key  = XDATA_KEY (ASCII)
Cipher = AES-CBC (AES-256), padding PKCS7
Output = urlsafe_base64(encrypted)
```

- `encrypt_xdata(plaintext, xtime_ms)` dan `decrypt_xdata(xdata, xtime_ms)`.

### 8.2 `x-signature` (API utama)

```
key = f"{X_API_BASE_SECRET};{id_token};{method};{path};{sig_time_sec}"
msg = f"{id_token};{sig_time_sec};"
sig = HMAC-SHA512(key, msg).hexdigest()
```

- `make_x_signature(id_token, method, path, sig_time_sec)`.

### 8.3 `x-signature` khusus (payment / loyalty / bounty)

- `make_x_signature_payment(...)` — `key = f"{X_API_BASE_SECRET};{sig_time_sec}#ae-hei_9Tee6he+Ik3Gais5=;POST;{path};{sig_time_sec}"`, `msg = f"{access_token};{token_payment};{sig_time_sec};{payment_for};{payment_method};{package_code};"`.
- `make_x_signature_bounty(...)` — path fixed `api/v8/personalization/bounties-exchange`.
- `make_x_signature_loyalty(...)` — `msg = f"{token_confirmation};{sig_time_sec};{package_code};"`.
- `make_x_signature_bounty_allotment(...)` — menyisipkan `destination_msisdn` ke dalam key.
- `make_x_signature_basic(method, path, sig_time_sec)` — variant sederhana (belum banyak dipakai).

### 8.4 `Ax-Api-Signature` (CIAM)

```
key     = AX_API_SIG_KEY (ASCII)
preimage = f"{ts_for_sign}password{contact_type}{contact}{code}openid"
sig     = base64(HMAC-SHA256(key, preimage))
```

- `make_ax_api_signature(ts_for_sign, contact, code, contact_type)`.

### 8.5 Fingerprint perangkat (`ax.fp`)

`app/client/encrypt.py`:

- `build_fingerprint_plain(DeviceInfo)` — string `manufacturer|model|lang|resolution|tz_short|ip|font_scale|Android <ver>|msisdn`.
- `ax_fingerprint(dev, secret_key_32hex_ascii)` — AES-CBC (IV = 16 byte `\x00`), hasil base64.
- `load_ax_fp()` — membaca `ax.fp`; jika tidak ada/empty, generate dengan `DeviceInfo` acak (manufacturer `samsung####`, model `SM-N93####`, dst.) lalu simpan ke `ax.fp`.
- `ax_device_id()` — `MD5(ax.fp)`.

### 8.6 Field terenkripsi & MSISDN Circle

- `build_encrypted_field(iv_hex16=None, urlsafe_b64=False)` — mengenkripsi string kosong (di-pad) dengan `ENCRYPTED_FIELD_KEY`; hasil `b64(ct) + iv_hex`. Dipakai untuk `encrypted_payment_token` dan `encrypted_authentication_id`.
- `encrypt_circle_msisdn(msisdn)` / `decrypt_circle_msisdn(encrypted_b64)` — format `urlsafe_b64(ct) + iv_hex16`; IV diambil dari 16 karakter terakhir, sisanya ciphertext b64.

### 8.7 Utilitas waktu

- `java_like_timestamp(now)` — `YYYY-MM-DDTHH:MM:SS.cc+TZ:OFF` (2 digit centisecond).
- `ts_gmt7_without_colon(dt)` — timestamp GMT+7 dengan millis, tanpa colon pada offset.

---

## 9. Lapisan Klien (Client Layer)

### 9.1 `app/client/ahsiata.py` — Klien utama

Endpoint yang di-wrap (semuanya `POST`):

| Fungsi | Path | Keterangan |
|---|---|---|
| `get_profile` | `api/v8/profile` | Data profil + `subscriber_id`, `subscription_type` |
| `get_balance` | `api/v8/packages/balance-and-credit` | Saldo & masa aktif |
| `get_family` | `api/v8/xl-stores/options/list` | Detail family (brute-force kombinasi `is_enterprise` × `migration_type`) |
| `get_families` | `api/v8/xl-stores/families` | Daftar family per kategori |
| `get_package` | `api/v8/xl-stores/options/detail` | Detail option code |
| `get_addons` | `api/v8/xl-stores/options/addons-pinky-box` | Addon/bonus paket |
| `intercept_page` | `misc/api/v8/utility/intercept-page` | Hit intercept sebelum pembelian |
| `login_info` | `api/v8/auth/login` | Info login |
| `get_package_details` | (komposisi) | Family → variant → option → detail paket |
| `get_notifications` | `api/v8/notification-non-grouping` | Daftar notifikasi |
| `get_notification_detail` | `api/v8/notification/detail` | Detail notifikasi |
| `get_pending_transaction` | `api/v8/profile` | (TODO belum diimplementasi penuh) |
| `get_transaction_history` | `payments/api/v8/transaction-history` | Riwayat transaksi |
| `get_tiering_info` | `gamification/api/v8/loyalties/tiering/info` | Poin & tier |
| `unsubscribe` | `api/v8/packages/unsubscribe` | Berhenti berlangganan paket |
| `dashboard_segments` | `dashboard/api/v8/segments` | Segmen dashboard (dipakai notifikasi) |

`get_family` melakukan iterasi semua kombinasi `is_enterprise ∈ {False, True}` dan `migration_type ∈ {NONE, PRE_TO_PRIOH, PRIOH_TO_PRIO, PRIO_TO_PRIOH}` hingga mendapat respons dengan nama family non-kosong.

### 9.2 `app/client/famplan.py` — Family Plan

| Fungsi | Path | Keterangan |
|---|---|---|
| `get_family_data` | `sharings/api/v8/family-plan/member-info` | Info plan & anggota |
| `validate_msisdn` | `api/v8/auth/check-dukcapil` | Validasi MSISDN (bizon, optimus, dll.) |
| `change_member` | `sharings/api/v8/family-plan/change-member` | Assign nomor ke slot |
| `remove_member` | `sharings/api/v8/family-plan/remove-member` | Hapus anggota |
| `set_quota_limit` | `sharings/api/v8/family-plan/allocate-quota` | Alokasi kuota per anggota |

### 9.3 `app/client/circle.py` — Circle / Family Hub

| Fungsi | Path |
|---|---|
| `get_group_data` | `family-hub/api/v8/groups/status` |
| `get_group_members` | `family-hub/api/v8/members/info` |
| `validate_circle_member` | `family-hub/api/v8/members/validate` |
| `invite_circle_member` | `family-hub/api/v8/members/invite` |
| `remove_circle_member` | `family-hub/api/v8/members/remove` |
| `accept_circle_invitation` | `family-hub/api/v8/groups/accept-invitation` |
| `create_circle` | `family-hub/api/v8/groups/create` |
| `spending_tracker` | `gamification/api/v8/family-hub/spending-tracker` |
| `get_bonus_data` | `gamification/api/v8/family-hub/bonus/list` |

Catatan: MSISDN pada payload Circle dienkripsi dengan `encrypt_circle_msisdn`.

### 9.4 `app/client/registration.py`

- `validate_puk(api_key, msisdn, puk)` — `api/v8/infos/validate-puk`.
- `dukcapil(api_key, msisdn, kk, nik)` — `api/v8/auth/regist/dukcapil`.

### 9.5 `app/client/store/` — Katalog

| Modul | Fungsi | Path |
|---|---|---|
| `segments.py` | `get_segments` | `api/v8/configs/store/segments` |
| `search.py` | `get_family_list` | `api/v8/xl-stores/options/search/family-list` |
| `search.py` | `get_store_packages` | `api/v9/xl-stores/options/search` |
| `redeemables.py` | `get_redeemables` | `api/v8/personalization/redeemables` |

### 9.6 `app/client/purchase/` — Settlement (lihat juga §12)

| Modul | Fungsi |
|---|---|
| `common.py` | `get_payment_methods` — ambil metode pembayaran (`payments/api/v8/payment-methods-option`) |
| `balance.py` | `settlement_balance` — settlement via saldo |
| `qris.py` | `settlement_qris`, `get_qris_code`, `show_qris_payment` |
| `ewallet.py` | `settlement_multipayment`, `show_multipayment` |
| `redeem.py` | `settlement_bounty`, `settlement_loyalty`, `bounty_allotment` |

---

## 10. Lapisan Menu (UI Layer)

Semua modul `app/menus/*` adalah fungsi interaktif berbasis `print()` + `input()`.

### 10.1 `app/menus/util.py`

| Fungsi | Peran |
|---|---|
| `clear_screen()` | Bersihkan terminal + render ASCII art logo |
| `pause()` | `input("Press enter to continue...")` |
| `display_html(html_text, width)` | Konversi HTML (mis. T&C paket) ke teks rata kiri |
| `format_quota_byte(byte)` | Format byte → `GB`/`MB`/`KB`/`B` |

`HTMLToText` adalah parser berbasis `HTMLParser` — tag `<li>` dijadikan bullet `- `, `<br>` menjadi newline, baris di-wrap per `width`.

### 10.2 `app/menus/package.py`

Fungsi utama:

- **`show_package_details(api_key, tokens, package_option_code, is_enterprise, option_order=-1)`** — Menu detail paket: nama, harga, masa aktif, poin, plan type, benefits (kuota/menit/SMS), addons, T&C. Opsi pembelian:
  - `1` Pulsa (balance)
  - `2` E-Wallet
  - `3` QRIS
  - `4` Pulsa + Decoy (v1)
  - `5` Pulsa + Decoy V2 (token confirmation dari decoy)
  - `6` QRIS + Decoy (+1K)
  - `7` QRIS + Decoy V2 (Rp0)
  - `8` Pulsa N kali
  - `0` Tambah bookmark (hanya jika `option_order != -1`)
  - `B` Ambil sebagai bonus (bounty), `BA` Kirim bonus (allotment), `L` Beli dengan poin (loyalty) — hanya tampil jika `payment_for == "REDEEM_VOUCHER"`.
- **`get_packages_by_family(family_code, is_enterprise=None, migration_type=None)`** — Tampilkan semua variant & option dalam family; pilih nomor → `show_package_details`.
- **`fetch_my_packages()`** — `api/v8/packages/quota-details` → daftar kuota aktif, detail per paket, dan opsi `del <no>` untuk unsubscribe.

### 10.3 `app/menus/purchase.py`

- **`purchase_by_family(family_code, use_decoy, pause_on_success, delay_seconds, start_from_option)`** — Loop membeli **semua** option dalam family. Menyusun `PaymentItem` (dengan nama di-prefix angka acak `randint(1000,9999)`), melakukan `settlement_balance` dengan `overwrite_amount`; menangani error `Bizz-err.Amount.Total` (adjust amount). Laporan sukses di akhir.
- **`purchase_n_times(n, family_code, variant_code, option_order, ...)`** — Beli satu option N kali.
- **`purchase_n_times_by_option_code(n, option_code, ...)`** — Beli option (langsung via option code) N kali.

### 10.4 `app/menus/payment.py`

- `show_transaction_history(api_key, tokens)` — Tampilkan riwayat (`get_transaction_history`), format waktu Jakarta (`-7 jam`).

### 10.5 `app/menus/hot.py`

- `show_hot_menu()` — Membaca `hot_data/hot.json`, menampilkan daftar, memilih → resolve option code via `get_family` → `show_package_details`.
- `show_hot_menu2()` — Membaca `hot_data/hot2.json` (paket *bundle* multi-item), memuat detail setiap item → menyusun `payment_items` → menu pembayaran (1. Balance, 2. E-Wallet, 3. QRIS).

### 10.6 `app/menus/bookmark.py`

- `show_bookmark_menu()` — List bookmark; pilih → resolve option code → `show_package_details`. Dukungan hapus (`000`).

### 10.7 `app/menus/famplan.py`

- `show_family_info(api_key, tokens)` — Info plan (parent, total kuota, anggota), dengan opsi:
  - `1` Change member (validasi MSISDN → cek `family_plan_role == "NO_ROLE"` → `change_member`)
  - `limit <slot> <MB>` → `set_quota_limit`
  - `del <slot>` → `remove_member`
  - `00` Kembali.

### 10.8 `app/menus/circle.py`

- `show_circle_info(api_key, tokens)` — Tampilkan grup Circle, anggota (MSISDN didekripsi), kuota, spending tracker, dengan opsi:
  - `1` Invite member (validasi + `invite_circle_member`)
  - `del <no>` Remove member (proteksi parent & last member)
  - `acc <no>` Accept invitation
  - `2` Bonus list (`show_bonus_list`, action `PLP`/`PDP`).
- `show_circle_creation(...)` — Membuat Circle baru.

### 10.9 `app/menus/notification.py`

- `show_notification_menu()` — Mengambil notifikasi dari `dashboard_segments`, menampilkan status READ/UNREAD, dan opsi `1` untuk menandai semua unread via `get_notification_detail`.

### 10.10 `app/menus/store/`

- `segments.py::show_store_segments_menu` — Segmen store → pilih `A1`, `B2`, dst. → action `PDP` → detail paket.
- `search.py::show_family_list_menu` — Family list → pilih nomor → `get_packages_by_family`.
- `search.py::show_store_packages_menu` — Paket store (hasil `results_price_only`) → action `PDP`.
- `redemables.py::show_redeemables_menu` — Redeemables per kategori → action `PLP`/`PDP`. (Perhatikan: nama file ini **salah eja** — `redemables` bukan `redeemables` — sesuai codebase aslinya.)

### 10.11 `app/menus/family.py`

File **kosong** (placeholder). Tidak ada fungsi.

---

## 11. Lapisan Layanan (Service Layer)

### 11.1 `app/service/decoy.py` — Paket Decoy (lihat §13)

### 11.2 `app/service/bookmark.py` — Singleton `Bookmark`

- File: `bookmark.json`.
- Skema item: `{family_name, family_code, is_enterprise, variant_name, option_name, order}`.
- `add_bookmark(...)` — dedup berdasarkan `(family_code, variant_name, order)`.
- `remove_bookmark(...)`, `get_bookmarks()`.
- `_ensure_schema()` — migrasi otomatis field `family_name` & `order` untuk kompatibilitas.

---

## 12. Alur Pembelian & Metode Pembayaran

Struktur kontrak item pembelian (`app/type_dict.py`):

```python
class PaymentItem(TypedDict):
    item_code: str
    product_type: str
    item_price: int
    item_name: str
    tax: int
    token_confirmation: str
```

### 12.1 Balance / Pulsa (`purchase/balance.py`)

Alur `settlement_balance(api_key, tokens, items, payment_for, ask_overwrite, ...)`:

1. Validasi `overwrite_amount` / `ask_overwrite`.
2. Bangun `payment_targets` (item codes dipisah `;`).
3. `intercept_page(...)` — hit intercept.
4. `payments/api/v8/payment-methods-option` → `token_payment` + `timestamp` (dipakai untuk `x-signature` payment).
5. `POST payments/api/v8/settlement-multipayment` dengan `payment_method: "BALANCE"`, `total_amount`, `items`, field terenkripsi (`encrypted_payment_token`, `encrypted_authentication_id`), `additional_data` detail.
6. Header signature via `get_x_signature_payment`.
7. Dekripsi respons; sukses jika `status == "SUCCESS"`.

### 12.2 QRIS (`purchase/qris.py`)

- `settlement_qris(...)` → `POST payments/api/v8/settlement-multipayment/qris` (payload mirip balance, `payment_method: "QRIS"`, `verification_token: token_payment`). Mengembalikan `transaction_code`.
- `get_qris_code(api_key, tokens, transaction_id)` → `payments/api/v8/pending-detail` → `qr_code`.
- `show_qris_payment(...)` — render QR di terminal (`qrcode.print_ascii`) dan mencetak URL viewer `https://ki-ar-kod.netlify.app/?data=<b64>`.

### 12.3 E-Wallet (`purchase/ewallet.py`)

- `settlement_multipayment(...)` → `POST payments/api/v8/settlement-multipayment/ewallet` dengan `payment_method` salah satu dari `DANA`, `SHOPEEPAY`, `GOPAY`, `OVO` dan `wallet_number`.
- `show_multipayment(...)` — menu pilihan wallet; DANA/OVO meminta nomor wallet (validasi format `08...`); hasil settlement → tampilkan `deeplink` (kecuali OVO).

### 12.4 Redeem Bounty / Loyalty (`purchase/redeem.py`)

- `settlement_bounty(...)` — `POST api/v8/personalization/bounties-exchange`, `payment_for: "REDEEM_VOUCHER"`, `payment_method: "BALANCE"`. Signature via `get_x_signature_bounty`.
- `settlement_loyalty(...)` — `POST gamification/api/v8/loyalties/tiering/exchange` (bayar dengan poin). Signature via `get_x_signature_loyalty`.
- `bounty_allotment(...)` — `POST gamification/api/v8/loyalties/tiering/bounties-allotment` (kirim bonus ke MSISDN tujuan). Signature via `get_x_signature_bounty_allotment`.

---

## 13. Paket Decoy

**Konsep**: menambahkan paket "decoy" (paket penambah dummy) ke dalam keranjang pembayaran sehingga nilai `total_amount` dapat diubah untuk memengaruhi hasil settlement.

### `app/service/decoy.py` — Singleton `DecoyPackage`

- **State**: `decoys` dict dengan kunci `{default,prio}-{balance,qris,qris0}`; setiap entry `{option_code, price, last_fetched_at}`.
- **Sumber data**: `decoy_data/decoy-<name>.json` berisi `{family_name, family_code, is_enterprise, migration_type, variant_code, option_name, order, price}`.
- **`check_subscriber_change()`** — jika `subscriber_id` berubah, reset decoy; pilih prefix:
  - `prio-` bila `subscription_type ∈ {PRIORITAS, PRIOHYBRID, GO}`
  - `default-` selain itu.
- **`fetch_decoy_data(decoy_name)`** — baca JSON lokal → `get_package_details(...)` → simpan `option_code`, `last_fetched_at`.
- **`get_decoy(payment_type)`** — return decoy; **refresh otomatis jika `last_fetched_at` > 300 detik**.

### Penggunaan dalam pembelian

- Balance + Decoy (`choice 4/5`): `overwrite_amount = harga_paket + harga_decoy`; jika server membalas `Bizz-err.Amount.Total=<angka>`, ulangi dengan `overwrite_amount = <angka>` tersebut.
- QRIS + Decoy (`choice 6/7`): `payment_for = "SHARE_PACKAGE"`, `token_confirmation_idx = 1`, harga decoy ditambahkan ke item; user mengatur ulang amount.

---

## 14. Bookmark Paket

Disimpan di `bookmark.json` sebagai array objek. Field:

| Field | Tipe | Keterangan |
|---|---|---|
| `family_name` | str | Nama family (migrasi otomatis) |
| `family_code` | str | UUID family |
| `is_enterprise` | bool | Tipe store |
| `variant_name` | str | Nama variant |
| `option_name` | str | Nama option |
| `order` | int | Urutan option dalam variant (migrasi otomatis) |

Saat memilih bookmark, aplikasi me-resolve family (`get_family`) lalu mencari `option_code` berdasarkan `variant_name` + `order` sebelum menampilkan detail.

---

## 15. Paket HOT

Dua sumber data lokal:

- **`hot_data/hot.json`** — array `{family_name, family_code, is_enterprise, variant_name, option_name, order}`. Dipakai menu HOT (menu `3`).
- **`hot_data/hot2.json`** — array *bundle* multi-paket:
  ```json
  {
    "name": "...",
    "price": "Rp...",
    "detail": "...",
    "packages": [ {family_name, family_code, is_enterprise, migration_type, variant_code, option_name, order}, ... ],
    "payment_for": "BUY_PACKAGE | SHARE_PACKAGE",
    "ask_overwrite": false,
    "overwrite_amount": 0,
    "token_confirmation_idx": 0,
    "amount_idx": -1
  }
  ```
  Dipakai menu HOT-2 (menu `4`). Setiap paket di-resolve via `get_package_details`; hasil dijadikan `PaymentItem`.

---

## 16. Data Files

| File | Dibuat otomatis? | Isi |
|---|---|---|
| `.env` | Manual (dari `.env.template`) | Variabel lingkungan rahasia |
| `refresh-tokens.json` | Ya | Daftar refresh token pengguna |
| `active.number` | Ya | Nomor akun aktif |
| `ax.fp` | Ya | Fingerprint perangkat AES |
| `bookmark.json` | Ya | Daftar bookmark |
| `decoy_data/*.json` | Tidak | Konfigurasi paket decoy |
| `hot_data/*.json` | Tidak | Data paket HOT |

### Skema `decoy_data/*.json`

```json
{
  "family_name": "XL PASS",
  "family_code": "<uuid>",
  "is_enterprise": false,
  "migration_type": "NONE",
  "variant_code": "<uuid>",
  "option_name": "XL PASS 20 Days",
  "order": 1,
  "price": 800000
}
```

---

## 17. Dependensi

Dari `requirements.txt`:

| Paket | Versi | Peran |
|---|---|---|
| `Brotli` | 1.1.0 | Dekompresi respons (Accept-Encoding br) |
| `certifi` | 2025.8.3 | CA bundle requests |
| `charset-normalizer` | 3.4.3 | Normalisasi charset |
| `idna` | 3.10 | IDNA encoding |
| `pycryptodome` | 3.23.0 | AES, HMAC, padding (kriptografi) |
| `requests` | 2.32.5 | HTTP client |
| `urllib3` | 2.5.0 | HTTP engine |
| `qrcode` | 8.2 | Render QRIS di terminal |
| `python-dotenv` | 1.1.1 | Load `.env` |

---

## 18. Setup & Menjalankan

### Linux (Debian/Ubuntu, Fedora, Arch)

```bash
git clone https://github.com/purplemashu/Ah-Si-Ata
cd Ah-Si-Ata
bash setup.sh          # install deps sistem + venv + pip install
source venv/bin/activate
python main.py
```

`setup.sh` mendeteksi package manager (`apt-get`, `dnf`, `pacman`), membuat virtualenv `venv/`, dan install `requirements.txt`.

### Persiapan `.env`

1. Buat file `.env` (contoh dari `.env.template`).
2. Isi `BASE_API_URL`, `BASE_CIAM_URL`, `BASIC_AUTH`, `AX_FP_KEY`, `UA`, `API_KEY`, `ENCRYPTED_FIELD_KEY`, `XDATA_KEY`, `AX_API_SIG_KEY`, `X_API_BASE_SECRET`.

> Tanpa `BASE_API_URL` dan `BASE_CIAM_URL`, program akan `raise ValueError` saat import.

---

## 19. Catatan Pengembangan

- **`CIRCLE_MSISDN_KEY`** ada di `.env.template` tapi tidak dipakai; enkripsi MSISDN Circle memakai `ENCRYPTED_FIELD_KEY`.
- **`get_pending_transaction`** (`ahsiata.py`) berlabel `@TODO: implement this function properly`.
- **Bonus otomatis** di `show_package_details` (penambahan `bonuses` ke `payment_items`) sengaja di-comment — perlu pengujian lebih lanjut.
- **Versi aplikasi** yang di-emulasi: `x-version-app: 8.9.0`; model perangkat emulasi: `SM-N935F` (Samsung).
- **`show_hot_menu2`** bergantung pada data lokal `hot2.json`; jika struktur server berubah, `get_package_details` dapat gagal dan pembelian dibatalkan.
- Error `Bizz-err.Amount.Total=<angka>` adalah mekanisme server untuk mengoreksi jumlah; kode mengekstrak `<angka>` dan mengulang settlement.

---

*Dokumen ini dihasilkan dari analisis langsung terhadap source code pada branch `main` (commit terkini di repo lokal). Perilaku dapat berubah seiring update repository.*