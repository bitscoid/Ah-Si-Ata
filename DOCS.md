# Dokumentasi Teknis — Ah-Si-Ata

Dokumen ini berisi dokumentasi teknis untuk seluruh codebase `Ah-Si-Ata`. Dokumentasi mencakup arsitektur, struktur direktori, alur autentikasi, protokol komunikasi API, kriptografi, alur pembelian, serta deskripsi setiap modul dan file pendukung.

> **Catatan**: Proyek ini adalah CLI client untuk salah satu penyedia layanan internet seluler Indonesia. Konten yang ada di sini murni untuk tujuan dokumentasi teknis. Seluruh pengguna bertanggung jawab atas kepatuhan terhadap hukum dan ketentuan yang berlaku.

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
┌────────────────────────────────────────────────┐
│  entry points: main.py (thin wrapper),          │
│  python -m ahsiata, console script `ahsiata`    │
│  → semuanya memanggil ahsiata.cli.main()        │
└───────────────────┬────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────┐
│         ahsiata/ui/  (UI / presentasi)          │
│   Menampilkan menu, membaca input,              │
│   memformat output (ASCII, HTML→text)           │
└───────────────────┬────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────┐
│         ahsiata/api/  (API client layer)        │
│   Memanggil endpoint, menyusun payload,         │
│   enkripsi/signature, parsing respons           │
└───────────────────┬────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────┐
│        ahsiata/core/  (service layer)           │
│   State: session, bookmark, decoy,              │
│   kriptografi inti                              │
└────────────────────────────────────────────────┘
```

Pola desain yang digunakan:

| Pola | Penerapan |
|---|---|
| **Singleton** | `Session` (`ahsiata/core/session.py`, instance `SESSION`), `Bookmark` (`ahsiata/core/bookmark.py`, instance `BOOKMARK`), `DecoyPackage` (`ahsiata/core/decoy.py`, instance `DECOY`) — semuanya memakai `__new__` + flag `_initialized_` |
| **Facade / Gateway** | `ahsiata/api/client.py` — titik masuk `send_api_request()` / `post_encrypted()` untuk semua panggilan API utama |
| **TypedDict** | `ahsiata/type_dict.py` — kontrak struktur data `PaymentItem` |
| **Helper module** | `ahsiata/core/crypto.py` — primitif kripto murni; wrapper aplikasi di `ahsiata/api/encrypt.py` (re-export + helper fingerprint/waktu) |

---

## 3. Struktur Direktori

```
Ah-Si-Ata/
├── main.py                      # Thin wrapper → ahsiata.cli.main (jalur lama `python main.py`)
├── pyproject.toml               # Packaging; [project.scripts] ahsiata = "ahsiata.cli:main"
├── ahsiata/                     # Paket utama
│   ├── __init__.py
│   ├── __main__.py              # `python -m ahsiata` → ahsiata.cli.main()
│   ├── cli.py                   # main() (initialize SESSION/BOOKMARK) + loop menu
│   ├── config.py                # load_dotenv() + CONFIG (frozen dataclass, dibaca saat import)
│   ├── constants.py             # Endpoint, CIAMEndpoint, MigrationType, PaymentMethod,
│   │                            # PaymentFor, HttpHeader, CIAMHeader, LANG_EN
│   ├── type_dict.py             # PaymentItem (TypedDict)
│   │
│   ├── core/                    # Lapisan layanan / state
│   │   ├── crypto.py            # Primitif kripto: xdata AES-CBC, HMAC signature,
│   │   │                        #   encrypted-field / circle-msisdn, ax-api-signature
│   │   ├── session.py           # Singleton SESSION (sesi & token, refresh-tokens.json)
│   │   ├── bookmark.py          # Singleton BOOKMARK (bookmark.json)
│   │   └── decoy.py             # Singleton DECOY / DecoyPackage
│   │
│   ├── api/                     # Lapisan klien API
│   │   ├── client.py            # HTTP rendah: requests.Session + retry, build_headers,
│   │   │                        #   post_encrypted, send_api_request, get_balance, intercept_page
│   │   ├── encrypt.py           # Fingerprint (ax.fp), encrypted-field, timestamp,
│   │   │                        #   encryptsign_xdata, decrypt_xdata (wrapper)
│   │   ├── auth.py              # CIAM OIDC: get_otp, submit_otp, extend_session, get_new_token
│   │   ├── profile.py           # get_profile, get_tiering_info
│   │   ├── packages.py          # get_family, get_package, get_addons, get_package_details, unsubscribe
│   │   ├── catalog.py           # get_segments, get_family_list, get_store_packages, get_redeemables
│   │   ├── notifications.py     # get_notifications, get_notification_detail
│   │   ├── transactions.py      # get_transaction_history
│   │   ├── family_plan.py       # Family Plan API
│   │   ├── circle.py            # Circle / Family Hub API
│   │   ├── registration.py      # Registrasi dukcapil
│   │   ├── purchase/            # Settlement pembelian
│   │   │   ├── base.py          # resolve_amount, join_item_codes, fetch_payment_token,
│   │   │   │                    #   post_signed_payload, factory signature
│   │   │   ├── balance.py       # settlement_balance, append_decoy_item, settle_with_decoy
│   │   │   ├── qris.py          # settlement_qris, get_qris_code, show_qris_payment
│   │   │   ├── ewallet.py       # settlement_multipayment, show_multipayment
│   │   │   └── redeem.py        # settlement_bounty, settlement_loyalty, bounty_allotment
│   │   └── store/               # Hanya __init__.py (fungsi store ada di catalog.py)
│   │
│   └── ui/                      # Lapisan UI (print + input, teks Bahasa Indonesia)
│       ├── utils.py             # clear_screen, pause, display_html, format_quota_byte
│       ├── account.py           # Login / kelola akun
│       ├── bookmark.py          # Menu bookmark
│       ├── hot.py               # Paket HOT & HOT-2
│       ├── notification.py      # Menu notifikasi
│       ├── payment.py           # Riwayat transaksi
│       ├── family_plan.py       # Menu Family Plan
│       ├── package/
│       │   ├── details.py       # show_package_details, fetch_my_packages
│       │   └── list.py          # get_packages_by_family
│       ├── purchase/
│       │   ├── loop.py          # purchase_by_family
│       │   └── single.py        # purchase_n_times_by_option_code
│       ├── circle/
│       │   └── info.py          # show_circle_info, show_circle_creation
│       └── store/
│           ├── segments.py      # show_store_segments_menu
│           ├── search.py        # show_family_list_menu, show_store_packages_menu
│           └── redeemables.py   # show_redeemables_menu

