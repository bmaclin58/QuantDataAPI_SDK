"""Market Share request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Unpack

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_filter,
    add_filter_expression,
    add_session_or_time_range,
    OptionTradeFilters,
    option_trade_filters,
)
from QuantDataAPI.utility import _as_float

PREMIUM_FIELDS = ("equityCallPremium", "equityPutPremium", "indexPremium")
INTEGER_FIELDS = (
    "equityCallTradeCount",
    "equityCallVolume",
    "equityPutTradeCount",
    "equityPutVolume",
    "indexTradeCount",
    "indexVolume",
)
MARKET_SHARE_SCHEMA = {
    "exchange": str,
    "equityCallPremium": float,
    "equityCallTradeCount": int,
    "equityCallVolume": int,
    "equityPutPremium": float,
    "equityPutTradeCount": int,
    "equityPutVolume": int,
    "indexPremium": float,
    "indexTradeCount": int,
    "indexVolume": int,
}


def build_market_share_request(
    *,
    sessionDate: date | datetime | str | None = None,
    startTime: datetime | str | None = None,
    endTime: datetime | str | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    **filters: Unpack[OptionTradeFilters],
) -> dict[str, Any]:
    """Build the documented Market Share request body."""
    body: dict[str, Any] = {}
    add_session_or_time_range(
        body,
        sessionDate=sessionDate,
        startTime=startTime,
        endTime=endTime,
    )
    add_filter(body, **option_trade_filters(**filters))
    add_filter_expression(body, filterExpression)
    return body


def normalize_market_share(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Normalize exchange-keyed market-share cells into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for exchange, statistics in data.items():
            if not isinstance(exchange, str) or not isinstance(statistics, Mapping):
                raise TypeError("exchange statistics must be keyed objects")
            integers = {field: statistics[field] for field in INTEGER_FIELDS}
            if any(type(value) is not int for value in integers.values()):
                raise TypeError("trade counts and volumes must be integers")
            row = {"exchange": exchange}
            for field in MARKET_SHARE_SCHEMA:
                if field in PREMIUM_FIELDS:
                    row[field] = _as_float(statistics[field])
                elif field in integers:
                    row[field] = integers[field]
            rows.append(row)
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(f"Unexpected market share response: {exc}") from exc
    return sorted(rows, key=lambda row: row["exchange"])
