# main.py — wrapper tipis entry point

Satu-satunya isi: `from ahsiata.cli import main` lalu panggil `main()` saat dijalankan langsung.

## Ringkasan

File terkecil di repo (9 baris). Ada agar jalur historis `python main.py` tetap berfungsi. Semua logika ada di `ahsiata.cli.main()` — tiga cara meluncurkan CLI setara: `python main.py`, `python -m ahsiata` (via `ahsiata/__main__.py`), dan console script `ahsiata` (via `pyproject.toml`).

## Fungsi

- `main()` — delegasi ke `ahsiata.cli.main()`. Dipanggil hanya jika `__name__ == "__main__"`.

## Alur/Detail penting

- Tidak ada state atau konfigurasi di file ini; CWD adalah direktori kerja proyek (file state `refresh-tokens.json`, `active.number`, `bookmark.json`, `ax.fp` relatif-CWD).

## Catatan

- Docstring menegaskan ini *thin wrapper*; jangan tambahkan logika di sini.
- Lihat [cli.md](ahsiata/cli.md) untuk entry point sebenarnya.
