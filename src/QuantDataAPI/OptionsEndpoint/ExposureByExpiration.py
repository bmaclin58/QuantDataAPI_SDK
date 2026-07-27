"""Exposure By Expiration request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Sequence

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_filter,
    add_filter_expression,
    add_session_or_snapshot,
)
from QuantDataAPI.utility import GREEK_MODES, REPRESENTATION_MODES, _as_float
from QuantDataAPI.validationChecks import validate_enum, validate_non_empty_string

EXPOSURE_BY_EXPIRATION_SCHEMA = {
    "ticker": str,
    "expirationDate": date,
    "strikePrice": float,
    "callExposure": float,
    "putExposure": float,
    "stockPrice": float,
}


def build_exposure_by_expiration_request(
    *,
    ticker: str,
    greekMode: str,
    representationMode: str,
    sessionDate: date | datetime | str | None = None,
    snapshotTime: datetime | str | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    expirationDates: Sequence[str] | None = None,
    expirationDateRange: Mapping[str, Any] | None = None,
    strikePrices: Sequence[int | float] | None = None,
    strikePriceRange: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the documented Exposure By Expiration request body."""
    body: dict[str, Any] = {
        "greekMode": validate_enum("greekMode", greekMode, GREEK_MODES),
        "representationMode": validate_enum(
            "representationMode",
            representationMode,
            REPRESENTATION_MODES,
        ),
    }
    add_session_or_snapshot(
        body,
        sessionDate=sessionDate,
        snapshotTime=snapshotTime,
    )
    add_filter(
        body,
        ticker=validate_non_empty_string("ticker", ticker),
        expirationDates=expirationDates,
        expirationDateRange=expirationDateRange,
        strikePrices=strikePrices,
        strikePriceRange=strikePriceRange,
    )
    add_filter_expression(body, filterExpression)
    return body


def normalize_exposure_by_expiration(
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Flatten ticker/expiration/strike exposure cells into rows."""
    try:
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for ticker, ticker_data in data.items():
            if not isinstance(ticker, str) or not isinstance(ticker_data, Mapping):
                raise TypeError("ticker data must be keyed objects")
            exposure_map = ticker_data["exposureMap"]
            stock_price = _as_float(ticker_data["stockPrice"])
            if not isinstance(exposure_map, Mapping):
                raise TypeError("exposureMap must be an object")
            for expiration, strikes in exposure_map.items():
                if not isinstance(expiration, str) or not isinstance(strikes, Mapping):
                    raise TypeError("expiration data must be keyed objects")
                for strike, cell in strikes.items():
                    if not isinstance(cell, Mapping):
                        raise TypeError("strike cells must be objects")
                    call_exposure = cell.get("callExposure")
                    put_exposure = cell.get("putExposure")
                    rows.append(
                        {
                            "ticker": ticker,
                            "expirationDate": date.fromisoformat(expiration),
                            "strikePrice": _as_float(strike),
                            "callExposure": (
                                _as_float(call_exposure)
                                if call_exposure is not None
                                else None
                            ),
                            "putExposure": (
                                _as_float(put_exposure)
                                if put_exposure is not None
                                else None
                            ),
                            "stockPrice": stock_price,
                        }
                    )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected exposure by expiration response: {exc}"
        ) from exc
    return sorted(
        rows,
        key=lambda row: (row["ticker"], row["expirationDate"], row["strikePrice"]),
    )
