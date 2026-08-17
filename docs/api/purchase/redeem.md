# ahsiata/api/purchase/redeem.py — bounty, loyalty, bounty allotment

Flow redeem dengan `payment_for: "REDEEM_VOUCHER"`: klaim bounty (saldo), beli dengan poin loyalty, kirim bonus ke MSISDN lain.

## Ringkasan

Tiga settlement mandiri yang memakai skeleton `post_signed_payload` dengan signature khusus (bounty/loyalty/allotment) dari [base.py](base.md). Tidak memakai `intercept_page`/`fetch_payment_token` — token & timestamp datang dari detail paket ([api/packages.py](../packages.md) `get_package` → `token_confirmation`/`timestamp`).

## Fungsi

- `settlement_bounty(api_key, tokens, token_confirmation, ts_to_sign, payment_target, price, item_name="")` — `POST api/v8/personalization/bounties-exchange`; payload mirip balance (`payment_method: "BALANCE"`, `payment_for: "REDEEM_VOUCHER"`, `total_amount: 0`, `items` satu entry `{item_code, product_type: "", item_price, item_name, tax: 0}` — tanpa `token_confirmation` di item). Signature: `make_bounty_signature`. Sukses: `ok("Bounty berhasil diklaim.")`.
- `settlement_loyalty(api_key, tokens, token_confirmation, ts_to_sign, payment_target, price)` — `POST gamification/api/v8/loyalties/tiering/exchange`; payload ringkas `{item_code, amount: 0, partner: "", item_name: "", points: price, timestamp, token_confirmation}` — bayar dengan **poin** (harga = poin). Signature: `make_loyalty_signature`.
- `bounty_allotment(api_key, tokens, ts_to_sign, destination_msisdn, item_name, item_code, token_confirmation)` — `POST gamification/api/v8/loyalties/tiering/bounties-allotment`; payload `{destination_msisdn, item_code, item_name, timestamp, token_confirmation}`. Signature: `make_bounty_allotment_signature` (MSISDN tujuan ikut disign).

## Alur/Detail penting

- Opsi `B` / `BA` / `L` hanya tampil di [ui/package/details.py](../../ui/package/details.md) saat `package_family.payment_for == "REDEEM_VOUCHER"`.
- `ts_to_sign` = `package["timestamp"]` dari `get_package`.

## Catatan

- Gagal → `fail` + `None`; respons sukses → print `ok` lalu dikembalikan.