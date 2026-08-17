<div align="center">
  <h1>Ah-Si-Ata</h1>
  <p>
    CLI client Python untuk backend MyXL (XL Axiata) — beli paket, kelola
    kuota, Family Plan, dan Circle langsung dari terminal.
  </p>
  <br>
  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/requests-2.34.2-3776AB?style=flat" alt="requests" />
    <img src="https://img.shields.io/badge/PyCryptodome-3.23.0-3776AB?style=flat&logo=pypi&logoColor=white" alt="PyCryptodome" />
    <img src="https://img.shields.io/badge/qrcode-8.2-3776AB?style=flat&logo=pypi&logoColor=white" alt="qrcode" />
    <img src="https://img.shields.io/badge/UI-Bahasa%20Indonesia-00C853?style=flat&logo=statuspage&logoColor=white" alt="UI Bahasa Indonesia" />
  </p>
  <p>
    <a href="docs/README.md">📘 Dokumentasi Teknis Lengkap</a>
  </p>
</div>

---

## ✨ Features

| Fitur | Deskripsi |
|-------|-----------|
| **Login OTP (OIDC)** | Login via SMS OTP, sesi dipertahankan dengan refresh-token plus auto-extend `DEVICEID` |
| **Multi-account** | Simpan banyak nomor, pindah akun cepat, penghapusan aman |
| **Cek Profil & Saldo** | Saldo pulsa, masa aktif, poin & tier (PREPAID) |
| **Katalog Paket** | Jelajahi HOT, option code, family code, store segments, redeemables |
| **Pembelian Paket** | Saldo/pulsa, e-wallet (DANA/ShopeePay/GoPay/OVO), QRIS |
| **Pembelian Massal** | Loop beli semua paket dalam satu family, decoy otomatis dengan retry jumlah |
| **Family Plan / Circle** | Kelola anggota, alokasi kuota, bonus, spending tracker |
| **Bookmark** | Simpan paket favorit (`bookmark.json`) |
| **Notifikasi & Riwayat** | Baca notifikasi, riwayat transaksi |
| **UI Bahasa Indonesia** | Seluruh teks UI dan log dalam Bahasa Indonesia |

## 🛠️ Tech Stack

| Layer | Teknologi |
|-------|-----------|
| **Bahasa** | Python 3.10+ (type hints, `TypedDict`, `dataclass` frozen) |
| **HTTP** | requests + `urllib3.Retry` (session reuse, retry 429/5xx) |
| **Kriptografi** | PyCryptodome (AES-CBC, HMAC-SHA256/512, padding PKCS7) |
| **Rendering** | qrcode (QRIS ASCII di terminal), `html.parser` (HTML→teks) |
| **Config** | python-dotenv (`.env` di-`load_dotenv` saat import) |
| **Packaging** | pyproject.toml (`console script ahsiata`), Makefile, setup.sh |
| **CI** | Dependabot (mingguan) |

---

## 📁 Project Structure

```text
Ah-Si-Ata/
├── .github/
│   └── dependabot.yml          # Update dependensi otomatis
├── ahsiata/
│   ├── __init__.py
│   ├── __main__.py             # Entry `python -m ahsiata`
│   ├── cli.py                  # main() + menu loop (entry utama)
│   ├── config.py               # CONFIG (frozen dataclass, load_dotenv)
│   ├── constants.py            # Endpoint, header, PaymentMethod, dsb.
│   ├── type_dict.py            # PaymentItem (TypedDict)
│   ├── core/
│   │   ├── crypto.py           # AES/HMAC primitives + signatures
│   │   ├── session.py          # SESSION: multi-account + token refresh
│   │   ├── bookmark.py         # BOOKMARK: paket favorit
│   │   └── decoy.py            # DECOY: cache paket decoy (TTL 5 mnt)
│   ├── api/
│   │   ├── client.py           # requests.Session, build_headers, post_encrypted
│   │   ├── encrypt.py          # fingerprint, xdata, timestamp, wrap crypto
│   │   ├── auth.py             # CIAM OIDC: OTP, extend-session, refresh
│   │   ├── profile.py packages.py catalog.py notifications.py
│   │   ├── transactions.py family_plan.py circle.py registration.py
│   │   └── purchase/
│   │       ├── base.py         # resolve_amount, fetch_payment_token, post_signed_payload
│   │       ├── balance.py      # PULSA + settle_with_decoy (retry Bizz-err)
│   │       ├── qris.py ewallet.py redeem.py
│   └── ui/
│       ├── utils.py            # clear_screen, pause, format_quota_byte, HTML→teks
│       ├── account.py bookmark.py hot.py notification.py payment.py family_plan.py
│       ├── package/details.py package/list.py
│       ├── purchase/loop.py purchase/single.py
│       ├── circle/info.py
│       └── store/segments.py store/search.py store/redeemables.py
├── decoy_data/                 # Data decoy family (7 file JSON)
├── hot_data/                   # Paket HOT preset (hot.json, hot2.json)
├── .env.template               # Template konfigurasi
├── requirements.txt            # Dep langsung (5 pin + 1 floor urllib3)
├── pyproject.toml              # Packaging + console script
├── Makefile setup.sh           # Setup & run otomatis
├── docs/                       # Dokumentasi teknis per-file (indeks: docs/README.md)
└── main.py                     # Wrapper tipis → ahsiata.cli.main()
```

---

## 🚀 Quick Start

### Prerequisites

- Linux (mendukung Debian/Ubuntu, Fedora, Arch, Alpine) — aslinya untuk Termux
- Python 3.10+
- `make` + `git` (untuk `make setup`)

### Cara 1 — Makefile (disarankan)

