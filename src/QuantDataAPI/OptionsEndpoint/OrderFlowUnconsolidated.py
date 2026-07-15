"""Unconsolidated Order Flow one-page JSON request and response helpers."""

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

_UNSUPPORTED_FILTERS = frozenset({"tradeConsolidationTypes", "isGoldenSweep"})


def build_order_flow_unconsolidated_request(
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
    includeStatistics: bool | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    **filters: Unpack[OptionTradeFilters],
) -> JsonObject:
    """Build one documented Unconsolidated Order Flow page request."""
    unexpected = set(filters).difference(OPTION_TRADE_FILTER_NAMES)
    unsupported = set(filters).intersection(_UNSUPPORTED_FILTERS)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise TypeError(f"Unexpected order-flow filter(s): {names}.")
    if unsupported:
        names = ", ".join(sorted(unsupported))
        raise TypeError(
            f"Filter(s) not supported by unconsolidated order flow: {names}."
        )

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
        max_size=1_000,
    )
    add_projection(body, includes=includes, excludes=excludes)
    if includeStatistics is not None:
        body["includeStatistics"] = includeStatistics
    add_filter(body, **option_trade_filters(**filters))
    add_filter_expression(body, filterExpression)
    return body


def normalize_order_flow_unconsolidated(payload: JsonObject) -> JsonObject:
    """Validate and return one complete Unconsolidated Order Flow JSON page."""
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
            "Unexpected order flow unconsolidated response page shape."
        )
    return payload
