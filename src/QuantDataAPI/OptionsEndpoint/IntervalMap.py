"""Interval Map request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_aggregation,
    add_filter,
    add_session_or_time_range,
)
from QuantDataAPI.utility import CONTRACT_TYPES, GREEK_MODES, _as_float, to_quantdata_date
from QuantDataAPI.validationChecks import (
    validate_enum,
    validate_non_empty_string,
    validate_positive,
)

INTERVAL_MAP_SCHEMA = {
    "timestamp": int,
    "expirationDate": str,
    "strikePrice": float,
    "contractType": str,
    "exposure": float,
}


def build_interval_map_request(
    *,
    ticker: str,
    greekMode: str,
    sessionDate: date | datetime | str | None = None,
    startTime: datetime | str | None = None,
    endTime: datetime | str | None = None,
    aggregationPeriod: str | None = None,
    expirationDate: date | datetime | str | None = None,
    minStrikePrice: int | float | None = None,
    maxStrikePrice: int | float | None = None,
) -> dict[str, Any]:
    """Build the documented Interval Map request body."""
    minimum = validate_positive("minStrikePrice", minStrikePrice)
    maximum = validate_positive("maxStrikePrice", maxStrikePrice)
    if minimum is not None and maximum is not None and maximum < minimum:
        raise ValueError("maxStrikePrice must be at least minStrikePrice.")
    body: dict[str, Any] = {
        "greekMode": validate_enum("greekMode", greekMode, GREEK_MODES)
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
        ticker=validate_non_empty_string("ticker", ticker),
        expirationDate=(
            to_quantdata_date(expirationDate)
            if expirationDate is not None
            else None
        ),
        minStrikePrice=minimum,
        maxStrikePrice=maximum,
    )
    return body


def normalize_interval_map(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Flatten timestamp/expiration/strike/contract exposure cells into rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for timestamp, expirations in data.items():
            if not isinstance(expirations, Mapping):
                raise TypeError("timestamp data must be an object")
            for expiration, strikes in expirations.items():
                if not isinstance(expiration, str) or not isinstance(strikes, Mapping):
                    raise TypeError("expiration data must be keyed objects")
                for strike, cell in strikes.items():
                    if not isinstance(cell, Mapping) or not cell:
                        raise TypeError("strike cells must be non-empty objects")
                    for contract_type, exposure in cell.items():
                        if contract_type not in CONTRACT_TYPES:
                            raise TypeError("contract type must be CALL or PUT")
                        rows.append(
                            {
                                "timestamp": int(timestamp),
                                "expirationDate": expiration,
                                "strikePrice": _as_float(strike),
                                "contractType": contract_type,
                                "exposure": _as_float(exposure),
                            }
                        )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(f"Unexpected interval map response: {exc}") from exc
    return sorted(
        rows,
        key=lambda row: (
            row["timestamp"],
            row["expirationDate"],
            row["strikePrice"],
            row["contractType"],
        ),
    )
