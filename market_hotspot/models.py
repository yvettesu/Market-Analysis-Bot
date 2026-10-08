from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Instrument:
    watch_symbol: str
    underlying_asset: str
    venue: str
    target_venue: str
    product_type: str
    instrument_id: str
    capabilities: tuple[str, ...]
    trading_status: str = "TRADING"


@dataclass(frozen=True)
class Snapshot:
    instrument: Instrument
    source_ts: datetime
    last_price: Optional[float]
    price_change_24h: Optional[float]
    volume_24h: Optional[float]
    oi_contracts: Optional[float]
    oi_usd: Optional[float]
    funding_rate: Optional[float]
    quality_status: str = "VALID"
