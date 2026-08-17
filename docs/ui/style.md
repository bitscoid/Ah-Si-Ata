# ahsiata/ui/style.py — style ANSI & helper teks

Kode warna ANSI + helper format untuk seluruh output terminal.

## Ringkasan

Kelas `C` berisi escape code warna/bold; fungsi `p`, `title`, `rule`, `center` menyusun teks berwarna; `ok`/`fail`/`warn`/`info` memberi emoji + warna untuk pesan status. Dipakai hampir semua modul UI dan beberapa modul core (mis. [core/bookmark.py](../core/bookmark.md)).

## Kelas/Fungsi

- `C` — konstanta ANSI: `RESET`, `BOLD`, `DIM`, warna dasar (`RED`…`WHITE`), warna terang (`B_RED`…`B_WHITE`), background (`BG_*`).
- `p(text, *codes) -> str` — bungkus teks dengan `''.join(codes)` + `RESET`; tanpa kode → `str(text)`.
- `disp_w(s: str) -> int` — lebar tampilan; karakter `east_asian_width in "WF"` (emoji/CJK) dihitung 2.
- `center(text, width) -> str` — rata tengah dengan padding simetris.
- `title(text, char="=", color=C.CYAN, width=55) -> str` — banner `===== Text =====` berwarna.
- `rule(char="-", color="", width=55) -> str` — garis horizontal.
- `ok(msg) -> str` / `fail(msg) -> str` / `warn(msg) -> str` / `info(msg) -> str` — `✅`/`❌`/`⚠️`/`💡` + warna `GREEN`/`RED`/`YELLOW`/`CYAN`.

## Alur/Detail penting

- Di Windows (`os.name == "nt"`) aktifkan pemrosesan ANSI via `os.system("")` di import — no-op di platform lain.

## Catatan

- `disp_w` dipakai bersama `center` dan layout dua kolom (mis. [ui/store/search.md](store/search.md)) supaya emoji tidak merusak perataan.