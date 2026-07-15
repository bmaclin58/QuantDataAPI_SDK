"""Contract Trade Side Statistics request and response helpers."""

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
from QuantDataAPI.utility import CONTRACT_TYPES, TRADE_SIDE_STAT_DATA_MODES, _as_float
from QuantDataAPI.validationChecks import validate_enum

TRADE_SIDE_NAMES = {"ABOVE_ASK", "ASK", "MID_MARKET", "BID", "BELOW_BID"}
MODE_FIELD = {
    "PREMIUM": "premium",
    "TRADE_COUNT": "tradeCount",
    "VOLUME": "volume",
}
CONTRACT_TRADE_SIDE_STATISTICS_SCHEMA = {
    "contractType": str,
    "tradeSide": str,
    "dataMode": str,
    "value": float,
}


def build_contract_trade_side_statistics_request(
    *,
    dataMode: str,
    sessionDate: date | datetime | str | None = None,
    startTime: datetime | str | None = None,
    endTime: datetime | str | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    **filters: Unpack[OptionTradeFilters],
) -> dict[str, Any]:
    """Build the documented Contract Trade Side Statistics request body."""
    body: dict[str, Any] = {
        "dataMode": validate_enum(
            "dataMode",
            dataMode,
            TRADE_SIDE_STAT_DATA_MODES,
        )
    }
    add_session_or_time_range(
        body,
        sessionDate=sessionDate,
        startTime=startTime,
        endTime=endTime,
    )
    add_filter(body, **option_trade_filters(**filters))
    add_filter_expression(body, filterExpression)
    return body


def normalize_contract_trade_side_statistics(
    payload: Mapping[str, Any],
    data_mode: str,
) -> list[dict[str, Any]]:
    """Normalize contract-type/trade-side cells into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        metric_field = MODE_FIELD[data_mode]

        rows = []
        for contract_type, sides in data.items():
            if contract_type not in CONTRACT_TYPES or not isinstance(sides, Mapping):
                raise TypeError("contract data must be CALL/PUT objects")
            for trade_side, cell in sides.items():
                if trade_side not in TRADE_SIDE_NAMES or not isinstance(cell, Mapping):
                    raise TypeError("trade-side cells use documented wire names")
                rows.append(
                    {
                        "contractType": contract_type,
                        "tradeSide": trade_side,
                        "dataMode": data_mode,
                        "value": _as_float(cell[metric_field]),
                    }
                )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected contract trade-side statistics response: {exc}"
        ) from exc

    return sorted(rows, key=lambda row: (row["contractType"], row["tradeSide"]))
