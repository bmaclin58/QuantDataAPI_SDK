"""Equity Prints one-page JSON request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Sequence

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_filter,
    add_filter_expression,
    add_pagination,
    add_projection,
    add_session_or_time_range,
)
from QuantDataAPI.utility import JsonObject


def build_equity_prints_request(
    *,
    sessionDate: date | datetime | str | None = None,
    startTime: datetime | str | None = None,
    endTime: datetime | str | None = None,
    size: int | None = None,
    searchAfter: Sequence[Any] | None = None,
    sortField: str | None = None,
    sortDirection: str | None = None,
    includes: Sequence[str] | None = None,
    excludes: Sequence[str] | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    tickers: Sequence[str] | None = None,
    equityPrintTypes: Sequence[str] | None = None,
    tradeSideCodes: Sequence[str] | None = None,
    priceRange: Mapping[str, Any] | None = None,
    sizeRange: Mapping[str, Any] | None = None,
    askPriceRange: Mapping[str, Any] | None = None,
    askSizeRange: Mapping[str, Any] | None = None,
    bidPriceRange: Mapping[str, Any] | None = None,
    bidSizeRange: Mapping[str, Any] | None = None,
    notionalValueRange: Mapping[str, Any] | None = None,
    isDelayedPrint: bool | None = None,
) -> JsonObject:
    """Build one documented Equity Prints page request."""
    body: JsonObject = {}
    add_session_or_time_range(
        body,
        sessionDate=sessionDate,
        startTime=startTime,
        endTime=endTime,
    )
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
        equityPrintTypes=equityPrintTypes,
        tradeSideCodes=tradeSideCodes,
        priceRange=priceRange,
        sizeRange=sizeRange,
        askPriceRange=askPriceRange,
        askSizeRange=askSizeRange,
        bidPriceRange=bidPriceRange,
        bidSizeRange=bidSizeRange,
        notionalValueRange=notionalValueRange,
        isDelayedPrint=isDelayedPrint,
    )
    add_filter_expression(body, filterExpression)
    return body


def normalize_equity_prints(payload: JsonObject) -> JsonObject:
    """Validate and return one complete Equity Prints JSON page."""
    data = payload.get("data")
    cursor = payload.get("nextSearchAfter")
    if not isinstance(data, list) or (
        "nextSearchAfter" in payload
        and cursor is not None
        and not isinstance(cursor, list)
    ):
        raise QuantDataClientError("Unexpected equity prints response page shape.")
    return payload
