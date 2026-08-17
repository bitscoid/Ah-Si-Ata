# ahsiata/api/packages.py — katalog & detail paket

Endpoint family, detail paket, addons, dan unsubscribe.

## Ringkasan

Fungsi inti untuk resolve paket. `get_family` melakukan brute-force kombinasi `is_enterprise ∈ {False, True}` × `migration_type ∈ MigrationType.ALL` sampai mendapat family bernama non-kosong. `get_package_details` menggabungkan family → variant → option → detail dalam satu panggilan.

## Fungsi

- `get_family(api_key, tokens, family_code, is_enterprise=None, migration_type=None) -> dict | None` — `api/v8/xl-stores/options/list`; payload penuh (13 kunci: `is_show_tagging_tab`, `is_dedicated_event`, `is_transaction_routine: False`, `migration_type`, `package_family_code`, `is_autobuy: False`, `is_enterprise`, `is_pdlp: True`, `referral_code: ""`, `is_migration: False`, `lang`). Berhenti di kombinasi pertama dengan `status == "SUCCESS"` dan nama family non-kosong; return `res["data"]`.
- `get_package(api_key, tokens, package_option_code, package_family_code="", package_variant_code="") -> dict | None` — `api/v8/xl-stores/options/detail`; payload 12 kunci (`migration_type: "NONE"`, `family_role_hub: ""`, `is_shareable: False`, `is_upsell_pdp: False`, dll.); return `res["data"]`.
- `get_addons(api_key, tokens, package_option_code) -> dict | None` — `api/v8/xl-stores/options/addons-pinky-box`; return `res["data"]`.
- `get_package_details(api_key, tokens, family_code, variant_code, option_order, is_enterprise=None, migration_type=None) -> dict | None` — `get_family` → cari variant by `package_variant_code` → option by `order == option_order` → `get_package(option_code)`. Return detail penuh.
- `unsubscribe(api_key, tokens, quota_code, product_domain, product_subscription_type) -> bool` — `api/v8/packages/unsubscribe`; payload `{product_subscription_type, quota_code, product_domain, unsubscribe_reason_code: "", family_member_id: ""}`; sukses jika `res["code"] == "000"` (exception → `False`).

## Alur/Detail penting

- Pemanggil: `get_package_details` dipakai decoy ([core/decoy.py](../core/decoy.md)), bookmark ([ui/bookmark.py](../ui/bookmark.md)), HOT ([ui/hot.py](../ui/hot.md)); `get_family` dipakai [ui/package/list.py](../ui/package/list.md) dan [ui/purchase/loop.py](../ui/purchase/loop.md).
- Nilai penting pada detail: `package_option.package_option_code/.price/.name`, `package_family.payment_for/.plan_type`, `token_confirmation`, `timestamp`.

## Catatan

- Dekripsi gagal dari [client.py](client.md) mengembalikan str — fungsi di sini menangani dengan `isinstance(res, dict)` checks.