# ahsiata/api/encrypt.py — wrapper enkripsi & timestamp

Fingerprint perangkat (`ax.fp`), `encryptsign_xdata`, field terenkripsi, timestamp Java/GMT+7, dan re-export primitif crypto.

## Ringkasan

Lapisan aplikasi di atas [core/crypto.py](../core/crypto.md): menambah fingerprint perangkat, kompatibilitas import lama (re-export `decrypt_xdata`, `encrypt_circle_msisdn`, dll.), dan formatter waktu. Dipakai oleh [client.py](client.md), [auth.py](auth.md), [circle.py](circle.md), dan semua settlement.

## Kelas/Fungsi

- `DeviceInfo` — dataclass: `manufacturer, model, lang, resolution, tz_short, ip, font_scale, android_release, msisdn`.
- `_build_fingerprint_plain(dev) -> str` — `manufacturer|model|lang|resolution|tz_short|ip|font_scale|Android <ver>|msisdn`.
- `ax_fingerprint(dev, secret_key_32hex_ascii) -> str` — AES-CBC, IV 16 byte `\x00`, key `AX_FP_KEY`, output base64.
- `load_ax_fp() -> str` — baca `ax.fp`; jika kosong/missing: generate dengan `DeviceInfo` acak (`samsung####`, `SM-N93####`, `720x1540`, IP `192.169.69.69`, MSISDN `DEVICE_FAKE_MSISDN`) dan simpan.
- `ax_device_id() -> str` — `MD5(ax.fp)` hexdigest.
- `build_encrypted_field(iv_hex16=None, urlsafe_b64=False) -> str` — enkripsi string kosong (di-pad) dengan `ENCRYPTED_FIELD_KEY`; hasil `b64(ct) + iv_hex`. Dipakai untuk `encrypted_payment_token` & `encrypted_authentication_id`.
- `java_like_timestamp(now) -> str` — `%Y-%m-%dT%H:%M:%S.<2-digit centisecond>` + offset `+HH:MM`.
- `ts_gmt7_without_colon(dt) -> str` — GMT+7, millis 3 digit, offset tanpa colon (`+0700`).
- `encryptsign_xdata(api_key, method, path, id_token, payload) -> dict` — body `json.dumps(separators=(",", ":"))`, `xtime = int(time.time() * 1000)`, return `{"x_signature", "encrypted_body": {"xdata", "xtime"}}`.
- `decrypt_xdata(api_key, encrypted_payload) -> dict` — validasi kunci `xdata`/`xtime`, delegasi ke `core.crypto.decrypt_xdata`, `json.loads`.
- `encrypt_circle_msisdn(api_key, msisdn) -> str` / `decrypt_circle_msisdn(api_key, encrypted_msisdn_b64) -> str` — wrapper; arg `api_key` pertama **diabaikan** (kompatibilitas).

## Alur/Detail penting

- `ax.fp` adalah file state relatif-CWD; dibuat otomatis saat pertama kali dibutuhkan (side effect import di [auth.py](auth.md)).
- Semua signature `xdata` memakai `make_x_signature` (HMAC-SHA512), sedangkan payment memakai `x_signature` berbeda yang menimpa di [client.py](client.md) `post_encrypted`.

## Catatan

- `_random_iv_hex16()` = `os.urandom(8).hex()`; IV field terenkripsi bukan dari SHA256 (beda dengan IV `xdata`).