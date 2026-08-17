# ahsiata/api/catalog.py — endpoint katalog store

Segments, family list, store packages (v9), dan redeemables.

## Ringkasan

Empat fungsi POST tipis di atas `send_api_request`; masing-masing memvalidasi `status == "SUCCESS"` dan mencetak `fail` lalu `return None` jika gagal. Payload baku `{is_enterprise, lang: "en"}` plus kunci spesifik.

## Fungsi

- `get_segments(api_key, tokens, is_enterprise=False) -> dict | None` — `api/v8/configs/store/segments`; payload `{is_enterprise, lang}`.
- `get_family_list(api_key, tokens, subs_type="PREPAID", is_enterprise=False) -> dict | None` — `api/v8/xl-stores/options/search/family-list`; payload `{is_enterprise, subs_type, lang}`.
- `get_store_packages(api_key, tokens, subs_type="PREPAID", is_enterprise=False) -> dict | None` — `api/v9/xl-stores/options/search`; payload berisi `filters` (4 filter kosong berbasis `unit`/`id`/`type`: `FIL_SEL_P` PRICE, `FIL_SEL_MQ` DATA_TYPE, `FIL_PKG_N` PACKAGE_NAME, `FIL_SEL_V` VALIDITY), `substype`, `text_search: ""`, `lang`.
- `get_redeemables(api_key, tokens, is_enterprise=False) -> dict | None` — `api/v8/personalization/redeemables`; payload `{is_enterprise, lang}`.

## Alur/Detail penting

- Pemanggil UI: [ui/store/segments.py](../ui/store/segments.md) (segments), [ui/store/search.py](../ui/store/search.md) (family list & store packages), [ui/store/redeemables.py](../ui/store/redeemables.md) (redeemables).
- Respons store packages dipakai `results_price_only`; redeemables memakai `data.categories[].redeemables[]` dengan `action_type`/`action_param` (PLP/PDP).

## Catatan

- `Endpoint.STORE_PACKAGES_SEARCH` adalah `api/v9/...` (satu-satunya endpoint v9 di repo).