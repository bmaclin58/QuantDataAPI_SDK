"""Max Pain request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import add_filter, add_session
from QuantDataAPI.utility import _as_float, to_quantdata_date
from QuantDataAPI.validationChecks import validate_non_empty_string, validate_required

MAX_PAIN_SCHEMA = {
    "strikePrice": float,
    "callIntrinsicValue": float,
    "putIntrinsicValue": float,
    "maxPainStrikePrice": float,
    "stockPrice": float,
}


def build_max_pain_request(
    *,
    ticker: str,
    expirationDate: date | datetime | str,
    sessionDate: date | datetime | str | None = None,
) -> dict[str, Any]:
    """Build the documented Max Pain request body."""
    body: dict[str, Any] = {}
    add_session(body, sessionDate)
    expiration = to_quantdata_date(validate_required("expirationDate", expirationDate))
    add_filter(
        body,
        ticker=validate_non_empty_string("ticker", ticker),
        expirationDate=expiration,
    )
    return body


def normalize_max_pain(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Normalize strike-keyed intrinsic values into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        max_pain_strike = _as_float(payload["maxPainStrikePrice"])
        stock_price = _as_float(payload["stockPrice"])
        rows = []
        for strike, cell in data.items():
            if not isinstance(cell, Mapping):
                raise TypeError("strike cells must be objects")
            rows.append(
                {
                    "strikePrice": _as_float(strike),
                    "callIntrinsicValue": _as_float(cell["callIntrinsicValue"]),
                    "putIntrinsicValue": _as_float(cell["putIntrinsicValue"]),
                    "maxPainStrikePrice": max_pain_strike,
                    "stockPrice": stock_price,
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(f"Unexpected max pain response: {exc}") from exc
    return sorted(rows, key=lambda row: row["strikePrice"])
