from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional


CRYPTO_PERP_WEIGHTS = {
    "price": 0.25, "volume": 0.25, "oi": 0.20,
    "taker": 0.15, "long_short": 0.10, "funding": 0.05,
}
RTOKEN_WEIGHTS = {"price": 0.50, "volume": 0.50}


@dataclass(frozen=True)
class Score:
    quant_score: Optional[float]
    event_score: Optional[float]
    hotspot_score: Optional[float]
    priority: str
    ranking_mode: str
    score_quality: str


def profile_for(product_type: str) -> tuple[str, Mapping[str, float]]:
    if product_type == "CRYPTO_PERP":
        return "crypto_perp_v1", CRYPTO_PERP_WEIGHTS
    if product_type == "RTOKEN":
        return "rtoken_v1", RTOKEN_WEIGHTS
    return "price_volume_v1", RTOKEN_WEIGHTS


def weighted_score(metrics: Mapping[str, Optional[float]], weights: Mapping[str, float]) -> Optional[float]:
    # A predefined profile may score only the metrics native to that product type.
    values = [metrics.get(name) for name in weights]
    if any(value is None for value in values):
        return None
    return round(sum(float(metrics[name]) * weight for name, weight in weights.items()), 4)


def classify(quant: Optional[float], event: Optional[float], score_quality: str) -> Score:
    if quant is None or score_quality == "COLD_START":
        return Score(quant, event, None, "Monitor", "QUANT_ONLY", score_quality)
    if event is None:
        return Score(quant, None, None, "P1" if quant >= 60 else "P2", "QUANT_ONLY", score_quality)
    hotspot = round(quant * 0.65 + event * 0.35, 4)
    if quant >= 80 and event < 60:
        priority = "P1"
    elif event >= 85 and quant < 70:
        priority = "P1"
    elif hotspot >= 80 and quant >= 70 and event >= 60:
        priority = "P0"
    elif hotspot >= 60:
        priority = "P1"
    elif hotspot >= 40:
        priority = "P2"
    else:
        priority = "Monitor"
    return Score(quant, event, hotspot, priority, "FULL", score_quality)


def delivery_status(risk_status: str) -> str:
    return {"PASS": "READY_FOR_REVIEW", "REVIEW": "REVIEW_REQUIRED", "BLOCK": "PROHIBITED"}[risk_status]
