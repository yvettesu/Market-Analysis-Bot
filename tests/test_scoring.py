from market_hotspot.risk import assess_tradeability
from market_hotspot.scoring import classify, weighted_score


def test_quant_only_never_promotes_to_p0() -> None:
    result = classify(95, None, "READY")
    assert result.priority == "P1"
    assert result.hotspot_score is None


def test_missing_native_metric_does_not_redistribute_weight() -> None:
    assert weighted_score({"price": 90, "volume": None}, {"price": .5, "volume": .5}) is None


def test_block_does_not_change_hotspot_priority() -> None:
    status, reasons = assess_tradeability(tradable=True, book_complete=True, fresh=True, bid_depth_usd=1, ask_depth_usd=60_000, spread=10, buy_slippage_bps=2, sell_slippage_bps=2)
    assert (status, reasons) == ("BLOCK", ["INSUFFICIENT_1PCT_DEPTH"])
