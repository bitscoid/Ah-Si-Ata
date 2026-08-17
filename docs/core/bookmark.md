# ahsiata/core/bookmark.py — penyimpanan bookmark paket

Singleton `BOOKMARK` berbasis file `bookmark.json` (relatif-CWD).

## Ringkasan

Menyimpan daftar paket favorit. Tidak menyentuh disk saat import; state dimuat satu kali via `BOOKMARK.initialize()` dari entry point (`cli.main()`). File dibuat `[]` jika belum ada. Dedup saat tambah; migrasi skema otomatis untuk entri lama.

## Kelas

- `Bookmark` — singleton via `__new__` + flag `_initialized` (instance: `BOOKMARK`).
  - `initialize() -> None` — muat dari disk satu kali; buat `[]` jika file belum ada.
  - `load_bookmark() -> None` — baca file, lalu `_ensure_schema()`.
  - `save_bookmark() -> None` / `_save(data: list[dict]) -> None` — tulis file (indent 4).
  - `_ensure_schema() -> None` — tambah `family_name: ""` dan `order: 0` ke entri yang kurang; simpan ulang jika berubah.
  - `add_bookmark(family_code: str, family_name: str, is_enterprise: bool, variant_name: str, option_name: str, order: int) -> bool` — dedup key `(family_code, variant_name, order)`; print warn/ok; simpan.
  - `remove_bookmark(family_code: str, is_enterprise: bool, variant_name: str, order: int) -> bool` — hapus entri cocok; print ok/warn.
  - `get_bookmarks() -> list[dict]` — salinan daftar.

## Alur/Detail penting

- Skema item: `{family_name, family_code, is_enterprise, variant_name, option_name, order}`.
- Pemakaian: tambah dari opsi `0` di [ui/package/details.py](../ui/package/details.md); baca/dihapus di [ui/bookmark.py](../ui/bookmark.md).
- `_filepath` class-level = `"bookmark.json"`.

## Catatan

- Pesan UI memakai `ok`/`warn` dari [ui/style.py](../ui/style.md) — modul core bergantung pada modul ui.