"""Volatility Drift request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import add_filter, add_session
from QuantDataAPI.utility import _as_float, to_quantdata_date
from QuantDataAPI.validationChecks import validate_non_empty_string

VOLATILITY_DRIFT_SCHEMA = {
    "timestamp": int,
    "arv": float,
    "iv": float,
    "stockPrice": float,
}


def build_volatility_drift_request(
    *,
    ticker: str,
    sessionDate: date | datetime | str | None = None,
    expirationDate: date | datetime | str | None = None,
) -> dict[str, Any]:
    """Build the documented Volatility Drift request body."""
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


def normalize_volatility_drift(
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Normalize fixed one-minute volatility buckets into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for timestamp, bucket in data.items():
            if not isinstance(bucket, Mapping):
                raise TypeError("bucket must be an object")
            arv = bucket.get("arv")
            iv = bucket.get("iv")
            rows.append(
                {
                    "timestamp": int(timestamp),
                    "arv": _as_float(arv) if arv is not None else None,
                    "iv": _as_float(iv) if iv is not None else None,
                    "stockPrice": _as_float(bucket["stockPrice"]),
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected volatility drift response: {exc}"
        ) from exc
    return sorted(rows, key=lambda row: row["timestamp"])
