"""Dark Pool Levels request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import add_filter, add_session_date_range
from QuantDataAPI.utility import _as_float

DARK_POOL_LEVELS_SCHEMA = {
    "priceLevel": float,
    "notionalValue": float,
    "size": int,
    "tradeCount": int,
    "latestStockPrice": float,
}


def build_dark_pool_levels_request(
    *,
    ticker: str,
    startDate: date | datetime | str,
    endDate: date | datetime | str | None = None,
) -> dict[str, Any]:
    """Build the documented Dark Pool Levels request body."""
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("ticker must be a non-empty string.")

    body: dict[str, Any] = {}
    add_session_date_range(body, startDate=startDate, endDate=endDate)
    add_filter(body, ticker=ticker.strip())
    return body


def normalize_dark_pool_levels(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Normalize the price-keyed response into DataFrame-ready rows."""
    try:
        latest_stock_price = _as_float(payload["latestStockPrice"])
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")

        rows = []
        for price_level, statistics in data.items():
            if not isinstance(statistics, Mapping):
                raise TypeError("price-level statistics must be an object")
            size = statistics["size"]
            trade_count = statistics["tradeCount"]
            if type(size) is not int or type(trade_count) is not int:
                raise TypeError("size and tradeCount must be integers")
            rows.append(
                {
                    "priceLevel": _as_float(price_level),
                    "notionalValue": _as_float(statistics["notionalValue"]),
                    "size": size,
                    "tradeCount": trade_count,
                    "latestStockPrice": latest_stock_price,
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected dark-pool levels response: {exc}"
        ) from exc

    return sorted(rows, key=lambda row: row["priceLevel"])
