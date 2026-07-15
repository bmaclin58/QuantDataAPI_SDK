"""Open Interest Over Time request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import add_filter
from QuantDataAPI.utility import to_quantdata_date
from QuantDataAPI.validationChecks import validate_non_empty_string, validate_positive

OPEN_INTEREST_OVER_TIME_SCHEMA = {
    "sessionDate": str,
    "callOpenInterest": int,
    "putOpenInterest": int,
}


def build_open_interest_over_time_request(
    *,
    ticker: str,
    expirationDate: date | datetime | str | None = None,
    strikePrice: int | float | None = None,
) -> dict[str, Any]:
    """Build the documented Open Interest Over Time request body."""
    body: dict[str, Any] = {}
    add_filter(
        body,
        ticker=validate_non_empty_string("ticker", ticker),
        expirationDate=(
            to_quantdata_date(expirationDate)
            if expirationDate is not None
            else None
        ),
        strikePrice=validate_positive("strikePrice", strikePrice),
    )
    return body


def normalize_open_interest_over_time(
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Normalize session-keyed open interest into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for session, cell in data.items():
            if not isinstance(session, str) or not isinstance(cell, Mapping):
                raise TypeError("session cells must be keyed objects")
            call_oi = cell["callOpenInterest"]
            put_oi = cell["putOpenInterest"]
            if type(call_oi) is not int or type(put_oi) is not int:
                raise TypeError("open-interest values must be integers")
            rows.append(
                {
                    "sessionDate": session,
                    "callOpenInterest": call_oi,
                    "putOpenInterest": put_oi,
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected open interest over time response: {exc}"
        ) from exc
    return sorted(rows, key=lambda row: row["sessionDate"])
