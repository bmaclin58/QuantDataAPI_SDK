"""Open Interest By Expiration request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import add_filter, add_session
from QuantDataAPI.validationChecks import validate_non_empty_string, validate_positive

OPEN_INTEREST_BY_EXPIRATION_SCHEMA = {
    "expirationDate": date,
    "callOpenInterest": int,
    "putOpenInterest": int,
}


def build_open_interest_by_expiration_request(
    *,
    ticker: str,
    sessionDate: date | datetime | str | None = None,
    strikePrice: int | float | None = None,
) -> dict[str, Any]:
    """Build the documented Open Interest By Expiration request body."""
    body: dict[str, Any] = {}
    add_session(body, sessionDate)
    add_filter(
        body,
        ticker=validate_non_empty_string("ticker", ticker),
        strikePrice=validate_positive("strikePrice", strikePrice),
    )
    return body


def normalize_open_interest_by_expiration(
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Normalize expiration-keyed open interest into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for expiration, cell in data.items():
            if not isinstance(expiration, str) or not isinstance(cell, Mapping):
                raise TypeError("expiration cells must be keyed objects")
            call_oi = cell["callOpenInterest"]
            put_oi = cell["putOpenInterest"]
            if type(call_oi) is not int or type(put_oi) is not int:
                raise TypeError("open-interest values must be integers")
            rows.append(
                {
                    "expirationDate": date.fromisoformat(expiration),
                    "callOpenInterest": call_oi,
                    "putOpenInterest": put_oi,
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected open interest by expiration response: {exc}"
        ) from exc
    return sorted(rows, key=lambda row: row["expirationDate"])
