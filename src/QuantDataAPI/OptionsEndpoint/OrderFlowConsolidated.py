"""Consolidated Order Flow one-page JSON request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Sequence, Unpack

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    OPTION_TRADE_FILTER_NAMES,
    OptionTradeFilters,
    add_filter,
    add_filter_expression,
    add_pagination,
    add_projection,
    add_session_or_time_range,
    option_trade_filters,
)
from QuantDataAPI.utility import JsonObject


def build_order_flow_consolidated_request(
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
    includeComprisingTrades: bool | None = None,
    includeStatistics: bool | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    **filters: Unpack[OptionTradeFilters],
) -> JsonObject:
    """Build one documented Consolidated Order Flow page request."""
    unexpected = set(filters).difference(OPTION_TRADE_FILTER_NAMES)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise TypeError(f"Unexpected order-flow filter(s): {names}.")

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
    if includeComprisingTrades is not None:
        body["includeComprisingTrades"] = includeComprisingTrades
    if includeStatistics is not None:
        body["includeStatistics"] = includeStatistics
    add_filter(body, **option_trade_filters(**filters))
    add_filter_expression(body, filterExpression)
    return body


def normalize_order_flow_consolidated(payload: JsonObject) -> JsonObject:
    """Validate and return one complete Consolidated Order Flow JSON page."""
    data = payload.get("data")
    cursor = payload.get("nextSearchAfter")
    statistics = payload.get("statistics")
    if (
        not isinstance(data, list)
        or (
            "nextSearchAfter" in payload
            and cursor is not None
            and not isinstance(cursor, list)
        )
        or (
            "statistics" in payload
            and statistics is not None
            and not isinstance(statistics, Mapping)
        )
    ):
        raise QuantDataClientError(
            "Unexpected order flow consolidated response page shape."
        )
    return payload
