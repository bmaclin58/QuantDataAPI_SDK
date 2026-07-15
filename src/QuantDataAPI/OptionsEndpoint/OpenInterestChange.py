"""Open Interest Change one-page JSON request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Sequence

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_filter,
    add_filter_expression,
    add_pagination,
    add_projection,
    add_session,
)
from QuantDataAPI.utility import CONTRACT_TYPES, JsonObject
from QuantDataAPI.validationChecks import validate_enum_sequence


def build_open_interest_change_request(
    *,
    sessionDate: date | datetime | str | None = None,
    size: int | None = None,
    searchAfter: Sequence[Any] | None = None,
    sortField: str | None = None,
    sortDirection: str | None = None,
    includes: Sequence[str] | None = None,
    excludes: Sequence[str] | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    tickers: Sequence[str] | None = None,
    contractTypes: Sequence[str] | None = None,
    strikePrices: Sequence[int | float] | None = None,
    strikePriceRange: Mapping[str, Any] | None = None,
    expirationDates: Sequence[date | datetime | str] | None = None,
    expirationDateRange: Mapping[str, Any] | None = None,
    previousOpenInterestRange: Mapping[str, Any] | None = None,
    currentOpenInterestRange: Mapping[str, Any] | None = None,
    changeInOpenInterestRange: Mapping[str, Any] | None = None,
    percentChangeInOpenInterestRange: Mapping[str, Any] | None = None,
) -> JsonObject:
    """Build one documented Open Interest Change page request."""
    if strikePrices is not None and strikePriceRange is not None:
        raise ValueError("strikePrices and strikePriceRange are mutually exclusive.")
    if expirationDates is not None and expirationDateRange is not None:
        raise ValueError(
            "expirationDates and expirationDateRange are mutually exclusive."
        )

    body: JsonObject = {}
    add_session(body, sessionDate)
    add_pagination(
        body,
        size=size,
        searchAfter=searchAfter,
        sortField=sortField,
        sortDirection=sortDirection,
    )
    add_projection(body, includes=includes, excludes=excludes)
    add_filter(
        body,
        tickers=tickers,
        contractTypes=validate_enum_sequence(
            "contractTypes",
            contractTypes,
            CONTRACT_TYPES,
        ),
        strikePrices=strikePrices,
        strikePriceRange=strikePriceRange,
        expirationDates=expirationDates,
        expirationDateRange=expirationDateRange,
        previousOpenInterestRange=previousOpenInterestRange,
        currentOpenInterestRange=currentOpenInterestRange,
        changeInOpenInterestRange=changeInOpenInterestRange,
        percentChangeInOpenInterestRange=percentChangeInOpenInterestRange,
    )
    add_filter_expression(body, filterExpression)
    return body


def normalize_open_interest_change(payload: JsonObject) -> JsonObject:
    """Validate and return one complete Open Interest Change JSON page."""
    data = payload.get("data")
    cursor = payload.get("nextSearchAfter")
    if not isinstance(data, list) or (
        "nextSearchAfter" in payload
        and cursor is not None
        and not isinstance(cursor, list)
    ):
        raise QuantDataClientError(
            "Unexpected open interest change response page shape."
        )
    return payload
