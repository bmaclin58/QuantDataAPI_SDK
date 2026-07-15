"""Core client for the QuantData.US REST API."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone as utc_timezone
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd
import polars as pl
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from QuantDataAPI.Equities.DarkPoolLevels import (
    DARK_POOL_LEVELS_SCHEMA,
    build_dark_pool_levels_request,
    normalize_dark_pool_levels,
)
from QuantDataAPI.errors import (
    QuantDataAuthenticationError,
    QuantDataAuthorizationError,
    QuantDataBadRequestError,
    QuantDataClientError,
    QuantDataConfigurationError,
    QuantDataDataUnavailableError,
    QuantDataHttpError,
    QuantDataInternalError,
    QuantDataOpraAgreementRequiredError,
    QuantDataRateLimitError,
    QuantDataValidationError,
)
from QuantDataAPI.utility import BASE_URL, DARK_POOL_LEVELS, JsonObject

RETRY_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
OUTPUT_TYPES = frozenset({"json", "pandas", "polars"})

_ERROR_CLASS_BY_TYPE = {
    error_class.problem_type: error_class
    for error_class in (
        QuantDataValidationError,
        QuantDataBadRequestError,
        QuantDataAuthenticationError,
        QuantDataAuthorizationError,
        QuantDataOpraAgreementRequiredError,
        QuantDataDataUnavailableError,
        QuantDataRateLimitError,
        QuantDataInternalError,
    )
}

class QuantDataAPI_Client:
    """Thin client for authenticated QuantData.US requests."""

    def __init__(
        self,
        api_key: str,
        *,
        output_type: str = "json",
        timezone: str = "America/New_York",
        convertTimezone: bool = True,
        base_url: str = BASE_URL,
        timeout: float | int = 30,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise QuantDataConfigurationError("api_key must be a non-empty string.")
        if not isinstance(output_type, str):
            raise QuantDataConfigurationError(
                "output_type must be one of: json, pandas, polars."
            )
        normalized_output = output_type.strip().lower()
        if normalized_output not in OUTPUT_TYPES:
            raise QuantDataConfigurationError(
                "output_type must be one of: json, pandas, polars."
            )
        if type(convertTimezone) is not bool:
            raise QuantDataConfigurationError("convertTimezone must be True or False.")
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or timeout <= 0
        ):
            raise QuantDataConfigurationError("timeout must be a positive number.")
        if not isinstance(timezone, str):
            raise QuantDataConfigurationError(
                "timezone must be a valid IANA timezone name."
            )
        try:
            selected_timezone = ZoneInfo(timezone)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise QuantDataConfigurationError(
                "timezone must be a valid IANA timezone name."
            ) from exc

        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.output_type = normalized_output
        self.timezone = timezone
        self.convertTimezone = convertTimezone
        self._timezone = selected_timezone
        self._session = requests.Session()
        self._session.headers["Authorization"] = f"Bearer {self.api_key}"

        retry = Retry(
            total=2,
            connect=2,
            read=2,
            status=2,
            backoff_factor=0.5,
            status_forcelist=RETRY_STATUS_CODES,
            allowed_methods=frozenset({"POST"}),
            respect_retry_after_header=True,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def _serialize_request_value(self, value: Any) -> Any:
        if isinstance(value, datetime):
            if not self.convertTimezone:
                return value.isoformat()
            return self._as_utc_instant(value)
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            if not self.convertTimezone:
                return value
            parsed = self._parse_iso_datetime(value)
            return self._as_utc_instant(parsed) if parsed is not None else value
        if isinstance(value, Mapping):
            return {
                key: self._serialize_request_value(item)
                for key, item in value.items()
            }
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return [self._serialize_request_value(item) for item in value]
        return value

    def _as_utc_instant(self, value: datetime) -> str:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            value = value.replace(tzinfo=self._timezone)
        return value.astimezone(utc_timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _parse_iso_datetime(value: str) -> datetime | None:
        if "T" not in value:
            return None
        try:
            normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
            return datetime.fromisoformat(normalized)
        except ValueError:
            return None

    def _convert_response_value(self, value: Any, *, for_dataframe: bool) -> Any:
        if not self.convertTimezone:
            return value
        if isinstance(value, str):
            parsed = self._parse_iso_datetime(value)
            if (
                parsed is None
                or parsed.tzinfo is None
                or parsed.utcoffset() != timedelta(0)
            ):
                return value
            converted = parsed.astimezone(self._timezone)
            return converted if for_dataframe else converted.isoformat()
        if isinstance(value, Mapping):
            return {
                key: self._convert_response_value(item, for_dataframe=for_dataframe)
                for key, item in value.items()
            }
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return [
                self._convert_response_value(item, for_dataframe=for_dataframe)
                for item in value
            ]
        return value

    def _post(self, path: str, json_body: JsonObject | None = None) -> JsonObject:
        response = self._session.post(
            f"{self.base_url}{path}",
            json=self._serialize_request_value(json_body or {}),
            timeout=self.timeout,
        )
        return self._handle(response)

    def _handle(self, response: requests.Response) -> JsonObject:
        try:
            body = response.json()
        except ValueError as exc:
            if 200 <= response.status_code < 300:
                raise QuantDataClientError("QuantData returned invalid JSON.") from exc
            body = {"detail": response.text}

        if not isinstance(body, dict):
            raise QuantDataClientError("QuantData returned a non-object JSON response.")
        if 200 <= response.status_code < 300:
            return body

        message = body.get("message") or body.get("detail") or response.text
        error_class = _ERROR_CLASS_BY_TYPE.get(body.get("type"), QuantDataHttpError)
        raise error_class(
            response.status_code,
            message,
            headers=dict(response.headers),
            problem=body,
        )

    def _format_response(
        self,
        payload: JsonObject,
        *,
        rows: list[dict[str, Any]],
        schema: Mapping[str, type] | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        if self.output_type == "json":
            return self._convert_response_value(payload, for_dataframe=False)

        converted_rows = self._convert_response_value(rows, for_dataframe=True)
        if self.output_type == "pandas":
            frame = pd.DataFrame.from_records(
                converted_rows,
                columns=list(schema) if schema is not None else None,
            )
            return frame.astype(schema) if schema is not None else frame

        return pl.DataFrame(converted_rows, schema=schema)

    def get_dark_pool_levels(
        self,
        ticker: str,
        startDate: date | datetime | str,
        endDate: date | datetime | str | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return dark-pool activity aggregated by price level."""
        request_body = build_dark_pool_levels_request(
            ticker=ticker,
            startDate=startDate,
            endDate=endDate,
        )
        payload = self._post(DARK_POOL_LEVELS, request_body)
        rows = normalize_dark_pool_levels(payload)
        return self._format_response(
            payload,
            rows=rows,
            schema=DARK_POOL_LEVELS_SCHEMA,
        )
