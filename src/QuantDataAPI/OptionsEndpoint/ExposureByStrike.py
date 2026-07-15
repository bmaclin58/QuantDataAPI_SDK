"""Exposure By Strike request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Sequence

from QuantDataAPI.OptionsEndpoint.ExposureByExpiration import (
    EXPOSURE_BY_EXPIRATION_SCHEMA,
    normalize_exposure_by_expiration,
)
from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_filter,
    add_filter_expression,
    add_session_or_snapshot,
)
from QuantDataAPI.utility import (
    GREEK_MODES,
    REPRESENTATION_MODES,
    to_quantdata_date,
)
from QuantDataAPI.validationChecks import validate_enum, validate_non_empty_string

EXPOSURE_BY_STRIKE_SCHEMA = dict(EXPOSURE_BY_EXPIRATION_SCHEMA)


def build_exposure_by_strike_request(
    *,
    ticker: str,
    greekMode: str,
    representationMode: str,
    sessionDate: date | datetime | str | None = None,
    snapshotTime: datetime | str | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    expirationDate: date | datetime | str | None = None,
    expirationDates: Sequence[str] | None = None,
    expirationDateRange: Mapping[str, Any] | None = None,
    strikePrices: Sequence[int | float] | None = None,
    strikePriceRange: Mapping[str, Any] | None = None,
    moneyTypes: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Build the documented Exposure By Strike request body."""
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
        expirationDate=(
            to_quantdata_date(expirationDate)
            if expirationDate is not None
            else None
        ),
        expirationDates=expirationDates,
        expirationDateRange=expirationDateRange,
        strikePrices=strikePrices,
        strikePriceRange=strikePriceRange,
        moneyTypes=moneyTypes,
    )
    add_filter_expression(body, filterExpression)
    return body


def normalize_exposure_by_strike(
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Flatten the shared exposure wire contract into DataFrame-ready rows."""
    try:
        return normalize_exposure_by_expiration(payload)
    except QuantDataClientError as exc:
        detail = str(exc).replace("exposure by expiration", "exposure by strike")
        raise QuantDataClientError(detail) from exc
