"""Transaction history menu."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ahsiata.api.transactions import get_transaction_history
from ahsiata.ui.style import C, p, title, rule, info, fail
from ahsiata.ui.utils import clear_screen, pause


def show_transaction_history(api_key: str, tokens: dict) -> None:
    clear_screen()
    print(title("🧾 Riwayat Transaksi", color=C.CYAN))

    res = get_transaction_history(api_key, tokens)
    if not isinstance(res, dict):
        print(fail(f"Gagal ambil riwayat: {res}"))
        pause()
        return

    transactions = res.get("list", [])
    if not transactions:
        print(info("Tidak ada transaksi"))
        pause()
        return

    gmt7 = timezone(timedelta(hours=7))
    for idx, tx in enumerate(transactions):
        ts = tx.get("timestamp", 0)
        ts_str = datetime.fromtimestamp(ts, tz=gmt7).strftime("%Y-%m-%d %H:%M:%S")
        title_tx = tx.get("title", "N/A")
        price = tx.get("price", "N/A")
        print(f"{idx}. {p(ts_str, C.DIM)} | {p(title_tx, C.BOLD, C.WHITE)}")
        print(f"   💳 Metode: {tx.get('payment_method_label', 'N/A')}")
        print(f"   📊 Status: {tx.get('payment_status', 'N/A')}")
        print(f"   {p(str(price), C.BOLD, C.YELLOW)}")
        print(rule(color=C.BLUE))

    print("00. ↩️ Keluar")
    pause()