├── requirements.txt             # Dependensi Python (5 paket langsung, versi di-pin)
├── setup.sh                     # Script setup Linux (system deps + venv + pip install)
├── Makefile                     # make setup / make run / make install / make env
├── README.md                    # Panduan pengguna
├── .env                         # Variabel lingkungan (rahasia, tidak di-commit)
├── .env.template                # Template variabel lingkungan
├── .gitignore
├── ax.fp                        # Fingerprint perangkat (dihasilkan otomatis)
├── active.number                # Nomor akun aktif (dihasilkan otomatis)
├── refresh-tokens.json          # Penyimpanan refresh token (dihasilkan otomatis)
├── bookmark.json                # Bookmark paket (dihasilkan otomatis)
│
├── decoy_data/                  # Konfigurasi paket decoy (JSON, 7 file)
│   ├── decoy-default-{balance,qris,qris0}.json
│   ├── decoy-prio-{balance,qris,qris0}.json
│   └── decoy-default-pass20.json  # Tidak dipakai kode (hanya 6 nama decoy yang dikelola)
│
├── hot_data/                    # Data paket HOT (JSON)
│   ├── hot.json
│   └── hot2.json
│
└── tests/                       # Tes offline (stdlib unittest)
    └── test_crypto.py
```

---

## 4. Alur Eksekusi Aplikasi

Aplikasi dapat diluncurkan lewat tiga cara yang setara — semuanya memanggil `ahsiata.cli.main()`:

- `python main.py` (thin wrapper agar jalur lama tetap jalan).
- `python -m ahsiata` (via `ahsiata/__main__.py`).
- Console script `ahsiata` (via `pyproject.toml` → `[project.scripts] ahsiata = "ahsiata.cli:main"`, setelah `pip install .`).

Alur `main()` (`ahsiata/cli.py`):

1. **`SESSION.initialize()`** — baca `refresh-tokens.json` + `active.number` dari CWD (buat file kosong jika belum ada). **`BOOKMARK.initialize()`** — baca `bookmark.json`. (Keduanya tidak menyentuh disk saat import; inisialisasi hanya di entry point.)
2. **Loop utama** — `_run()` berjalan terus hingga keluar:
   - Ambil *active user* via `SESSION.get_active_user()`.
   - **Jika sudah login**: ambil saldo (`get_balance`), informasi tiering untuk PREPAID (`get_tiering_info`), tampilkan menu utama, lalu proses pilihan.
   - **Jika belum login**: masuk ke menu akun (`show_account_menu`) untuk memilih/menambah akun; jika ada akun terpilih, `SESSION.set_active_user()`.

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

Semua rahasia dan konfigurasi diambil dari environment variable. `load_dotenv()` dipanggil **saat import `ahsiata/config.py`** (mencari `.env` dari CWD ke atas). Semua nilai dibaca sekali menjadi `CONFIG` — dataclass `frozen` — saat import. Variabel REQUIRED (10) yang tidak diset memicu `ValueError(f"{name} environment variable not set")` segera; variabel OPTIONAL memakai default yang terdokumentasi di kode.

| Variabel | Wajib? | Dipakai di | Keterangan |
|---|---|---|---|
| `BASE_API_URL` | Ya | `client.py` | Base URL API utama (`https://...`) |
| `BASE_CIAM_URL` | Ya | `auth.py` | Base URL CIAM / OIDC provider |
| `BASIC_AUTH` | Ya | `auth.py` | Credential `Basic auth` (base64) untuk CIAM |
| `AX_FP_KEY` | Ya | `encrypt.py` | Kunci AES untuk fingerprint perangkat (32-hex ASCII) |
| `UA` | Ya | `client.py`, `auth.py` | User-Agent emulasi aplikasi |
| `API_KEY` | Ya | `client.py`, `session.py` | `x-api-key` untuk API utama |
| `ENCRYPTED_FIELD_KEY` | Ya | `encrypt.py`, `core/crypto.py` | Kunci AES untuk field terenkripsi & MSISDN Circle |
| `XDATA_KEY` | Ya | `core/crypto.py` | Kunci AES untuk enkripsi body (`xdata`) |
| `AX_API_SIG_KEY` | Ya | `core/crypto.py` | Kunci HMAC untuk `Ax-Api-Signature` |
| `X_API_BASE_SECRET` | Ya | `core/crypto.py` | Secret dasar untuk semua `x-signature` |
| `PAYMENT_SIGN_SALT` | Tidak | `core/crypto.py` | Salt dalam HMAC key payment/bounty/loyalty (default `ae-hei_9Tee6he+Ik3Gais5=`) |
| `DEVICE_MANUFACTURER` | Tidak | `auth.py` | Header CIAM `Ax-Request-Device` (default `samsung`) |
| `DEVICE_MODEL` | Tidak | `auth.py` | Header CIAM `Ax-Request-Device-Model` (default `SM-N935F`) |
| `DEVICE_FAKE_MSISDN` | Tidak | `encrypt.py` | MSISDN fallback untuk fingerprint pertama (default `6281398370564`) |
| `APP_VERSION` | Tidak | `client.py`, `profile.py` | `x-version-app` (default `8.9.0`) |
| `X_HV` | Tidak | `client.py` | `x-hv` header (default `v3`) |
| `DEFAULT_SUBSTYPE` | Tidak | `auth.py` | `Ax-Substype` pra-login (default `PREPAID`) |
| `TOKEN_REFRESH_INTERVAL` | Tidak | `core/session.py` | Detik antar rotasi token otomatis (default `300`) |

