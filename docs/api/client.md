# ahsiata/api/client.py — HTTP client level rendah

Session `requests` bersama, header baku, POST body terenkripsi, dekripsi respons.

## Ringkasan

Titik masuk semua panggilan backend utama (`BASE_API_URL`). Satu `requests.Session` bersama dengan `urllib3.Retry(total=2, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504))`, timeout 30 detik. Alur per panggilan: `encryptsign_xdata(...)` → `build_headers(...)` → POST JSON → `decrypt_xdata(...)`.

## State & helper

- `_SESSION` — session bersama (module-level).
- `_common_payload(**overrides) -> dict` — `{"is_enterprise": False, "lang": "en"}` + override.

## Fungsi

- `build_headers(path, id_token, xtime_ms, x_signature) -> dict` — header: `host` (base URL tanpa skema), `content-type: application/json; charset=utf-8`, `user-agent`, `x-api-key`, `authorization: Bearer <id_token>`, `x-hv` (default `v3`), `x-signature-time` (`xtime // 1000`), `x-signature`, `x-request-id` (uuid4), `x-request-at` (`java_like_timestamp`), `x-version-app` (`8.9.0`).
- `post_encrypted(api_key, path, id_token, encrypted_payload, x_signature=None) -> dict | str` — POST body `{xdata, xtime}`; arg `x_signature` menimpa signature `xdata` bawaan (flow payment). Respons didekripsi; jika dekripsi gagal → log + return **raw string**.
- `send_api_request(api_key, path, payload_dict, id_token, method="POST")` — enkripsi → sign → `post_encrypted`.
- `get_balance(api_key, id_token) -> dict | None` — `api/v8/packages/balance-and-credit`; return `data.balance` (mis. `remaining`, `expired_at`); gagal → `fail` + `None`.
- `intercept_page(api_key, tokens, option_code, is_enterprise=False) -> None` — `misc/api/v8/utility/intercept-page`; payload `{package_option_code, ...}`; dicetak sebelum settlement (lihat [purchase](purchase/base.md)).

## Alur/Detail penting

- Respons non-`SUCCESS` di-log ke `ahsiata.log` sebagai `[respons gagal]`; dekripsi gagal dicatat `[dekripsi gagal]`.
- `log` dari [core/log.py](../core/log.md) dengan `raw=...[:2000]`.

## Catatan

- Gagal dekripsi mengembalikan **str mentah**, bukan dict — pemanggil harus menangani keduanya (`isinstance(res, dict)`).