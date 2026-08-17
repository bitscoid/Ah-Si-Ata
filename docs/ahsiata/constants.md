# ahsiata/constants.py — path endpoint & konstanta protokol

Semua string endpoint dan konstanta header/protokol yang dipakai lintas lapisan.

## Ringkasan

Modul tanpa logika: kumpulan kelas konstanta + satu string `LANG_EN = "en"`. Path `/` dibedakan: `Endpoint` adalah path di belakang `BASE_API_URL` (dikirim sebagai payload `xdata`), `CIAMEndpoint` adalah path lengkap di belakang `BASE_CIAM_URL` (dipakai langsung sebagai URL).

## Kelas

- `Endpoint` — path backend utama, dikelompokkan: profil/balance (`PROFILE`, `BALANCE`, `QUOTA_DETAILS`), paket (`FAMILY_LIST`, `PACKAGE_DETAIL`, `ADDONS`, `INTERCEPT_PAGE`), notifikasi & riwayat (`NOTIFICATIONS`, `NOTIFICATION_DETAIL`, `TRANSACTION_HISTORY`), gamifikasi (`TIERING_INFO`, `UNSUBSCRIBE`), store (`STORE_SEGMENTS`, `FAMILY_LIST_SEARCH`, `STORE_PACKAGES_SEARCH`, `REDEEMABLES`), Family Plan/Circle (`FAMILY_PLAN_*`, `CIRCLE_*`), registrasi (`DUKCAPIL`), payment (`PAYMENT_METHODS_OPTION`, `SETTLEMENT_MULTIPAYMENT`, `SETTLEMENT_QRIS`, `SETTLEMENT_EWALLET`, `PENDING_DETAIL`), loyalty (`BOUNTIES_EXCHANGE`, `LOYALTIES_EXCHANGE`, `BOUNTIES_ALLOTMENT`).
- `CIAMEndpoint` — `OTP` (`/realms/xl-ciam/auth/otp`), `EXTEND_SESSION` (`/realms/xl-ciam/auth/extend-session`), `TOKEN` (`/realms/xl-ciam/protocol/openid-connect/token`).
- `MigrationType` — `NONE`, `PRE_TO_PRIOH`, `PRIOH_TO_PRIO`, `PRIO_TO_PRIOH`, plus tuple `ALL`.
- `PaymentMethod` — `BALANCE`, `QRIS` (e-wallet memakai string literal `DANA`/`SHOPEEPAY`/`GOPAY`/`OVO` di [ewallet.py](../api/purchase/ewallet.md)).
- `PaymentFor` — `BUY_PACKAGE`, `SHARE_PACKAGE`, `REDEEM_VOUCHER`.
- `HttpHeader` — nama header backend utama: `host`, `content-type`, `user-agent`, `x-api-key`, `authorization`, `x-hv`, `x-signature-time`, `x-signature`, `x-request-id`, `x-request-at`, `x-version-app`.
- `CIAMHeader` — nama header CIAM: `Ax-Device-Id`, `Ax-Fingerprint`, `Ax-Request-At`, `Ax-Request-Device`, `Ax-Request-Device-Model`, `Ax-Request-Id`, `Ax-Substype`, `Ax-Api-Signature`, `Accept-Encoding`.

## Alur/Detail penting

- `MigrationType.ALL` dipakai brute-force di [api/packages.py](../api/packages.md) `get_family`.
- `PaymentFor.REDEEM_VOUCHER` memicu opsi bounty/loyalty di [ui/package/details.py](../ui/package/details.md).

## Catatan

- Jangan mengubah string path tanpa sinkron dengan payload tiap modul API; path ikut disign (lihat [core/crypto.md](../core/crypto.md)).