> **Keamanan**: `X_API_BASE_SECRET`, `XDATA_KEY`, dan `BASIC_AUTH` adalah rahasia. Jangan commit nilai aslinya (`.env` sudah di-`.gitignore`).

---

## 6. Autentikasi & Manajemen Sesi

### 6.1 `ahsiata/api/auth.py` — CIAM / OIDC

Fungsi utama:

- **`validate_contact(contact)`** — Validasi nomor diawali `628`, panjang ≤ 14.
- **`get_otp(contact)`** — `GET /realms/xl-ciam/auth/otp?contact=...&contactType=SMS&alternateContact=false`. Mengirim OTP via SMS, mengembalikan `subscriber_id` (atau `None`). Header memuat `Accept-Encoding: gzip, deflate, br`, `Ax-Device-Id`, `Ax-Fingerprint`, `Ax-Request-At`, `Ax-Request-Device`, `Ax-Request-Device-Model`, `Ax-Request-Id`, `Ax-Substype: PREPAID` (dari `DEFAULT_SUBSTYPE`), `Authorization: Basic <BASIC_AUTH>`.
- **`extend_session(subscriber_id)`** — Memperpanjang sesi via `GET /realms/xl-ciam/auth/extend-session?contact=<base64 subscriber_id>&contactType=DEVICEID`. Mengembalikan `exchange_code` (dari `data.exchange_code`).
- **`submit_otp(api_key, contact_type, contact, code)`** — `POST /realms/xl-ciam/protocol/openid-connect/token` dengan `grant_type=password`. Mengirim OTP (SMS, kode 6 digit) atau exchange code (DEVICEID). Header memuat `Ax-Api-Signature` (dari `make_ax_api_signature` di `ahsiata/core/crypto.py`); `Ax-Request-At` di-set ke timestamp 5 menit lebih awal. Mengembalikan token OIDC `{access_token, id_token, refresh_token, ...}`.
- **`get_new_token(api_key, refresh_token, subscriber_id)`** — Flow *refresh token grant*:
  1. `POST .../token` dengan `grant_type=refresh_token` (header lowercase).
  2. Jika respons `400` + `error_description == "Session not active"`: memanggil `extend_session(subscriber_id)` lalu `submit_otp(..., "DEVICEID", subscriber_id, exchange_code)` untuk memperoleh token baru.
  3. Jika token tidak valid → `ValueError`.

### 6.2 `ahsiata/core/session.py` — Singleton `Session` (instance `SESSION`)

Menyimpan sesi aktif dan daftar refresh token. Tidak menyentuh disk saat import — state dimuat lewat `SESSION.initialize()` yang dipanggil dari `ahsiata.cli.main()`.

**State (class-level)**:

- `api_key` — diisi dari `CONFIG.api_key` saat konstruksi (sebelumnya placeholder hardcode `"Noir1"`).
- `refresh_tokens` — daftar `{number, subscriber_id, subscription_type, refresh_token}`.
- `active_user` — `{number, subscriber_id, subscription_type, tokens}` dengan `tokens = {refresh_token, access_token, id_token}`.
- `last_refresh_time` — timestamp token terakhir di-refresh.

**Metode penting**:

| Metode | Peran |
|---|---|
| `initialize()` | Muat state dari disk satu kali (dipanggil entry point): baca `refresh-tokens.json` (buat `[]` jika belum ada) + `load_active_number()`. |
| `load_tokens()` | Membaca `refresh-tokens.json`; hanya entry valid (`number` & `refresh_token`). |
| `add_refresh_token(number, refresh_token)` | Tambah/replace token; jika nomor baru, ambil profil via `get_new_token` + `get_profile` untuk `subscriber_id` & `subscription_type`; simpan file; set active user. |
| `remove_refresh_token(number)` | Hapus dari list; jika yang dihapus adalah akun aktif, otomatis pindah ke akun pertama yang tersisa. |
| `set_active_user(number)` | Tukar token (`get_new_token`), ambil profil, set `active_user`, simpan `active.number`. |
| `renew_active_user_token()` | Refresh token untuk akun aktif. |
| `get_active_user()` | Mengembalikan user aktif; **auto-renew jika `last_refresh_time` kosong atau melebihi `TOKEN_REFRESH_INTERVAL` (default 300 detik)**. |
| `get_active_tokens()` | Helper → `active_user["tokens"]`. |
| `write_tokens_to_file()` / `write_active_number()` / `load_active_number()` | Persistensi ke `refresh-tokens.json` dan `active.number`. |

**Persistensi**:

- `refresh-tokens.json` — daftar token (indent 4).
- `active.number` — nomor akun aktif (plain text). Jika tidak ada user aktif, file dihapus.

### 6.3 `ahsiata/ui/account.py`

Alur login interaktif:

1. Input nomor (`628xxx`), validasi format.
2. `get_otp()` → kirim OTP.
3. Loop maksimal **5 percobaan** input OTP 6 digit → `submit_otp(api_key, "SMS", ...)`.
4. Token refresh disimpan via `SESSION.add_refresh_token()`. Menu akun juga mendukung perpindahan akun, penambahan (`0`), dan penghapusan (`del <nomor urut>`; akun aktif tidak bisa dihapus).

---

## 7. Protokol Komunikasi API

Semua panggilan API utama melewati **`send_api_request()`** di `ahsiata/api/client.py` (atau `post_encrypted()` untuk payload yang sudah ditandatangani ala payment):

