"""Market Map request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Sequence

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_filter,
    add_filter_expression,
    add_session_or_snapshot,
)
from QuantDataAPI.utility import _as_float

MARKET_MAP_SCHEMA = {
    "ticker": str,
    "companyName": str,
    "currentValue": float,
    "industry": str,
    "previousValue": float,
    "sector": str,
    "size": float,
}


def build_market_map_request(
    *,
    sessionDate: date | datetime | str | None = None,
    snapshotTime: datetime | str | None = None,
    sectors: Sequence[str] | None = None,
    industries: Sequence[str] | None = None,
    filterExpression: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the documented Market Map request body."""
    body: dict[str, Any] = {}
    add_session_or_snapshot(
        body,
        sessionDate=sessionDate,
        snapshotTime=snapshotTime,
    )
    add_filter(body, sectors=sectors, industries=industries)
    add_filter_expression(body, filterExpression)
    return body


def normalize_market_map(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Normalize ticker-keyed company snapshots into DataFrame-ready rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")

        rows = []
        for ticker, snapshot in data.items():
            if not isinstance(ticker, str) or not isinstance(snapshot, Mapping):
                raise TypeError("ticker snapshots must be keyed objects")
            text_fields = {
                field: snapshot[field]
                for field in ("companyName", "industry", "sector")
            }
            if any(not isinstance(value, str) for value in text_fields.values()):
                raise TypeError("companyName, industry, and sector must be strings")
            rows.append(
                {
                    "ticker": ticker,
                    "companyName": text_fields["companyName"],
                    "currentValue": _as_float(snapshot["currentValue"]),
                    "industry": text_fields["industry"],
                    "previousValue": _as_float(snapshot["previousValue"]),
                    "sector": text_fields["sector"],
                    "size": _as_float(snapshot["size"]),
                }
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(f"Unexpected market map response: {exc}") from exc

    return sorted(rows, key=lambda row: row["ticker"])
