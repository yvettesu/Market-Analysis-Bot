from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import pymysql

from market_hotspot.models import Instrument, Snapshot


MIGRATION = Path(__file__).resolve().parents[1] / "migrations" / "001_market_hotspot.sql"


def db_config(db_url: str | None = None) -> dict[str, Any]:
    value = db_url or os.getenv("DB_URL")
    if not value:
        raise RuntimeError("Missing DB_URL. Use mysql+pymysql://user:password@host:3306/database")
    parsed = urlparse(value)
    if parsed.scheme not in {"mysql", "mysql+pymysql"}:
        raise ValueError("DB_URL must use mysql:// or mysql+pymysql://")
    return {
        "host": parsed.hostname or "127.0.0.1", "port": parsed.port or 3306,
        "user": unquote(parsed.username or ""), "password": unquote(parsed.password or ""),
        "database": parsed.path.lstrip("/"), "charset": (parse_qs(parsed.query).get("charset") or ["utf8mb4"])[0],
        "autocommit": False,
    }


class MySQLStore:
    def __init__(self, db_url: str | None = None) -> None:
        self.connection = pymysql.connect(**db_config(db_url))

    def close(self) -> None:
        self.connection.close()

    def migrate(self) -> None:
        statements = [statement.strip() for statement in MIGRATION.read_text(encoding="utf-8").split(";") if statement.strip()]
        with self.connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
        self.connection.commit()

    def upsert_snapshot(self, snapshot: Snapshot, collected_at: datetime) -> None:
        instrument = snapshot.instrument
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO market_instruments
                   (watch_symbol, underlying_asset, venue, target_venue, product_type, instrument_id,
                    trading_status, capabilities, discovered_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE watch_symbol=VALUES(watch_symbol), capabilities=VALUES(capabilities),
                   trading_status=VALUES(trading_status), discovered_at=VALUES(discovered_at)""",
                (instrument.watch_symbol, instrument.underlying_asset, instrument.venue, instrument.target_venue,
                 instrument.product_type, instrument.instrument_id, instrument.trading_status,
                 json.dumps(instrument.capabilities), collected_at),
            )
            cursor.execute("SELECT id FROM market_instruments WHERE venue=%s AND product_type=%s AND instrument_id=%s", (instrument.venue, instrument.product_type, instrument.instrument_id))
            row = cursor.fetchone()
            instrument_key = row[0]
            cursor.execute(
                """INSERT INTO market_price_snapshot
                   (instrument_id, source_ts, collected_at, available_at, last_price, price_change_24h,
                    volume_24h, funding_rate, quality_status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE collected_at=VALUES(collected_at), last_price=VALUES(last_price),
                   price_change_24h=VALUES(price_change_24h), volume_24h=VALUES(volume_24h),
                   funding_rate=VALUES(funding_rate), quality_status=VALUES(quality_status)""",
                (instrument_key, snapshot.source_ts, collected_at, collected_at, snapshot.last_price,
                 snapshot.price_change_24h, snapshot.volume_24h, snapshot.funding_rate, snapshot.quality_status),
            )
            if snapshot.oi_contracts is not None:
                cursor.execute(
                    """INSERT INTO market_oi_snapshot
                       (instrument_id, source_ts, collected_at, oi_contracts, oi_usd, oi_unit, quality_status)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)
                       ON DUPLICATE KEY UPDATE collected_at=VALUES(collected_at), oi_contracts=VALUES(oi_contracts),
                       oi_usd=VALUES(oi_usd), quality_status=VALUES(quality_status)""",
                    (instrument_key, snapshot.source_ts, collected_at, snapshot.oi_contracts, snapshot.oi_usd,
                     "contracts", snapshot.quality_status),
                )
        self.connection.commit()
