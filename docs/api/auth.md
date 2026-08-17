# ahsiata/api/auth.py — autentikasi CIAM (OIDC)

Endpoint CIAM di `BASE_CIAM_URL`: OTP SMS, extend-session, token exchange & refresh.

## Ringkasan

Menangani flow login OIDC: `get_otp` mengirim OTP SMS, `submit_otp` menukar kode → token, `get_new_token` me-refresh token dan otomatis memperpanjang sesi (DEVICEID) saat server membalas `Session not active`. Konstanta path dari `CIAMEndpoint`; header dari `_ciam_headers`.

## State & helper

- Module-level (dimuat **saat import**): `_AX_DEVICE_ID = ax_device_id()`, `_AX_FP = load_ax_fp()` — baca/generate `ax.fp` sekali.
- `_ciam_headers(*, lowercase=False, ts_override=None, include_signature=None, bearer_token=None) -> dict` — header baku: `Accept-Encoding: gzip, deflate, br`, `Ax-Device-Id`, `Ax-Fingerprint`, `Ax-Request-At`, `Ax-Request-Device` (manufacturer), `Ax-Request-Device-Model`, `Ax-Request-Id` (uuid4), `Ax-Substype` (`DEFAULT_SUBSTYPE`), `Authorization: Basic <BASIC_AUTH>`, `Host`, `User-Agent`. Opsi: `lowercase=True` untuk refresh flow, `include_signature` menyuntik `Ax-Api-Signature`.

## Fungsi

- `validate_contact(contact: str) -> bool` — diawali `628`, panjang ≤ 14.
- `get_otp(contact: str) -> str | None` — `GET {BASE_CIAM_URL}/realms/xl-ciam/auth/otp?contact=...&contactType=SMS&alternateContact=false`; kembalikan `subscriber_id`.
- `extend_session(subscriber_id: str) -> str | None` — `GET /realms/xl-ciam/auth/extend-session?contact=<base64 subscriber_id>&contactType=DEVICEID`; return `data.exchange_code`.
- `submit_otp(api_key, contact_type, contact, code) -> dict | None` — `POST /realms/xl-ciam/protocol/openid-connect/token`, body `contactType=...&code=...&grant_type=password&contact=...&scope=openid`. `SMS`: validasi kode 6 digit; `DEVICEID`: contact di-base64. `Ax-Api-Signature` dari `make_ax_api_signature`; `Ax-Request-At` = timestamp 5 menit **lebih awal** (di-set via `ts_override`). Return body token OIDC.
- `get_new_token(api_key, refresh_token, subscriber_id) -> dict | None` — `POST .../token` `grant_type=refresh_token` (header lowercase). Jika `400` + `error_description == "Session not active"`: `extend_session(subscriber_id)` → `submit_otp(..., "DEVICEID", ...)` untuk token baru. Raise `ValueError` untuk kasus: `subscriber_id` kosong, gagal exchange code, refresh token invalid ("Invalid refresh token"), atau respons tanpa `id_token`/ada `error`.

## Alur/Detail penting

- Kegagalan dicatat ke [core/log.py](../core/log.md) (`[OTP gagal]`, `[submit_otp gagal]`, `[token gagal]`, `[extend_session gagal]` dengan `raw=...[:2000]`).
- JSON respons di-`json.loads(resp.text)` langsung (bukan `resp.json()`) — body CIAM tidak terenkripsi.

## Catatan

- Timestamp semua dalam GMT+7 (`timezone(timedelta(hours=7))`); `ts_gmt7_without_colon` format `%Y-%m-%dT%H:%M:%S.%f` + offset tanpa colon.