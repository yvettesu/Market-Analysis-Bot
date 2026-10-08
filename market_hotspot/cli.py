from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from market_hotspot.sources.binance import BinanceFuturesSource
from market_hotspot.storage import MySQLStore


DEFAULT_WATCHLIST = "XRPUSDT,DOGEUSDT,ADAUSDT,TRXUSDT,ZECUSDT,HYPEUSDT,AVAXUSDT,WLDUSDT,WLFIUSDT,ALEOUSDT,TSLAUSDT,NVDAUSDT,PLTRUSDT"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manual Market Hotspot Intelligence MVP.")
    parser.add_argument("command", choices=("discover", "ingest-market", "init-db"))
    parser.add_argument("--symbols", default=DEFAULT_WATCHLIST)
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--persist", action="store_true", help="Write discovered market snapshots to MySQL using DB_URL.")
    parser.add_argument("--db-url", help="Override DB_URL; never commit credentials.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "init-db":
        store = MySQLStore(args.db_url)
        try:
            store.migrate()
        finally:
            store.close()
        print("MySQL migrations applied")
        return 0
    source = BinanceFuturesSource()
    store = MySQLStore(args.db_url) if args.persist else None
    rows = []
    for symbol in (part.strip().upper() for part in args.symbols.split(",") if part.strip()):
        try:
            instrument = source.discover(symbol)
            if not instrument:
                rows.append({"watch_symbol": symbol, "status": "UNAVAILABLE", "reason": "No Binance USD-M perpetual discovered"})
            elif args.command == "discover":
                rows.append({**asdict(instrument), "status": "VALID"})
            else:
                snapshot = source.snapshot(instrument)
                if store:
                    store.upsert_snapshot(snapshot, datetime.now(timezone.utc))
                rows.append({**asdict(snapshot), "status": "VALID"})
        except Exception as exc:  # Public API errors must not turn into fabricated signals.
            rows.append({"watch_symbol": symbol, "status": "UNAVAILABLE", "reason": str(exc)})
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / f"{args.command}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps(rows, ensure_ascii=False, default=str, indent=2) + "\n", encoding="utf-8")
    if store:
        store.close()
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
