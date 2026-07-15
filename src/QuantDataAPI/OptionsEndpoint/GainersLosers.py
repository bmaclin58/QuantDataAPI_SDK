"""Gainers / Losers request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Sequence

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_filter,
    add_filter_expression,
    add_session_or_time_range,
)
from QuantDataAPI.utility import _as_float

GAINERS_LOSERS_SCHEMA = {
    "ticker": str,
    "bearishPremium": float,
    "bullishPremium": float,
    "premium": float,
    "premiumRatio": float,
    "tradeCount": int,
    "volume": int,
}


def build_gainers_losers_request(
    *,
    sessionDate: date | datetime | str | None = None,
    startTime: datetime | str | None = None,
    endTime: datetime | str | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    tickers: Sequence[str] | None = None,
    sectors: Sequence[str] | None = None,
    industries: Sequence[str] | None = None,
    expirationDates: Sequence[str] | None = None,
    expirationDateRange: Mapping[str, Any] | None = None,
    dteRange: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the documented Gainers / Losers request body."""
    body: dict[str, Any] = {}
    add_session_or_time_range(
        body,
        sessionDate=sessionDate,
        startTime=startTime,
        endTime=endTime,
    )
    add_filter(
        body,
        tickers=tickers,
        sectors=sectors,
        industries=industries,
        expirationDates=expirationDates,
        expirationDateRange=expirationDateRange,
        dteRange=dteRange,
    )
    add_filter_expression(body, filterExpression)
    return body


def normalize_gainers_losers(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Normalize ticker-keyed option-flow summaries into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for ticker, statistics in data.items():
            if not isinstance(ticker, str) or not isinstance(statistics, Mapping):
                raise TypeError("ticker statistics must be keyed objects")
            trade_count = statistics["tradeCount"]
            volume = statistics["volume"]
            if type(trade_count) is not int or type(volume) is not int:
                raise TypeError("tradeCount and volume must be integers")
            rows.append(
                {
                    "ticker": ticker,
                    "bearishPremium": _as_float(statistics["bearishPremium"]),
                    "bullishPremium": _as_float(statistics["bullishPremium"]),
                    "premium": _as_float(statistics["premium"]),
                    "premiumRatio": _as_float(statistics["premiumRatio"]),
                    "tradeCount": trade_count,
                    "volume": volume,
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(f"Unexpected gainers/losers response: {exc}") from exc
    return sorted(rows, key=lambda row: row["ticker"])
