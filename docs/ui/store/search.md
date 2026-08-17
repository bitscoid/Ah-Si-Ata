# ahsiata/ui/store/search.py — family list & store packages

Menu pencarian store: daftar family dua kolom (CLI `F`) dan daftar paket store dengan paginasi (CLI `S`).

## Ringkasan

Dua menu terpisah: `show_family_list_menu` memakai `get_family_list` → pilih family → `get_packages_by_family`; `show_store_packages_menu` memakai `get_store_packages` → daftar `results_price_only` dipaginasi 15 item/halaman → `show_package_details`.

## Fungsi

- `show_family_list_menu(subs_type: str, is_enterprise: bool) -> None` — keluarga dalam 2 kolom (lebar kolom dari `disp_w`); `<n>` → `get_packages_by_family(fam["id"], is_enterprise)`.
- `show_store_packages_menu(subs_type: str, is_enterprise: bool) -> None` — paginasi:
  - `page_size = 15`; `N` next / `P` prev (wrap modulo halaman); tampil `| Hal X/Y`.
  - Harga: `discounted_price` fallback `price`; nama: `title` fallback `package_name`/`name`.
  - `<n>` → `show_package_details(api_key, tokens, pkg["package_option_code"], is_enterprise)` jika ada option code.

## Alur/Detail penting

- Data store packages dari `res["data"]["results_price_only"]` — bukan daftar lengkap (server sudah mengirim versi ringkas).
- Tidak ada `text_search` interaktif — filter kosong dikirim apa adanya (lihat [api/catalog.md](../../api/catalog.md)).

## Catatan

- `show_store_packages_menu` gagal total (tidak loop) saat `get_store_packages`/`results_price_only` kosong.