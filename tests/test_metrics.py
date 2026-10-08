from datetime import datetime, timedelta, timezone

from market_hotspot.metrics import oi_changes, select_baseline
from market_hotspot.sources.binance import BinanceFuturesSource


NOW = datetime(2026, 10, 8, 12, tzinfo=timezone.utc)


def test_select_baseline_requires_tolerance() -> None:
    assert select_baseline([(NOW - timedelta(hours=24, minutes=6), 100)], NOW, timedelta(hours=24)) is None


def test_oi_changes_does_not_fabricate_missing_24h_baseline() -> None:
    samples = [(NOW, 120), (NOW - timedelta(hours=1), 100)]
    result = oi_changes(samples, NOW)
    assert result["oi_change_1h"] == 20
    assert result["oi_change_24h"] is None


def test_stock_watch_symbols_are_not_misclassified_as_crypto_perps() -> None:
    source = BinanceFuturesSource()
    # This branch must not call the remote exchange-info endpoint.
    assert source.discover("TSLAUSDT") is None
