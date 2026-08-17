# ahsiata/ui/package/details.py — detail paket & paket saya

Layar detail paket (menu `4` CLI, dan tujuan semua alur browse) + `fetch_my_packages` (menu `2`).

## Ringkasan

File UI terbesar. `show_package_details` memuat detail satu paket via `get_package`, menampilkan benefit/addon/T&C, lalu loop opsi pembelian: saldo, e-wallet, QRIS, empat varian decoy, pembelian N-kali, dan (untuk `REDEEM_VOUCHER`) bounty/loyalty/allotment. `fetch_my_packages` menampilkan kuota aktif dan mendukung unsubscribe.

## Fungsi

- `_print_benefits(benefits: list[dict]) -> None` — daftar benefit; `VOICE` → menit, `TEXT` → SMS, `DATA` → `format_quota_byte`, lain → mentah; tanda `is_unlimited` → `♾️`.
- `_print_summary(package: dict) -> tuple[str, int, str, str, str]` — header: nama gabungan, harga, `payment_for`, masa aktif, poin, plan, family code, parent code; return `(title, price, payment_for, family_code, parent_code)`.
- `show_package_details(api_key, tokens, package_option_code, is_enterprise, option_order=-1)` — loop opsi (detail di bawah). Return `True` saat pembelian dilakukan, `False` saat batal/kembali.
- `fetch_my_packages() -> None` — kuota aktif & unsubscribe.

## Alur/Detail penting — menu `show_package_details`

- Persiapkan: `payment_items = [PaymentItem(item_code, "", price, "<variant> <option>", 0, token_confirmation)]`; `payment_for = package_family.payment_for or "BUY_PACKAGE"`.
- Opsi:
  - `1` / `2` / `3` — `settlement_balance(..., ask_overwrite=True)` / `show_multipayment` / `show_qris_payment` (`ask_overwrite=True`).
  - `4` / `5` — Pulsa+Decoy / V2: `DECOY.get_decoy("balance")` → `get_package` → `settle_with_decoy(..., token_confirmation_idx=1 untuk "5")`; untuk `5`, `payment_for_arg = "🤫"` (bukan `BUY_PACKAGE`).
  - `6` / `7` — QRIS+Decoy / V2: `DECOY.get_decoy("qris" / "qris0")` → `append_decoy_item` + `show_qris_payment(..., payment_for="SHARE_PACKAGE", token_confirmation_idx=1)`; warn "trial & error, 0 = malformed".
  - `8` — `purchase_n_times_by_option_code(n, option_code, use_decoy, delay, token_confirmation_idx=1)`.
  - `0` (hanya jika `option_order != -1`) — `BOOKMARK.add_bookmark(...)`.
  - `B`/`BA`/`L` (hanya jika `payment_for == "REDEEM_VOUCHER"`) — `settlement_bounty` / `bounty_allotment` / `settlement_loyalty` memakai `token_confirmation` + `timestamp` dari paket.
  - `B` juga = kembali (string `"b"` di-check lebih dulu).

## `fetch_my_packages`

- `POST api/v8/packages/quota-details` (`Endpoint.QUOTA_DETAILS`) payload `{is_enterprise: False, lang, family_member_id: ""}`.
- Per kuota: cetak nama, benefit (dengan sisa/total), grup, kode kuota; family code ditebus via `get_package(quota_code)`.
- Pilihan: `<n>` → `show_package_details(api_key, tokens, quota_code, False)`; `D<n>` → konfirmasi → `unsubscribe(...)` (cek `code == "000"` di [api/packages.py](../../api/packages.md)).

## Catatan

- Quirk decoy V2: `payment_for="🤫"` dikirim apa adanya ke signature payment — literan tidak standar, dipertahankan karena berfungsi bagi server target.
- Opsi `0` bookmark hanya muncul bila datang dari daftar family (`option_order != -1`), bukan dari option code manual.