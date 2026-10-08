from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Optional, Sequence, Tuple


def percent_change(old: Optional[float], new: Optional[float]) -> Optional[float]:
    if old in (None, 0) or new is None:
        return None
    return (new - old) / old * 100


def select_baseline(samples: Iterable[Tuple[datetime, float]], as_of: datetime, interval: timedelta, tolerance: timedelta = timedelta(minutes=5)) -> Optional[float]:
    target = as_of - interval
    candidates = [(abs(ts - target), value) for ts, value in samples if abs(ts - target) <= tolerance]
    return min(candidates, key=lambda item: item[0])[1] if candidates else None


def oi_changes(samples: Sequence[Tuple[datetime, float]], as_of: datetime) -> dict[str, Optional[float]]:
    current = select_baseline(samples, as_of, timedelta(0), timedelta(minutes=5))
    return {
        "oi_change_1h": percent_change(select_baseline(samples, as_of, timedelta(hours=1)), current),
        "oi_change_4h": percent_change(select_baseline(samples, as_of, timedelta(hours=4)), current),
        "oi_change_24h": percent_change(select_baseline(samples, as_of, timedelta(hours=24)), current),
    }
