"""Option Price Over Time request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_aggregation,
    add_filter,
    add_session_or_time_range,
)
from QuantDataAPI.utility import CONTRACT_TYPES, _as_float, to_quantdata_date
from QuantDataAPI.validationChecks import (
    validate_enum,
    validate_non_empty_string,
    validate_positive,
)

OPTION_PRICE_OVER_TIME_SCHEMA = {
    "timestamp": int,
    "openPrice": float,
    "highPrice": float,
    "lowPrice": float,
    "closePrice": float,
    "volume": int,
}


def build_option_price_over_time_request(
    *,
    sessionDate: date | datetime | str | None = None,
    startTime: datetime | str | None = None,
    endTime: datetime | str | None = None,
    aggregationPeriod: str | None = None,
    osi: str | None = None,
    ticker: str | None = None,
    expirationDate: date | datetime | str | None = None,
    strikePrice: int | float | None = None,
    contractType: str | None = None,
) -> dict[str, Any]:
    """Build the documented Option Price Over Time request body."""
    contract_fields = (ticker, expirationDate, strikePrice, contractType)
    has_contract_fields = any(value is not None for value in contract_fields)
    has_all_contract_fields = all(value is not None for value in contract_fields)
    if osi is not None and has_contract_fields:
        raise ValueError("osi cannot be combined with ticker/expiration/strike/type.")
    if osi is None and not has_all_contract_fields:
        raise ValueError(
            "Provide osi or all of ticker, expirationDate, strikePrice, contractType."
        )

    body: dict[str, Any] = {}
    add_session_or_time_range(
        body,
        sessionDate=sessionDate,
        startTime=startTime,
        endTime=endTime,
    )
    add_aggregation(body, aggregationPeriod)
    if osi is not None:
        normalized_osi = validate_non_empty_string("osi", osi)
        add_filter(body, osi=normalized_osi)
    else:
        add_filter(
            body,
            ticker=validate_non_empty_string("ticker", ticker),
            expirationDate=to_quantdata_date(expirationDate),
            strikePrice=validate_positive("strikePrice", strikePrice),
            contractType=validate_enum("contractType", contractType, CONTRACT_TYPES),
        )
    return body


def normalize_option_price_over_time(
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Normalize timestamp-keyed option OHLCV bars into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for timestamp, bar in data.items():
            if not isinstance(bar, Mapping):
                raise TypeError("bars must be objects")
            volume = bar["volume"]
            if type(volume) is not int:
                raise TypeError("volume must be an integer")
            rows.append(
                {
                    "timestamp": int(timestamp),
                    "openPrice": _as_float(bar["openPrice"]),
                    "highPrice": _as_float(bar["highPrice"]),
                    "lowPrice": _as_float(bar["lowPrice"]),
                    "closePrice": _as_float(bar["closePrice"]),
                    "volume": volume,
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected option price over time response: {exc}"
        ) from exc
    return sorted(rows, key=lambda row: row["timestamp"])
