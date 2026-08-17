# ahsiata/config.py — konfigurasi terpusat dari env

Membaca semua env var sekali saat import menjadi `CONFIG` (frozen dataclass).

## Ringkasan

`load_dotenv()` dipanggil di level modul (mencari `.env` dari CWD ke atas) sehingga import `ahsiata.*` apa pun di luar `python main.py` tetap mendapat env. Variabel REQUIRED yang hilang memicu `ValueError("<nama> environment variable not set")` seketika; variabel OPTIONAL memakai default di kode.

## Kelas/Fungsi

- `_required(name: str) -> str` — `os.getenv`; raise `ValueError` jika kosong.
- `_optional(name: str, default: str) -> str` — `os.getenv(name, default)`.
- `Config` — dataclass `frozen=True`, 18 field.
- `CONFIG` — instance tunggal dibuat saat import.

## Alur/Detail penting

Variabel REQUIRED (10):

| Field | Env var |
|---|---|
| `base_api_url` | `BASE_API_URL` |
| `base_ciam_url` | `BASE_CIAM_URL` |
| `basic_auth` | `BASIC_AUTH` |
| `ax_fp_key` | `AX_FP_KEY` |
| `ua` | `UA` |
| `api_key` | `API_KEY` |
| `encrypted_field_key` | `ENCRYPTED_FIELD_KEY` |
| `xdata_key` | `XDATA_KEY` |
| `ax_api_sig_key` | `AX_API_SIG_KEY` |
| `x_api_base_secret` | `X_API_BASE_SECRET` |

Variabel OPTIONAL (8) dengan default: `PAYMENT_SIGN_SALT` (`ae-hei_9Tee6he+Ik3Gais5=`), `DEVICE_MANUFACTURER` (`samsung`), `DEVICE_MODEL` (`SM-N935F`), `DEVICE_FAKE_MSISDN` (`6281398370564`), `APP_VERSION` (`8.9.0`), `X_HV` (`v3`), `DEFAULT_SUBSTYPE` (`PREPAID`), `TOKEN_REFRESH_INTERVAL` (`300`, di-`int()`).

## Catatan

- Side effect import: `load_dotenv()` membaca sistem file (pencarian ke atas dari CWD).
- `token_refresh_interval` dipakai [core/session.py](../core/session.md); kunci enkripsi dipakai [core/crypto.py](../core/crypto.md) dan [api/encrypt.py](../api/encrypt.md). Jangan commit `.env` asli.