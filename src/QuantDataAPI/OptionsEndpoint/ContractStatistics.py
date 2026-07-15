"""Contract Statistics request and response helpers."""

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
from QuantDataAPI.utility import CONTRACT_TYPES, _as_float

CONTRACT_STATISTICS_SCHEMA = {
    "contractType": str,
    "premium": float,
    "tradeCount": int,
    "volume": int,
}


def build_contract_statistics_request(
    *,
    sessionDate: date | datetime | str | None = None,
    startTime: datetime | str | None = None,
    endTime: datetime | str | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    **filters: Unpack[OptionTradeFilters],
) -> dict[str, Any]:
    """Build the documented Contract Statistics request body."""
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


def normalize_contract_statistics(
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Normalize call/put aggregates into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")

        rows = []
        for contract_type, statistics in data.items():
            if contract_type not in CONTRACT_TYPES or not isinstance(statistics, Mapping):
                raise TypeError("contract statistics must be CALL/PUT objects")
            trade_count = statistics["tradeCount"]
            volume = statistics["volume"]
            if type(trade_count) is not int or type(volume) is not int:
                raise TypeError("tradeCount and volume must be integers")
            rows.append(
                {
                    "contractType": contract_type,
                    "premium": _as_float(statistics["premium"]),
                    "tradeCount": trade_count,
                    "volume": volume,
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected contract statistics response: {exc}"
        ) from exc

    return sorted(rows, key=lambda row: row["contractType"])
