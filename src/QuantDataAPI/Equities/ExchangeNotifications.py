"""Exchange Notifications one-page JSON request and response helpers."""

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


def build_exchange_notifications_request(
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
    types: Sequence[str] | None = None,
) -> JsonObject:
    """Build one documented Exchange Notifications page request."""
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
    add_filter(body, tickers=tickers, types=types)
    add_filter_expression(body, filterExpression)
    return body


def normalize_exchange_notifications(payload: JsonObject) -> JsonObject:
    """Validate and return one complete Exchange Notifications JSON page."""
    data = payload.get("data")
    cursor = payload.get("nextSearchAfter")
    if not isinstance(data, list) or (
        "nextSearchAfter" in payload
        and cursor is not None
        and not isinstance(cursor, list)
    ):
        raise QuantDataClientError(
            "Unexpected exchange notifications response page shape."
        )
    return payload
