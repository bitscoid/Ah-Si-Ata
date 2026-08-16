"""Transaction history menu."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ahsiata.api.transactions import get_transaction_history
from ahsiata.ui.utils import clear_screen, pause


def show_transaction_history(api_key: str, tokens: dict) -> None:
    clear_screen()
    print("-" * 55)
    print("Riwayat Transaksi".center(55))
    print("-" * 55)

    res = get_transaction_history(api_key, tokens)
    if not isinstance(res, dict):
        print(f"Gagal mengambil riwayat transaksi: {res}")
        pause()
        return

    transactions = res.get("list", [])
    if not transactions:
        print("Tidak ada transaksi.")
        pause()
        return

    gmt7 = timezone(timedelta(hours=7))
    for idx, tx in enumerate(transactions):
        ts = tx.get("timestamp", 0)
        ts_str = datetime.fromtimestamp(ts, tz=gmt7).strftime("%Y-%m-%d %H:%M:%S")
        title = tx.get("title", "N/A")
        price = tx.get("price", "N/A")
        print(f"{idx}. {ts_str} | {title}")
        print(f"   Metode Pembayaran: {tx.get('payment_method_label', 'N/A')}")
        print(f"   Status Pembayaran: {tx.get('payment_status', 'N/A')}")
        print(f"   {price}")
        print("-" * 55)

    print("00. Kembali ke Menu Utama")
    pause()
