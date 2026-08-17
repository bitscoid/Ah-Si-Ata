# ahsiata/ui/circle/info.py — info Circle & bonus

Layar Circle (CLI `9`): status grup, anggota (MSISDN didekripsi), kuota, spending tracker, undang/hapus/terima member, bonus, dan pembuatan Circle.

## Ringkasan

Satu layar komprehensif. Membaca `get_group_data` → `get_group_members` → `spending_tracker`; setiap MSISDN anggota didekripsi via `decrypt_circle_msisdn`. Opsi: undang (dengan validasi), hapus (proteksi parent & member terakhir), terima undangan (status `INVITED`), bonus list (`PLP`/`PDP`), dan buat Circle baru saat user belum tergabung.

## Fungsi

- `show_circle_creation(api_key, tokens) -> None` — input parent name, group name, MSISDN + nama member → `create_circle`.
- `_show_bonus_list(api_key, tokens, parent_subs_id, family_id) -> None` — `get_bonus_data` → daftar bonus (`name`, `bonus_type`, `action_type`, `action_param`); `PLP` → `get_packages_by_family`, `PDP` → `show_package_details`.
- `show_circle_info(api_key, tokens) -> None` — loop utama:
  - Tanpa `group_id` → tawarkan buat Circle; `group_status == "BLOCKED"` → tolak.
  - Cari member `member_role == "PARENT"` → `parent_member_id`, `parent_subs_id`, MSISDN parent (dekripsi).
  - Tampil: nama grup, owner, paket (`benefit.allocation .remaining`), spending (`spend`/`target`), list member (MSISDN terdekripsi, `member_role`, `join_date`, `slot_type`, `status`, pemakaian; penanda `(You)`).
  - Opsi:
    - `1` Undang: `validate_circle_member` → sukses hanya jika `data.response_code == "200-2001"` → `invite_circle_member` (sukses jika `response_code == "200-00"`).
    - `2` Bonus: `_show_bonus_list`.
    - `d` Hapus: tolak parent dan saat `len(members) == 2` (member terakhir); `remove_circle_member(..., is_last)`.
    - `a` Terima: hanya member `status == "INVITED"` → `accept_circle_invitation`.
    - `b` kembali.

## Alur/Detail penting

- Parent MSISDN juga didekripsi; `parrent_msisdn` ditampilkan di header (typo `parrent` dipertahankan).
- `my_msisdn` dari `SESSION.get_active_user()["number"]` untuk penanda `(You)`.

## Catatan

- Blokir ketika respons non-`SUCCESS` di salah satu panggilan; tidak ada retry.