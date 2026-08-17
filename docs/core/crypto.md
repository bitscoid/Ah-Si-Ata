# ahsiata/core/crypto.py — primitif kriptografi

AES-CBC (xdata & MSISDN Circle) dan HMAC (x-signature, Ax-Api-Signature). Semua kunci dari `CONFIG`.

## Ringkasan

Primitif murni tanpa I/O: enkripsi/dekripsi body `xdata`, lima varian HMAC signature, dan helper field terenkripsi MSISDN Circle. Wrapper aplikasi (fingerprint, timestamp, re-export) ada di [api/encrypt.py](../api/encrypt.md).

## Fungsi

- `_derive_iv(xtime_ms: int) -> bytes` — IV = 16 char pertama hex dari `SHA256(str(xtime_ms))` (ASCII).
- `encrypt_xdata(plaintext: str, xtime_ms: int) -> str` — AES-256-CBC, key `XDATA_KEY`, padding PKCS7, output `urlsafe_b64`.
- `decrypt_xdata(xdata: str, xtime_ms: int) -> str` — kebalikan; pad `=` ditambahkan otomatis.
- `make_x_signature(id_token, method, path, sig_time_sec) -> str` — key `f"{X_API_BASE_SECRET};{id_token};{method};{path};{sig_time_sec}"`, msg `f"{id_token};{sig_time_sec};"`, HMAC-SHA512 hex.
- `make_x_signature_payment(access_token, sig_time_sec, package_code, token_payment, payment_method, payment_for, path) -> str` — key `f"{X_API_BASE_SECRET};{sig_time_sec}#{salt};POST;{path};{sig_time_sec}"`, msg `f"{access_token};{token_payment};{sig_time_sec};{payment_for};{payment_method};{package_code};"`.
- `make_x_signature_bounty(access_token, sig_time_sec, package_code, token_payment) -> str` — path fixed `api/v8/personalization/bounties-exchange`; key menyisipkan `access_token`; msg `f"{access_token};{token_payment};{sig_time_sec};{package_code};"`.
- `make_x_signature_loyalty(sig_time_sec, package_code, token_confirmation, path) -> str` — msg `f"{token_confirmation};{sig_time_sec};{package_code};"`.
- `make_x_signature_bounty_allotment(sig_time_sec, package_code, token_confirmation, path, destination_msisdn) -> str` — key & msg menyisipkan `destination_msisdn`.
- `make_ax_api_signature(ts_for_sign, contact, code, contact_type) -> str` — key `AX_API_SIG_KEY` (ASCII), preimage `f"{ts_for_sign}password{contact_type}{contact}{code}openid"`, HMAC-SHA256, output `base64`.
- `encrypt_circle_msisdn(msisdn: str) -> str` — output `urlsafe_b64(ct) + iv_ascii16` (IV = 8 byte acak hex).
- `decrypt_circle_msisdn(encrypted_msisdn_b64: str) -> str` — 16 char terakhir = IV; kembalikan `""` jika dekripsi gagal.

## Alur/Detail penting

- Salt payment/bounty/loyalty dari `CONFIG.payment_sign_salt` (default `ae-hei_9Tee6he+Ik3Gais5=`), bukan literal.
- Signature payment/timestamp dipasang via [api/purchase/base.py](../api/purchase/base.md) `post_signed_payload`.

## Catatan

- `X_API_BASE_SECRET`, `XDATA_KEY`, `AX_API_SIG_KEY`, `ENCRYPTED_FIELD_KEY` adalah rahasia — jangan commit nilai asli.