1. **Enkripsi payload** — `encryptsign_xdata(api_key, method, path, id_token, payload)` (`ahsiata/api/encrypt.py`) menghasilkan:
   - `body = {"xdata": <AES-CBC urlsafe-b64>, "xtime": <ms>}`
   - `x_signature` (HMAC-SHA512).
2. **Header** (dibangun `build_headers(path, id_token, xtime_ms, x_signature)`):
   ```
   host                : BASE_API_URL tanpa skema
   content-type        : application/json; charset=utf-8
   user-agent          : UA
   x-api-key           : API_KEY
   authorization       : Bearer <id_token>
   x-hv                : X_HV (default "v3")
   x-signature-time    : xtime // 1000 (detik)
   x-signature         : x_signature
   x-request-id        : uuid4
   x-request-at        : timestamp gaya Java (java_like_timestamp)
   x-version-app       : APP_VERSION (default "8.9.0")
   ```
3. **Request** — `POST {BASE_API_URL}/{path}` dengan body JSON terenkripsi, timeout 30 detik, lewat **satu `requests.Session` bersama** yang memakai `urllib3.Retry(total=2, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504))`.
4. **Dekripsi respons** — `decrypt_xdata(api_key, json.loads(resp.text))` → dict Python. Jika gagal, mencetak `[err dekripsi]` dan mengembalikan raw text respons.

Konfigurasi (URL, `UA`, header) diambil dari `CONFIG` (`ahsiata/config.py`) — bukan di-import antar modul. Flow payment memakai `post_encrypted(api_key, path, id_token, encrypted_payload, x_signature=...)` untuk menimpa signature bawaan dengan signature payment.

---

## 8. Kriptografi & Penandaan (Signing)

Implementasi inti ada di **`ahsiata/core/crypto.py`**; wrapper untuk aplikasi (fingerprint, kompatibilitas signature lama, timestamp) ada di **`ahsiata/api/encrypt.py`**.

### 8.1 Enkripsi body (`xdata`)

```
IV   = SHA256(str(xtime_ms)) hexdigest → ambil 16 byte pertama (ASCII hex)
Key  = XDATA_KEY (ASCII)
Cipher = AES-CBC (AES-256), padding PKCS7
Output = urlsafe_base64(encrypted)
```

- `encrypt_xdata(plaintext, xtime_ms)` dan `decrypt_xdata(xdata, xtime_ms)` — di `ahsiata/core/crypto.py`.

### 8.2 `x-signature` (API utama)

```
key = f"{X_API_BASE_SECRET};{id_token};{method};{path};{sig_time_sec}"
msg = f"{id_token};{sig_time_sec};"
sig = HMAC-SHA512(key, msg).hexdigest()
```

- `make_x_signature(id_token, method, path, sig_time_sec)` — di `ahsiata/core/crypto.py`.

### 8.3 `x-signature` khusus (payment / loyalty / bounty)

Salt di key sekarang dari `PAYMENT_SIGN_SALT` (default `ae-hei_9Tee6he+Ik3Gais5=`), bukan literal di kode:

- `make_x_signature_payment(...)` — `key = f"{X_API_BASE_SECRET};{sig_time_sec}#{salt};POST;{path};{sig_time_sec}"`, `msg = f"{access_token};{token_payment};{sig_time_sec};{payment_for};{payment_method};{package_code};"`.
- `make_x_signature_bounty(...)` — path fixed `api/v8/personalization/bounties-exchange`.
- `make_x_signature_loyalty(...)` — `msg = f"{token_confirmation};{sig_time_sec};{package_code};"`.
- `make_x_signature_bounty_allotment(...)` — menyisipkan `destination_msisdn` ke dalam key dan msg.

Semua ada di `ahsiata/core/crypto.py`; factory pembungkusnya (`make_payment_signature`, `make_bounty_signature`, `make_loyalty_signature`, `make_bounty_allotment_signature`) ada di `ahsiata/api/purchase/base.py`.

### 8.4 `Ax-Api-Signature` (CIAM)

```
key     = AX_API_SIG_KEY (ASCII)
preimage = f"{ts_for_sign}password{contact_type}{contact}{code}openid"
sig     = base64(HMAC-SHA256(key, preimage))
```

- `make_ax_api_signature(ts_for_sign, contact, code, contact_type)` — di `ahsiata/core/crypto.py`; dipakai oleh `ahsiata/api/auth.py` di `submit_otp`.

### 8.5 Fingerprint perangkat (`ax.fp`)

`ahsiata/api/encrypt.py`:

- `_build_fingerprint_plain(dev: DeviceInfo)` — string `manufacturer|model|lang|resolution|tz_short|ip|font_scale|Android <ver>|msisdn`.
- `ax_fingerprint(dev, secret_key_32hex_ascii)` — AES-CBC (IV = 16 byte `\x00`), hasil base64.
- `load_ax_fp()` — membaca `ax.fp`; jika tidak ada/empty, generate dengan `DeviceInfo` acak (manufacturer `samsung####`, model `SM-N93####`, dst., MSISDN dari `DEVICE_FAKE_MSISDN`) lalu simpan ke `ax.fp`.
- `ax_device_id()` — `MD5(ax.fp)`.

### 8.6 Field terenkripsi & MSISDN Circle

- `build_encrypted_field(iv_hex16=None, urlsafe_b64=False)` — mengenkripsi string kosong (di-pad) dengan `ENCRYPTED_FIELD_KEY`; hasil `b64(ct) + iv_hex`. Dipakai untuk `encrypted_payment_token` dan `encrypted_authentication_id`.
- `encrypt_circle_msisdn(msisdn)` / `decrypt_circle_msisdn(encrypted_b64)` — format `urlsafe_b64(ct) + iv_hex16`; IV diambil dari 16 karakter terakhir, sisanya ciphertext b64. Primitive di `ahsiata/core/crypto.py` (signature `encrypt_circle_msisdn(msisdn)`); wrapper `ahsiata/api/encrypt.py` menerima `api_key` sebagai argumen pertama (diabaikan).

