"""Dark Flow request and response helpers."""

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

DARK_FLOW_SCHEMA = {
    "timestamp": int,
    "notionalValue": float,
    "size": int,
    "stockPrice": float,
    "tradeCount": int,
}


def build_dark_flow_request(
    *,
    ticker: str,
    sessionDate: date | datetime | str | None = None,
    startTime: datetime | str | None = None,
    endTime: datetime | str | None = None,
    aggregationPeriod: str | None = None,
) -> dict[str, Any]:
    """Build the documented Dark Flow request body."""
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


def normalize_dark_flow(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Normalize timestamp-keyed Dark Flow buckets into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")

        rows = []
        for timestamp, bucket in data.items():
            if not isinstance(bucket, Mapping):
                raise TypeError("bucket must be an object")
            size = bucket["size"]
            trade_count = bucket["tradeCount"]
            if type(size) is not int or type(trade_count) is not int:
                raise TypeError("size and tradeCount must be integers")
            rows.append(
                {
                    "timestamp": int(timestamp),
                    "notionalValue": _as_float(bucket["notionalValue"]),
                    "size": size,
                    "stockPrice": _as_float(bucket["stockPrice"]),
                    "tradeCount": trade_count,
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(f"Unexpected dark flow response: {exc}") from exc

    return sorted(rows, key=lambda row: row["timestamp"])
