"""Stock Price Over Time request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_aggregation,
    add_filter,
    add_session_or_time_range,
)
from QuantDataAPI.utility import _as_float
from QuantDataAPI.validationChecks import validate_non_empty_string

STOCK_PRICE_OVER_TIME_SCHEMA = {
    "timestamp": int,
    "openPrice": float,
    "highPrice": float,
    "lowPrice": float,
    "closePrice": float,
}


def build_stock_price_over_time_request(
    *,
    ticker: str,
    sessionDate: date | datetime | str | None = None,
    startTime: datetime | str | None = None,
    endTime: datetime | str | None = None,
    aggregationPeriod: str | None = None,
) -> dict[str, Any]:
    """Build the documented Stock Price Over Time request body."""
    body: dict[str, Any] = {}
    add_session_or_time_range(
        body,
        sessionDate=sessionDate,
        startTime=startTime,
        endTime=endTime,
    )
    add_aggregation(body, aggregationPeriod)
    add_filter(body, ticker=validate_non_empty_string("ticker", ticker))
    return body


def normalize_stock_price_over_time(
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Normalize timestamp-keyed OHLC buckets into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")

        rows = []
        for timestamp, bucket in data.items():
            if not isinstance(bucket, Mapping):
                raise TypeError("bucket must be an object")
            rows.append(
                {
                    "timestamp": int(timestamp),
                    "openPrice": _as_float(bucket["openPrice"]),
                    "highPrice": _as_float(bucket["highPrice"]),
                    "lowPrice": _as_float(bucket["lowPrice"]),
                    "closePrice": _as_float(bucket["closePrice"]),
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected stock price over time response: {exc}"
        ) from exc

    return sorted(rows, key=lambda row: row["timestamp"])