### 8.7 Utilitas waktu

- `java_like_timestamp(now)` — `YYYY-MM-DDTHH:MM:SS.cc+TZ:OFF` (2 digit centisecond).
- `ts_gmt7_without_colon(dt)` — timestamp GMT+7 dengan millis, tanpa colon pada offset.

---

## 9. Lapisan Klien (Client Layer)

### 9.1 `ahsiata/api/client.py` — HTTP rendah

Fungsi inti (lihat juga §7):

- `build_headers(path, id_token, xtime_ms, x_signature)` — konstruksi header standar.
- `post_encrypted(api_key, path, id_token, encrypted_payload, x_signature=None)` — POST body terenkripsi; `x_signature` menimpa signature bawaan (flow payment).
- `send_api_request(api_key, path, payload_dict, id_token, method="POST")` — enkripsi → sign → POST → dekripsi (thin wrapper di atas `post_encrypted`).
- `get_balance(api_key, id_token)` — `api/v8/packages/balance-and-credit`.
- `intercept_page(api_key, tokens, option_code, is_enterprise=False)` — `misc/api/v8/utility/intercept-page` (hit sebelum pembelian).

Modul per-domain (semuanya `POST`, lewat `send_api_request`):

| Modul | Fungsi | Path |
|---|---|---|
| `profile.py` | `get_profile` | `api/v8/profile` |
| `profile.py` | `get_tiering_info` | `gamification/api/v8/loyalties/tiering/info` |
| `packages.py` | `get_family` | `api/v8/xl-stores/options/list` (brute-force `is_enterprise` × `migration_type`) |
| `packages.py` | `get_package` | `api/v8/xl-stores/options/detail` |
| `packages.py` | `get_addons` | `api/v8/xl-stores/options/addons-pinky-box` |
| `packages.py` | `get_package_details` | (komposisi) family → variant → option → detail |
| `packages.py` | `unsubscribe` | `api/v8/packages/unsubscribe` |
| `catalog.py` | `get_segments` | `api/v8/configs/store/segments` |
| `catalog.py` | `get_family_list` | `api/v8/xl-stores/options/search/family-list` |
| `catalog.py` | `get_store_packages` | `api/v9/xl-stores/options/search` |
| `catalog.py` | `get_redeemables` | `api/v8/personalization/redeemables` |
| `notifications.py` | `get_notifications` | `api/v8/notification-non-grouping` |
| `notifications.py` | `get_notification_detail` | `api/v8/notification/detail` |
| `transactions.py` | `get_transaction_history` | `payments/api/v8/transaction-history` |

`get_family` melakukan iterasi semua kombinasi `is_enterprise ∈ {False, True}` dan `migration_type ∈ {NONE, PRE_TO_PRIOH, PRIOH_TO_PRIO, PRIO_TO_PRIOH}` (`MigrationType.ALL`) hingga mendapat respons `status == "SUCCESS"` dengan nama family non-kosong.

### 9.2 `ahsiata/api/family_plan.py` — Family Plan

| Fungsi | Path | Keterangan |
|---|---|---|
| `get_family_data` | `sharings/api/v8/family-plan/member-info` | Info plan & anggota |
| `validate_msisdn` | `api/v8/auth/check-dukcapil` | Validasi MSISDN (bizon, optimus, dll.) |
| `change_member` | `sharings/api/v8/family-plan/change-member` | Assign nomor ke slot |
| `remove_member` | `sharings/api/v8/family-plan/remove-member` | Hapus anggota |
| `set_quota_limit` | `sharings/api/v8/family-plan/allocate-quota` | Alokasi kuota per anggota |

### 9.3 `ahsiata/api/circle.py` — Circle / Family Hub

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

### 9.4 `ahsiata/api/registration.py`

- `dukcapil(api_key, msisdn, kk, nik)` — `api/v8/auth/regist/dukcapil`. (Fungsi `validate_puk` tidak ada lagi di codebase.)

### 9.5 Katalog store

Fungsi katalog (`get_segments`, `get_family_list`, `get_store_packages`, `get_redeemables`) ada di **`ahsiata/api/catalog.py`** — lihat tabel §9.1. Direktori `ahsiata/api/store/` hanya berisi `__init__.py` kosong (sisa struktur lama).

### 9.6 `ahsiata/api/purchase/` — Settlement (lihat juga §12)

| Modul | Fungsi |
|---|---|
| `base.py` | `resolve_amount`, `join_item_codes`, `fetch_payment_token` — fetch `token_payment` + `timestamp` (`payments/api/v8/payment-methods-option`); `post_signed_payload` — enkripsi + attach signature payment + POST via `post_encrypted`; factory signature `make_payment_signature` / `make_bounty_signature` / `make_loyalty_signature` / `make_bounty_allotment_signature` |
| `balance.py` | `settlement_balance`, `append_decoy_item`, `settle_with_decoy` — settlement via saldo + dekoy terpusat |
| `qris.py` | `settlement_qris`, `get_qris_code`, `show_qris_payment` |
| `ewallet.py` | `settlement_multipayment`, `show_multipayment` |
| `redeem.py` | `settlement_bounty`, `settlement_loyalty`, `bounty_allotment` |

---

## 10. Lapisan Menu (UI Layer)

Semua modul `ahsiata/ui/*` adalah fungsi interaktif berbasis `print()` + `input()`. Seluruh teks UI dan log memakai Bahasa Indonesia (istilah domain API dipertahankan: `SUCCESS`, `Payment For`, `Family Code`, `QRIS`, `DANA`, dll.).

### 10.1 `ahsiata/ui/utils.py`

| Fungsi | Peran |
|---|---|
| `clear_screen()` | Bersihkan terminal + render ASCII art logo |
| `pause()` | `input("\nTekan enter untuk melanjutkan...")` |
| `display_html(html_text, width)` | Konversi HTML (mis. T&C paket) ke teks rata kiri |
| `format_quota_byte(byte)` | Format byte → `GB`/`MB`/`KB`/`B` |

