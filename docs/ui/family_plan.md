# ahsiata/ui/family_plan.py — menu Family Plan

Info plan, ganti member, hapus member, batas kuota.

## Ringkasan

`show_family_info` (menu CLI `8`) menampilkan status Family Plan (Akrab Organizer): tipe plan, parent, kuota total/sisa, tanggal akhir, daftar member dengan pemakaian. Aksi: ganti member (validasi MSISDN), `del <slot>`, `limit <slot> <MB>`.

## Fungsi

- `show_family_info(api_key, tokens) -> None` — loop:
  - `B` — kembali; `plan_type == ""` → "bukan organizer", keluar.
  - `1` — Ganti member: input slot (harus kosong), MSISDN tujuan, alias; `validate_msisdn` (cek `family_plan_role == "NO_ROLE"`), konfirmasi `y`, `change_member`.
  - `del <slot>` — hapus member slot (tolak slot kosong), konfirmasi, `remove_member`.
  - `limit <slot> <MB>` — `set_quota_limit(original=quota_allocated, new=MB*1024*1024, family_member_id)`.

## Alur/Detail penting

- Sumber data: `get_family_data` → `data.member_info` (`plan_type`, `parent_msisdn`, `members[]`, `total_quota`, `remaining_quota`, `end_date`); per member: `msisdn`, `alias`, `member_type`, `add_chances`/`total_add_chances`, `usage.quota_allocated`/`quota_used`, `family_member_id`, `slot_id`.
- Kuota ditampilkan via `format_quota_byte` ([ui/utils.md](utils.md)).

## Catatan

- MSISDN di layar ini **tidak** dienkripsi (beda dengan Circle).
- Waktu `end_date` di-`datetime.fromtimestamp` (zona lokal).