"""Heat Map request and polymorphic response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Sequence

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_filter,
    add_filter_expression,
    add_session_or_snapshot,
)
from QuantDataAPI.utility import HEAT_MAP_DATA_MODES, _as_float, to_quantdata_date
from QuantDataAPI.validationChecks import validate_enum, validate_non_empty_string

HEAT_MAP_CONTRACT_SCHEMA = {
    "type": str,
    "expirationDate": str,
    "strikePrice": float,
    "callValue": float,
    "putValue": float,
}
HEAT_MAP_SINGLE_SCHEMA = {
    "type": str,
    "expirationDate": str,
    "strikePrice": float,
    "value": float,
}


def build_heat_map_request(
    *,
    ticker: str,
    dataMode: str,
    sessionDate: date | datetime | str | None = None,
    snapshotTime: datetime | str | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    expirationDate: date | datetime | str | None = None,
    expirationDates: Sequence[str] | None = None,
    expirationDateRange: Mapping[str, Any] | None = None,
    strikePrices: Sequence[int | float] | None = None,
    strikePriceRange: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the documented Heat Map request body."""
    body: dict[str, Any] = {
        "dataMode": validate_enum("dataMode", dataMode, HEAT_MAP_DATA_MODES)
    }
    add_session_or_snapshot(
        body,
        sessionDate=sessionDate,
        snapshotTime=snapshotTime,
    )
    add_filter(
        body,
        ticker=validate_non_empty_string("ticker", ticker),
        expirationDate=(
            to_quantdata_date(expirationDate)
            if expirationDate is not None
            else None
        ),
        expirationDates=expirationDates,
        expirationDateRange=expirationDateRange,
        strikePrices=strikePrices,
        strikePriceRange=strikePriceRange,
    )
    add_filter_expression(body, filterExpression)
    return body


def normalize_heat_map(
    payload: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], Mapping[str, type]]:
    """Normalize the advertised contract or single Heat Map response shape."""
    try:
        response_type = payload["type"]
        data = payload["data"]
        if response_type not in {"contract", "single"}:
            raise TypeError("type must be contract or single")
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        schema = (
            HEAT_MAP_CONTRACT_SCHEMA
            if response_type == "contract"
            else HEAT_MAP_SINGLE_SCHEMA
        )
        rows = []
        for expiration, strikes in data.items():
            if not isinstance(expiration, str) or not isinstance(strikes, Mapping):
                raise TypeError("expiration data must be keyed objects")
            for strike, cell in strikes.items():
                if not isinstance(cell, Mapping):
                    raise TypeError("strike cells must be objects")
                row = {
                    "type": response_type,
                    "expirationDate": expiration,
                    "strikePrice": _as_float(strike),
                }
                if response_type == "contract":
                    row["callValue"] = _as_float(cell["callValue"])
                    row["putValue"] = _as_float(cell["putValue"])
                else:
                    row["value"] = _as_float(cell["value"])
                rows.append(row)
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(f"Unexpected heat map response: {exc}") from exc
    rows.sort(key=lambda row: (row["expirationDate"], row["strikePrice"]))
    return rows, schema