`_HTMLToText` adalah parser berbasis `HTMLParser` — tag `<li>` dijadikan bullet `- `, `<br>` menjadi newline, baris di-wrap per `width`.

### 10.2 `ahsiata/ui/package/details.py` & `list.py`

Fungsi utama:

- **`show_package_details(api_key, tokens, package_option_code, is_enterprise, option_order=-1)`** — Menu detail paket: nama, harga, masa aktif, poin, plan type, benefits (kuota/menit/SMS), addons, T&C (`SnK MyXL`). Opsi pembelian:
  - `1` Pulsa (balance)
  - `2` E-Wallet
  - `3` QRIS
  - `4` Pulsa + Decoy
  - `5` Pulsa + Decoy V2 (`token_confirmation_idx=1`)
  - `6` QRIS + Decoy (+1K, decoy `qris`, amount diatur manual)
  - `7` QRIS + Decoy V2 (Rp0, decoy `qris0`)
  - `8` Pulsa N kali (→ `purchase_n_times_by_option_code`)
  - `0` Tambah bookmark (hanya jika `option_order != -1`)
  - `00` Kembali ke daftar paket
  - `B` Ambil sebagai bonus (bounty), `BA` Kirim bonus (allotment), `L` Beli dengan poin (loyalty) — hanya tampil jika `payment_for == "REDEEM_VOUCHER"`.
- **`get_packages_by_family(family_code, is_enterprise=None, migration_type=None)`** (`list.py`) — Tampilkan semua variant & option dalam family; pilih nomor → `show_package_details`.
- **`fetch_my_packages()`** (`details.py`) — `api/v8/packages/quota-details` → daftar kuota aktif, detail per paket, dan opsi `del <no>` untuk unsubscribe.

### 10.3 `ahsiata/ui/purchase/loop.py` & `single.py`

- **`purchase_by_family(family_code, use_decoy, pause_on_success, delay_seconds, start_from_option)`** (`loop.py`) — Loop membeli **semua** option dalam family dari `start_from_option`. Menyusun `PaymentItem` (dengan nama di-prefix angka acak `randint(1000,9999)`), melakukan `settlement_balance`/`settle_with_decoy`; laporan sukses di akhir.
- **`purchase_n_times_by_option_code(n, option_code, use_decoy, delay_seconds, pause_on_success, token_confirmation_idx=0)`** (`single.py`) — Beli satu option (langsung via option code) N kali.

### 10.4 `ahsiata/ui/payment.py`

- `show_transaction_history(api_key, tokens)` — Tampilkan riwayat (`get_transaction_history`), format waktu GMT+7 (Jakarta).

### 10.5 `ahsiata/ui/hot.py`

- `show_hot_menu()` — Membaca `hot_data/hot.json`, menampilkan daftar, memilih → resolve option code via `get_family` → `show_package_details`.
- `show_hot_menu2()` — Membaca `hot_data/hot2.json` (paket *bundle* multi-item), memuat detail setiap item → menyusun `payment_items` → menu pembayaran (1. Balance, 2. E-Wallet, 3. QRIS).

### 10.6 `ahsiata/ui/bookmark.py`

- `show_bookmark_menu()` — List bookmark; pilih → `get_family` + `get_package_details` → `show_package_details`. Dukungan hapus (`000`), kembali (`00`).

### 10.7 `ahsiata/ui/family_plan.py`

- `show_family_info(api_key, tokens)` — Info plan (parent, total kuota, anggota), dengan opsi:
  - `1` Ganti member (validasi MSISDN → cek `family_plan_role == "NO_ROLE"` → `change_member`)
  - `limit <slot> <MB>` → `set_quota_limit`
  - `del <slot>` → `remove_member`
  - `00` Kembali.

### 10.8 `ahsiata/ui/circle/info.py`

- `show_circle_info(api_key, tokens)` — Tampilkan grup Circle, anggota (MSISDN didekripsi), kuota, spending tracker, dengan opsi:
  - `1` Undang member (validasi + `invite_circle_member`)
  - `del <no>` Hapus member (proteksi parent & last member)
  - `acc <no>` Terima undangan
  - `2` Daftar bonus (`_show_bonus_list`, action `PLP`/`PDP`).
- `show_circle_creation(api_key, tokens)` — Membuat Circle baru.

### 10.9 `ahsiata/ui/notification.py`

- `show_notification_menu()` — Mengambil notifikasi dari `get_notifications` (`api/v8/notification-non-grouping`), menampilkan status READ/UNREAD, dan opsi `1` untuk menandai semua unread via `get_notification_detail`.

### 10.10 `ahsiata/ui/store/`

- `segments.py::show_store_segments_menu(is_enterprise)` — Segmen store → pilih `A1`, `B2`, dst. → `show_package_details`.
- `search.py::show_family_list_menu(subs_type, is_enterprise)` — Family list → pilih nomor → `get_packages_by_family`.
- `search.py::show_store_packages_menu(subs_type, is_enterprise)` — Paket store (hasil `results_price_only`) → `show_package_details`.
- `redeemables.py::show_redeemables_menu(is_enterprise)` — Redeemables per kategori → action `PLP`/`PDP`. (Nama file sudah diperbaiki dari `redemables.py` pada layout lama.)

---

## 11. Lapisan Layanan (Service Layer)

### 11.1 `ahsiata/core/decoy.py` — Paket Decoy (lihat §13)

### 11.2 `ahsiata/core/bookmark.py` — Singleton `Bookmark` (instance `BOOKMARK`)

- File: `bookmark.json` (CWD-relative, tidak disentuh saat import — dimuat lewat `BOOKMARK.initialize()` dari entry point).
- Skema item: `{family_name, family_code, is_enterprise, variant_name, option_name, order}`.
- `add_bookmark(...)` — dedup berdasarkan `(family_code, variant_name, order)`.
- `remove_bookmark(...)`, `get_bookmarks()`.
- `_ensure_schema()` — migrasi otomatis field `family_name` & `order` untuk kompatibilitas.

