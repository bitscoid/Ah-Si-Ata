# ahsiata/ui/store/redeemables.py — menu redeemables

Daftar kategori redeemable (CLI `C`), pilih paket → buka family list atau detail.

## Ringkasan

Memuat `get_redeemables(is_enterprise)` — kategori dengan paket — lalu pilihan `A1`, `B2`, dst. (`<huruf><angka>`). Aksi diteruskan ke `get_packages_by_family` (PLP) atau `show_package_details` (PDP).

## Fungsi

- `show_redeemables_menu(is_enterprise: bool) -> None` — loop:
  - `B` — kembali.
  - Pilihan `<letter><digits>`: `letter_idx = ord(choice[0].upper()) - ord("A")`, `pkg_idx = int(choice[1:]) - 1`; validasi rentang kategori/paket.
  - `selected["action_type"]`: `"PLP"` → `get_packages_by_family(action_param)`; `"PDP"` → `show_package_details(api_key, tokens, action_param, False)`; lain → `fail("Tipe aksi yang tidak ditangani: ...")`.

## Alur/Detail penting

- Data: `res["data"]["categories"][]` dengan `category_name` dan `redeemables[]` (`name`, `action_type`, `action_param`).

## Catatan

- Docstring: nama file diperbaiki dari `redemables.py` layout lama.