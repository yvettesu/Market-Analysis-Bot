from __future__ import annotations

import json
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from market_hotspot.models import Instrument, Snapshot


class BinanceFuturesSource:
    base_url = "https://fapi.binance.com"
    # These watch labels must be resolved by a stock-product source. A matching
    # Binance symbol alone is not proof that it tracks the listed equity.
    stock_watch_symbols = {"TSLAUSDT", "NVDAUSDT", "PLTRUSDT"}

    def _get(self, path: str, **params):
        request = Request(f"{self.base_url}{path}?{urlencode(params)}", headers={"User-Agent": "Market-Analysis-Bot/0.1"})
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))

    def discover(self, watch_symbol: str) -> Instrument | None:
        symbol = watch_symbol.upper()
        if symbol in self.stock_watch_symbols:
            return None
        data = self._get("/fapi/v1/exchangeInfo")
        listed = next((item for item in data["symbols"] if item["symbol"] == symbol and item["status"] == "TRADING"), None)
        if not listed:
            return None
        return Instrument(symbol, symbol.removesuffix("USDT"), "BINANCE", "BINANCE", "CRYPTO_PERP", symbol, ("PRICE", "VOLUME", "OI", "FUNDING", "ORDERBOOK", "TAKER", "TOP_TRADER_RATIO"))

    def snapshot(self, instrument: Instrument) -> Snapshot:
        ticker = self._get("/fapi/v1/ticker/24hr", symbol=instrument.instrument_id)
        oi = self._get("/fapi/v1/openInterest", symbol=instrument.instrument_id)
        funding = self._get("/fapi/v1/fundingRate", symbol=instrument.instrument_id, limit=1)
        source_ts = datetime.fromtimestamp(int(ticker["closeTime"]) / 1000, tz=timezone.utc)
        return Snapshot(
            instrument=instrument, source_ts=source_ts,
            last_price=float(ticker["lastPrice"]), price_change_24h=float(ticker["priceChangePercent"]),
            volume_24h=float(ticker["quoteVolume"]), oi_contracts=float(oi["openInterest"]),
            oi_usd=float(oi["openInterest"]) * float(ticker["lastPrice"]),
            funding_rate=float(funding[-1]["fundingRate"]) if funding else None,
        )