```bash
git clone https://github.com/bitscoid/Ah-Si-Ata.git
cd Ah-Si-Ata
make setup              # deps sistem + venv + install requirements
make env                # buat .env dari .env.template (edit nilainya)
make run                # jalankan `venv/bin/python main.py`
```

### Cara 2 — Manual

```bash
git clone https://github.com/bitscoid/Ah-Si-Ata.git
cd Ah-Si-Ata
python3 -m venv venv
venv/bin/pip install -e .
cp .env.template .env    # lalu isi semua nilai
venv/bin/ahsiata         # atau: venv/bin/python main.py / python -m ahsiata
```

### Konfigurasi

Salin `.env.template` ke `.env` dan isi nilai. Lihat bagian
[⚙️ Environment Configuration](#️-environment-configuration) untuk daftar lengkap.

---

## 💻 Development

### Perintah

| Perintah | Deskripsi |
|----------|-----------|
| `make setup` | Setup penuh: deps sistem, venv, python deps, `.env` |
| `make run` | Menjalankan aplikasi (auto-setup jika venv belum ada) |
| `make install` | (Re)install dependensi python ke venv |
| `make env` | Membuat `.env` dari `.env.template` jika belum ada |
| `make update` | `git pull --rebase` |
| `make clean` | Bersihkan venv dan `__pycache__` |
| `python -m pyflakes ahsiata/ main.py` | Lint (pastikan bersih) |

### Catatan

- Aplikasi **harus** dijalankan dari direktori proyek (state file bersifat
  relatif-CWD: `refresh-tokens.json`, `active.number`, `bookmark.json`, `ax.fp`).
- Seluruh UI & log berbahasa Indonesia; istilah domain API (SUCCESS, Family
  Code, Payment For, QRIS, dsb.) dipertahankan.

---

## ⚙️ Environment Configuration

### Wajib (raise `ValueError` jika kosong)

| Variabel | Deskripsi |
|----------|-----------|
| `BASE_API_URL` | Root backend utama (profile, paket, pembayaran) |
| `BASE_CIAM_URL` | Root identity provider OIDC (OTP, refresh token) |
| `BASIC_AUTH` | `base64(client_id:secret)` untuk `Authorization: Basic` CIAM |
| `AX_FP_KEY` | AES-256 secret untuk enkripsi fingerprint perangkat (`ax.fp`) |
| `UA` | User-Agent (mimik aplikasi MyXL Android) |
| `API_KEY` | Header `x-api-key` pada backend utama |
| `ENCRYPTED_FIELD_KEY` | AES key untuk `encrypted_payment_token`, `encrypted_authentication_id`, MSISDN Circle |
| `XDATA_KEY` | AES key untuk enkripsi body `xdata` |
| `AX_API_SIG_KEY` | HMAC-SHA256 key untuk `Ax-Api-Signature` CIAM |
| `X_API_BASE_SECRET` | Base secret HMAC-SHA512 `x-signature` |

### Opsional (punya default)

| Variabel | Default | Deskripsi |
|----------|---------|-----------|
| `PAYMENT_SIGN_SALT` | `ae-hei_...` | Salt HMAC payment/bounty/loyalty |
| `DEVICE_MANUFACTURER` | `samsung` | Header CIAM `Ax-Request-Device` |
| `DEVICE_MODEL` | `SM-N935F` | Header CIAM `Ax-Request-Device-Model` |
| `DEVICE_FAKE_MSISDN` | `6281398370564` | MSISDN fallback fingerprint |
| `APP_VERSION` | `8.9.0` | Header `x-version-app` |
| `X_HV` | `v3` | Header `x-hv` |
| `DEFAULT_SUBSTYPE` | `PREPAID` | Header CIAM `Ax-Substype` |
| `TOKEN_REFRESH_INTERVAL` | `300` | Detik antar rotasi token OIDC |

---

## 🎮 Menu CLI

| Input | Fitur |
|-------|-------|
| `1` | Login / Ganti akun |
| `2` | Lihat Paket Saya |
| `3` | Beli Paket 🔥 HOT 🔥 |
| `4` | Beli Paket 🔥 HOT-2 🔥 |
| `5` | Beli Paket berdasarkan Option Code |
| `6` | Beli Paket berdasarkan Family Code |
| `7` | Beli semua paket di Family Code (loop, decoy + jeda) |
| `8` | Riwayat Transaksi |
| `9` | Family Plan / Akrab Organizer |
| `10` | Circle |
| `11` | Store Segments |
| `12` | Store Family List |
| `13` | Store Packages |
| `14` | Redeemables |
| `R` | Register (Dukcapil) |
| `N` | Notifikasi |
| `V` | Validasi msisdn |
| `00` | Bookmark Paket |
| `99` | Tutup aplikasi |

---

## 🔐 Security Notes

- `refresh-tokens.json` berisi **refresh token OIDC = akses penuh akun**,
  disimpan plaintext di direktori kerja. Satukan file ini, jangan di-commit
  (sudah masuk `.gitignore`).
- `.env.template` memuat contoh kredensial backend; **jangan** publikasikan
  repo ini sebagai publik tanpa mengganti seluruh kunci, dan jangan pernah
  meng-commit `.env`.
- Proyek ini client **tidak resmi** untuk backend MyXL. Gunakan sebatas akun
  sendiri; aktivitas yang mencurigakan dapat diblokir oleh penyedia.

---

## 📄 License

Distributed under MIT License. See `LICENSE` file.

---

<div align="center">
  <p>
    📘 Dokumentasi teknis lengkap: <a href="docs/README.md">docs/README.md</a> ·
    🔐 Lindungi refresh token · ⚠️ Proyek tidak penting & tanpa garansi
  </p>
</div>