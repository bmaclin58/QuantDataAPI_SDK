"""Max Pain Over Time request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import add_filter, add_session
from QuantDataAPI.utility import _as_float
from QuantDataAPI.validationChecks import validate_non_empty_string

MAX_PAIN_OVER_TIME_SCHEMA = {
    "expirationDate": str,
    "maxPainStrikePrice": float,
}


def build_max_pain_over_time_request(
    *,
    ticker: str,
    sessionDate: date | datetime | str | None = None,
) -> dict[str, Any]:
    """Build the documented Max Pain Over Time request body."""
    body: dict[str, Any] = {}
    add_session(body, sessionDate)
    add_filter(body, ticker=validate_non_empty_string("ticker", ticker))
    return body


def normalize_max_pain_over_time(
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Normalize expiration-keyed max-pain strikes into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = [
            {
                "expirationDate": expiration,
                "maxPainStrikePrice": _as_float(strike),
            }
            for expiration, strike in data.items()
            if isinstance(expiration, str)
        ]
        if len(rows) != len(data):
            raise TypeError("expiration dates must be strings")
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected max pain over time response: {exc}"
        ) from exc
    return sorted(rows, key=lambda row: row["expirationDate"])
