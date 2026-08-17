# ahsiata/__main__.py — entry `python -m ahsiata`

Memungkinkan peluncuran `python -m ahsiata` untuk menjalankan CLI.

## Ringkasan

Dua baris: import `main` dari `ahsiata.cli`, lalu panggil langsung `main()` di level modul (tanpa guard `if __name__ == "__main__"` — aman karena modul hanya dieksekusi sebagai `__main__`).

## Fungsi

- Tidak ada fungsi; eksekusi langsung `ahsiata.cli.main()`.

## Alur/Detail penting

- Tidak menginisialisasi apa pun sendiri; `SESSION.initialize()` dan `BOOKMARK.initialize()` dipanggil di dalam `cli.main()`.

## Catatan

- Konsol script `ahsiata` (pyproject.toml) mengarah langsung ke `ahsiata.cli:main`, bukan ke modul ini.
