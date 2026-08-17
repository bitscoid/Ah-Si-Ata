# ahsiata/ui/package/list.py — daftar paket per family

Daftar semua variant/option satu family → pilih → buka detail paket.

## Ringkasan

`get_packages_by_family` (menu CLI `5`, dan target PLP dari store/redeemables/bonus) memuat family via `get_family`, menampilkan variant (berlabel) dengan option bernomor, lalu meneruskan pilihan ke `show_package_details` beserta `option_order`.

## Fungsi

- `get_packages_by_family(family_code: str, is_enterprise: bool | None = None, migration_type: str | None = None) -> list[dict] | None` — loop:
  - Header: nama family, family code, tipe, jumlah variant.
  - `packages` diakumulasi per option: `{number, variant_name, option_name, price, code, option_order}`.
  - `B` — kembali, return daftar.
  - `<n>` — `show_package_details(api_key, tokens, code, is_enterprise, option_order=option_order)`.

## Alur/Detail penting

- Harga memakai `format_price`; `option_order` dipakai agar opsi `0` (bookmark) muncul di detail.
- `is_enterprise`/`migration_type` diteruskan ke `get_family` (brute-force terjadi di sana bila `None`).

## Catatan

- Daftar dibangun ulang dari `data` tiap loop (tidak ada cache).