---

## 12. Alur Pembelian & Metode Pembayaran

Struktur kontrak item pembelian (`ahsiata/type_dict.py`):

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

Alur `settlement_balance(api_key, tokens, items, payment_for, ask_overwrite, overwrite_amount=-1, token_confirmation_idx=0, amount_idx=-1, ...)`:

1. Validasi `overwrite_amount` / `ask_overwrite`.
2. `resolve_amount` — pilih amount: overwrite eksplisit > tanya user > harga item (indeks `amount_idx`).
3. Bangun `payment_targets` (item codes dipisah `;` via `join_item_codes`).
4. `intercept_page(...)` — hit intercept.
5. `fetch_payment_token` → `payments/api/v8/payment-methods-option` → `token_payment` + `timestamp` (dipakai untuk `x-signature` payment).
6. `POST payments/api/v8/settlement-multipayment` dengan `payment_method: "BALANCE"`, `total_amount`, `items`, field terenkripsi (`encrypted_payment_token`, `encrypted_authentication_id`), `additional_data` detail.
7. Signature via `make_payment_signature` (`purchase/base.py`), dikirim lewat `post_signed_payload` → `post_encrypted(..., x_signature=...)`.
8. Dekripsi respons; sukses jika `status == "SUCCESS"`.

Fungsi tambahan (dipakai flow decoy, lihat §13):

- `append_decoy_item(items, decoy_detail)` — tambahkan item decoy ke daftar `PaymentItem`.
- `settle_with_decoy(api_key, tokens, items, payment_for, decoy_detail, token_confirmation_idx=0)` — sentralisasi: append decoy → `settlement_balance` dengan `overwrite_amount = harga paket + harga decoy` → jika server membalas `Bizz-err.Amount.Total=<angka>`, ulangi **sekali** dengan `overwrite_amount = <angka>` (total koreksi server).

### 12.2 QRIS (`purchase/qris.py`)

- `settlement_qris(...)` → `POST payments/api/v8/settlement-multipayment/qris` (payload mirip balance, `payment_method: "QRIS"`, `verification_token: token_payment`). Mengembalikan `transaction_code`.
- `get_qris_code(api_key, tokens, transaction_id)` → `payments/api/v8/pending-detail` → `qr_code`.
- `show_qris_payment(...)` — render QR di terminal (`qrcode.print_ascii`) dan mencetak URL viewer `https://ki-ar-kod.netlify.app/?data=<b64>`.

### 12.3 E-Wallet (`purchase/ewallet.py`)

- `settlement_multipayment(...)` → `POST payments/api/v8/settlement-multipayment/ewallet` dengan `payment_method` salah satu dari `DANA`, `SHOPEEPAY`, `GOPAY`, `OVO` dan `wallet_number`.
- `show_multipayment(...)` — menu pilihan wallet; DANA/OVO meminta nomor wallet (validasi format `08...`); hasil settlement → tampilkan `deeplink` (kecuali OVO).

### 12.4 Redeem Bounty / Loyalty (`purchase/redeem.py`)

- `settlement_bounty(...)` — `POST api/v8/personalization/bounties-exchange`, `payment_for: "REDEEM_VOUCHER"`, `payment_method: "BALANCE"`. Signature via `make_bounty_signature`.
- `settlement_loyalty(...)` — `POST gamification/api/v8/loyalties/tiering/exchange` (bayar dengan poin). Signature via `make_loyalty_signature`.
- `bounty_allotment(...)` — `POST gamification/api/v8/loyalties/tiering/bounties-allotment` (kirim bonus ke MSISDN tujuan). Signature via `make_bounty_allotment_signature`.

---

## 13. Paket Decoy

**Konsep**: menambahkan paket "decoy" (paket penambah dummy) ke dalam keranjang pembayaran sehingga nilai `total_amount` dapat diubah untuk memengaruhi hasil settlement.

### `ahsiata/core/decoy.py` — Singleton `DecoyPackage` (instance `DECOY`)

- **State**: `decoys` dict dengan kunci `{default,prio}-{balance,qris,qris0}`; setiap entry `{option_code, price, last_fetched_at}`.
- **Sumber data**: `decoy_data/decoy-<name>.json` berisi `{family_name, family_code, is_enterprise, migration_type, variant_code, option_name, order, price}`. (Catatan: `decoy_data/decoy-default-pass20.json` ada di repo tapi **tidak dibaca** kode — hanya 6 nama `{default,prio}-{balance,qris,qris0}` yang dikelola.)
- **`check_subscriber_change()`** — jika `subscriber_id` berubah, reset decoy; pilih prefix:
  - `prio-` bila `subscription_type ∈ {PRIORITAS, PRIOHYBRID, GO}`
  - `default-` selain itu.
- **`fetch_decoy_data(decoy_name)`** — baca JSON lokal → `get_package_details(...)` → simpan `option_code`, `last_fetched_at`.
- **`get_decoy(payment_type)`** — return decoy; **refresh otomatis jika `last_fetched_at` > 300 detik** (`_DECOY_TTL_SECONDS`).

### Penggunaan dalam pembelian

- Balance + Decoy (`choice 4/5`): `settle_with_decoy` → `overwrite_amount = harga_paket + harga_decoy`; jika server membalas `Bizz-err.Amount.Total=<angka>`, ulangi **sekali** dengan `overwrite_amount = <angka>` tersebut. Choice `5` memakai `token_confirmation_idx = 1`.
- QRIS + Decoy (`choice 6/7`): `append_decoy_item` + `show_qris_payment` dengan `payment_for = "SHARE_PACKAGE"`, `token_confirmation_idx = 1`, harga decoy ditambahkan ke item; user mengatur ulang amount (trial & error, `0` = malformed).

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

