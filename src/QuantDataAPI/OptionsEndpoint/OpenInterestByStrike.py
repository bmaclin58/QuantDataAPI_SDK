"""Open Interest By Strike request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import add_filter, add_session
from QuantDataAPI.utility import _as_float, to_quantdata_date
from QuantDataAPI.validationChecks import validate_non_empty_string

OPEN_INTEREST_BY_STRIKE_SCHEMA = {
    "strikePrice": float,
    "callOpenInterest": int,
    "putOpenInterest": int,
}


def build_open_interest_by_strike_request(
    *,
    ticker: str,
    sessionDate: date | datetime | str | None = None,
    expirationDate: date | datetime | str | None = None,
) -> dict[str, Any]:
    """Build the documented Open Interest By Strike request body."""
    body: dict[str, Any] = {}
    add_session(body, sessionDate)
    add_filter(
        body,
        ticker=validate_non_empty_string("ticker", ticker),
        expirationDate=(
            to_quantdata_date(expirationDate)
            if expirationDate is not None
            else None
        ),
    )
    return body


def normalize_open_interest_by_strike(
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Normalize strike-keyed open interest into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for strike, cell in data.items():
            if not isinstance(cell, Mapping):
                raise TypeError("strike cells must be objects")
            call_oi = cell["callOpenInterest"]
            put_oi = cell["putOpenInterest"]
            if type(call_oi) is not int or type(put_oi) is not int:
                raise TypeError("open-interest values must be integers")
            rows.append(
                {
                    "strikePrice": _as_float(strike),
                    "callOpenInterest": call_oi,
                    "putOpenInterest": put_oi,
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected open interest by strike response: {exc}"
        ) from exc
    return sorted(rows, key=lambda row: row["strikePrice"])
