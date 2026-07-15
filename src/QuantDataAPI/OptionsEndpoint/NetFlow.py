"""Net Flow request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Sequence

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_aggregation,
    add_filter,
    add_filter_expression,
    add_session_or_time_range,
)
from QuantDataAPI.utility import NET_FLOW_DATA_MODES, _as_float
from QuantDataAPI.validationChecks import validate_enum

NET_FLOW_SCHEMA = {
    "timestamp": int,
    "callSum": float,
    "putSum": float,
    "stockPrice": float,
}


def build_net_flow_request(
    *,
    dataMode: str,
    sessionDate: date | datetime | str | None = None,
    startTime: datetime | str | None = None,
    endTime: datetime | str | None = None,
    aggregationPeriod: str | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    ticker: str | None = None,
    tickers: Sequence[str] | None = None,
    expirationDates: Sequence[str] | None = None,
    expirationDateRange: Mapping[str, Any] | None = None,
    strikePrices: Sequence[int | float] | None = None,
    strikePriceRange: Mapping[str, Any] | None = None,
    moneyTypes: Sequence[str] | None = None,
    tradeSideCodes: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Build the documented Net Flow request body."""
    body: dict[str, Any] = {
        "dataMode": validate_enum("dataMode", dataMode, NET_FLOW_DATA_MODES)
    }
    add_session_or_time_range(
        body,
        sessionDate=sessionDate,
        startTime=startTime,
        endTime=endTime,
    )
    add_aggregation(body, aggregationPeriod)
    add_filter(
        body,
        ticker=ticker,
        tickers=tickers,
        expirationDates=expirationDates,
        expirationDateRange=expirationDateRange,
        strikePrices=strikePrices,
        strikePriceRange=strikePriceRange,
        moneyTypes=moneyTypes,
        tradeSideCodes=tradeSideCodes,
    )
    add_filter_expression(body, filterExpression)
    return body


def normalize_net_flow(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Normalize timestamp-keyed net-flow buckets into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for timestamp, bucket in data.items():
            if not isinstance(bucket, Mapping):
                raise TypeError("bucket must be an object")
            stock_price = bucket.get("stockPrice")
            rows.append(
                {
                    "timestamp": int(timestamp),
                    "callSum": _as_float(bucket["callSum"]),
                    "putSum": _as_float(bucket["putSum"]),
                    "stockPrice": (
                        _as_float(stock_price) if stock_price is not None else None
                    ),
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(f"Unexpected net flow response: {exc}") from exc
    return sorted(rows, key=lambda row: row["timestamp"])
