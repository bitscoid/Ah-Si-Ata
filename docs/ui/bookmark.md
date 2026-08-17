# ahsiata/ui/bookmark.py — menu bookmark

Daftar bookmark, buka detail paket, hapus bookmark.

## Ringkasan

Menampilkan isi `BOOKMARK.get_bookmarks()`; pilihan nomor meresolve paket via `get_family` + `get_package_details` lalu membuka [show_package_details](package/details.md). Hapus via `D`.

## Fungsi

- `show_bookmark_menu() -> None` — loop:
  - `B` — kembali.
  - `D` — input nomor urut → `BOOKMARK.remove_bookmark(...)`.
  - `<n>` — ambil `bm`, `get_family(api_key, tokens, bm["family_code"], bm["is_enterprise"])`, `get_package_details(api_key, tokens, bm["family_code"], bm["variant_name"], bm["order"], bm["is_enterprise"])`; ambil `package_option.package_option_code` → `show_package_details(..., bm["is_enterprise"])`.

## Alur/Detail penting

- Note: `get_package_details` dipanggil dengan `variant_name` sebagai argumen `variant_code` — resolusi mengandalkan kecocokan nama variant (lihat [api/packages.py](../api/packages.md)).
- Bookmark tanpa `option_order` tetap bisa dibuka karena diganti `order` dari bookmark.

## Catatan

- Tidak ada aksi "buka paket my packages" — hanya bookmark tersimpan.