Saat memilih bookmark, aplikasi memanggil `get_family(family_code, is_enterprise)` lalu `get_package_details(family_code, variant_name, order, is_enterprise)` untuk mendapatkan detail paket (option code) sebelum menampilkan `show_package_details`.

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
| `refresh-tokens.json` | Ya (buat `[]` saat `SESSION.initialize()`) | Daftar refresh token pengguna |
| `active.number` | Ya | Nomor akun aktif |
| `ax.fp` | Ya | Fingerprint perangkat AES |
| `bookmark.json` | Ya (buat `[]` saat `BOOKMARK.initialize()`) | Daftar bookmark |
| `decoy_data/*.json` (7 file) | Tidak | Konfigurasi paket decoy |
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

Catatan: struktur tiap file bervariasi — `decoy-default-qris.json` berisi `family_name`/`option_name` kosong (`price: 1000`), `decoy-default-qris0.json` berisi `family_name`/`option_name` terisi (`price: 0`). Yang dibaca kode (`decoy.py`) hanyalah `price` dan field resolusi `{family_code, variant_code, order, is_enterprise, migration_type}`.

---

## 17. Dependensi

Dari `requirements.txt` (5 paket langsung, versi di-pin; transitif tidak lagi di-pin):

| Paket | Versi | Peran |
|---|---|---|
| `Brotli` | 1.2.0 | Dekompresi respons (header CIAM `Accept-Encoding: gzip, deflate, br`) |
| `pycryptodome` | 3.23.0 | AES, HMAC, padding (kriptografi) |
| `python-dotenv` | 1.2.2 | Load `.env` (di `ahsiata/config.py`) |
| `qrcode` | 8.2 | Render QRIS di terminal (`print_ascii`) |
| `requests` | 2.34.2 | HTTP client (session + retry) |

Transitives (`certifi`, `charset-normalizer`, `idna`, `urllib3`) tidak di-pin dan resolve otomatis via `requests`. Versi yang sama didaftarkan di `pyproject.toml` (`dependencies`).

---

## 18. Setup & Menjalankan

### Linux (Debian/Ubuntu, Fedora, Arch)

```bash
git clone https://github.com/purplemashu/Ah-Si-Ata
cd Ah-Si-Ata
make setup           # = bash setup.sh (deps sistem + venv + pip install -r requirements.txt) + stamp
make run             # pastikan .env ada (copy dari template jika belum), lalu jalankan `venv/bin/python main.py`
```

Manual (tanpa Makefile):

```bash
bash setup.sh          # deteksi package manager (apt-get, dnf, pacman, apk), buat venv/, install requirements.txt
source venv/bin/activate
python main.py
```

`make install` = `venv/bin/python -m pip install -r requirements.txt` (re-install deps ke venv); `make env` membuat `.env` dari `.env.template`; `make update` = `git pull --rebase`; `make clean` menghapus `venv/` dan cache.

Tiga cara meluncurkan CLI (setara):

- `python main.py` — thin wrapper.
- `python -m ahsiata` — via `ahsiata/__main__.py`.
- `ahsiata` — console script dari `pyproject.toml` (`pip install .` atau `pip install -e .` di venv).

### Persiapan `.env`

1. Buat file `.env` (contoh dari `.env.template`).
2. Isi 10 variabel REQUIRED: `BASE_API_URL`, `BASE_CIAM_URL`, `BASIC_AUTH`, `AX_FP_KEY`, `UA`, `API_KEY`, `ENCRYPTED_FIELD_KEY`, `XDATA_KEY`, `AX_API_SIG_KEY`, `X_API_BASE_SECRET`. Variabel OPTIONAL (`PAYMENT_SIGN_SALT`, `DEVICE_*`, `APP_VERSION`, `X_HV`, `DEFAULT_SUBSTYPE`, `TOKEN_REFRESH_INTERVAL`) memakai default di kode.

> Tanpa salah satu variabel REQUIRED, `ahsiata/config.py` akan `raise ValueError("<nama> environment variable not set")` saat import. `load_dotenv()` membaca `.env` dari CWD ke atas secara otomatis.

---

## 19. Catatan Pengembangan

- **`CIRCLE_MSISDN_KEY`** sudah **dihapus** dari `.env.template`; enkripsi MSISDN Circle memakai `ENCRYPTED_FIELD_KEY` (via `encrypt_circle_msisdn`).
- **Tidak ada hierarki exception khusus** — hierarki lama (`ahsiata/exceptions.py` yang memuat `AhsiataError`, `ConfigError`, `AuthError`, `APIError`, `DecoyError`, `CipherError`) sudah dihapus. Kode sekarang memakai `ValueError` + pesan `print` biasa; konfigurasi hilang memicu `ValueError` dari `config.py`.
- **Versi aplikasi** yang di-emulasi: `x-version-app: 8.9.0` (default `APP_VERSION`); model perangkat emulasi: `SM-N935F` (default `DEVICE_MODEL`).
- **`show_hot_menu2`** bergantung pada data lokal `hot2.json`; jika struktur server berubah, `get_package_details` dapat gagal dan pembelian dibatalkan.
- Error `Bizz-err.Amount.Total=<angka>` adalah mekanisme server untuk mengoreksi jumlah; penanganan terpusat di `settle_with_decoy` (`ahsiata/api/purchase/balance.py`) — kode mengekstrak `<angka>` dan mengulang settlement sekali.
- **Testing offline**: `python -m unittest discover -s tests -v` menjalankan `tests/test_crypto.py` (roundtrip `xdata` & circle-msisdn, determinisme signature, tanpa jaringan). CI (`.github/workflows/ci.yml`) pada push/PR: checkout → setup-python 3.12 → `pip install -r requirements.txt` → unittest.

---

*Dokumen ini dihasilkan dari analisis langsung terhadap source code pada branch `main` (commit terkini di repo lokal). Perilaku dapat berubah seiring update repository.*