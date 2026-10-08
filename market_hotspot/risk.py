from __future__ import annotations

from typing import Iterable, Optional, Sequence, Tuple


def spread_bps(best_bid: Optional[float], best_ask: Optional[float]) -> Optional[float]:
    if best_bid is None or best_ask is None or best_bid <= 0 or best_ask <= 0:
        return None
    return (best_ask - best_bid) / ((best_ask + best_bid) / 2) * 10_000


def book_notional(levels: Iterable[Tuple[float, float]], lower: float, upper: float) -> float:
    return sum(price * size for price, size in levels if lower <= price <= upper)


def assess_tradeability(*, tradable: bool, book_complete: bool, fresh: bool, bid_depth_usd: Optional[float], ask_depth_usd: Optional[float], spread: Optional[float], buy_slippage_bps: Optional[float], sell_slippage_bps: Optional[float]) -> tuple[str, list[str]]:
    if not tradable:
        return "BLOCK", ["NOT_TRADABLE"]
    if not fresh:
        return "BLOCK", ["STALE_MARKET_DATA"]
    if not book_complete or None in (bid_depth_usd, ask_depth_usd, spread, buy_slippage_bps, sell_slippage_bps):
        return "REVIEW", ["INSUFFICIENT_ORDERBOOK_EVIDENCE"]
    if bid_depth_usd < 50_000 or ask_depth_usd < 50_000:
        return "BLOCK", ["INSUFFICIENT_1PCT_DEPTH"]
    if spread > 50 or buy_slippage_bps > 100 or sell_slippage_bps > 100:
        return "BLOCK", ["EXECUTION_COST_EXCEEDED"]
    return "PASS", []
