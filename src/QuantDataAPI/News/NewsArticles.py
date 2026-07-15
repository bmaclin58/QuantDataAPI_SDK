"""News Articles one-page JSON request and response helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping, Sequence

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import (
    add_filter,
    add_filter_expression,
    add_pagination,
    add_projection,
)
from QuantDataAPI.utility import JsonObject


def _parse_instant(name: str, value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value
    if "T" not in value and " " not in value:
        raise ValueError(f"{name} must be an ISO-8601 datetime.")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 datetime.") from exc


def build_news_articles_request(
    *,
    startTime: datetime | str | None = None,
    endTime: datetime | str | None = None,
    size: int | None = None,
    searchAfter: Sequence[Any] | None = None,
    includes: Sequence[str] | None = None,
    excludes: Sequence[str] | None = None,
    includeBody: bool | None = None,
    filterExpression: Mapping[str, Any] | None = None,
    tickers: Sequence[str] | None = None,
    topics: Sequence[str] | None = None,
    sentiments: Sequence[str] | None = None,
) -> JsonObject:
    """Build one documented News Articles page request."""
    if (startTime is None) != (endTime is None):
        raise ValueError("startTime and endTime must both be provided together.")

    body: JsonObject = {}
    if startTime is not None and endTime is not None:
        parsed_start = _parse_instant("startTime", startTime)
        parsed_end = _parse_instant("endTime", endTime)
        start_aware = parsed_start.utcoffset() is not None
        end_aware = parsed_end.utcoffset() is not None
        if start_aware != end_aware:
            raise ValueError("startTime and endTime must use compatible timezones.")
        if parsed_end <= parsed_start:
            raise ValueError("endTime must be after startTime.")
        body["timeRange"] = {"startTime": startTime, "endTime": endTime}

    projection_fields = tuple(includes or ()) + tuple(excludes or ())
    non_projectable = {
        field
        for field in projection_fields
        if isinstance(field, str) and field.upper() in {"BODY", "SENTIMENT"}
    }
    if non_projectable:
        names = ", ".join(sorted(non_projectable))
        raise ValueError(f"News field(s) are not projectable: {names}.")

    add_pagination(body, size=size, searchAfter=searchAfter)
    add_projection(body, includes=includes, excludes=excludes)
    if includeBody is not None:
        body["includeBody"] = includeBody
    add_filter(
        body,
        tickers=tickers,
        topics=topics,
        sentiments=sentiments,
    )
    add_filter_expression(body, filterExpression)
    return body


def normalize_news_articles(payload: JsonObject) -> JsonObject:
    """Validate and return one complete News Articles JSON page."""
    data = payload.get("data")
    cursor = payload.get("nextSearchAfter")
    if not isinstance(data, list) or (
        "nextSearchAfter" in payload
        and cursor is not None
        and not isinstance(cursor, list)
    ):
        raise QuantDataClientError("Unexpected news articles response page shape.")
    return payload
