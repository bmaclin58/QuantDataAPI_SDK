"""Net Drift request and response helpers."""

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
from QuantDataAPI.utility import _as_float

NET_DRIFT_SCHEMA = {
    "timestamp": int,
    "midMarketCallPremium": float,
    "midMarketPutPremium": float,
    "netCallPremium": float,
    "netCallVolume": int,
    "netPutPremium": float,
    "netPutVolume": int,
    "stockPrice": float,
}


def build_net_drift_request(
    *,
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
) -> dict[str, Any]:
    """Build the documented Net Drift request body."""
    body: dict[str, Any] = {}
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
    )
    add_filter_expression(body, filterExpression)
    return body


def normalize_net_drift(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Normalize timestamp-keyed net-drift buckets into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for timestamp, bucket in data.items():
            if not isinstance(bucket, Mapping):
                raise TypeError("bucket must be an object")
            call_volume = bucket["netCallVolume"]
            put_volume = bucket["netPutVolume"]
            if type(call_volume) is not int or type(put_volume) is not int:
                raise TypeError("net volume fields must be integers")
            stock_price = bucket.get("stockPrice")
            rows.append(
                {
                    "timestamp": int(timestamp),
                    "midMarketCallPremium": _as_float(bucket["midMarketCallPremium"]),
                    "midMarketPutPremium": _as_float(bucket["midMarketPutPremium"]),
                    "netCallPremium": _as_float(bucket["netCallPremium"]),
                    "netCallVolume": call_volume,
                    "netPutPremium": _as_float(bucket["netPutPremium"]),
                    "netPutVolume": put_volume,
                    "stockPrice": (
                        _as_float(stock_price) if stock_price is not None else None
                    ),
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(f"Unexpected net drift response: {exc}") from exc
    return sorted(rows, key=lambda row: row["timestamp"])
