# ahsiata/ui/store/segments.py — menu segmen store

Menu segmen/promo store (CLI `P`): kategori segmen → banner → detail paket.

## Ringkasan

`show_store_segments_menu` memuat `get_segments(is_enterprise)`, menampilkan segmen (`A`, `B`, …) dengan banner bernomor (`a1`, `b2`, …), lalu pilihan `<huruf><angka>` membuka `show_package_details` memakai `action_param` banner sebagai option code.

## Fungsi

- `show_store_segments_menu(is_enterprise: bool) -> None` — loop:
  - `B` — kembali.
  - Pilihan `A1`-style: `seg_idx = ord(choice[0].upper()) - ord("A")`, `banner_idx = int(choice[1:]) - 1`; validasi rentang.
  - `option_code = banners[banner_idx].get("action_param", "")` → `show_package_details(api_key, tokens, option_code, False)` (import lokal di dalam blok).

## Alur/Detail penting

- Data: `res["data"]["store_segments"][]` dengan `title` dan `banners[]` (`title`, `discounted_price`, `action_param`).
- Harga banner tampil hanya jika `discounted_price` numerik.

## Catatan

- `is_enterprise` dipakai untuk fetch, tetapi detail dibuka dengan `False`.