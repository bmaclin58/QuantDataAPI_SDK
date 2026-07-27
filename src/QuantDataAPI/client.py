"""Core client for the QuantData.US REST API."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone as utc_timezone
from typing import Any, Mapping, Sequence, Unpack
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
from QuantDataAPI.Equities.DarkFlow import (
    DARK_FLOW_SCHEMA,
    build_dark_flow_request,
    normalize_dark_flow,
)
from QuantDataAPI.Equities.EquityPrints import (
    build_equity_prints_request,
    normalize_equity_prints,
)
from QuantDataAPI.Equities.ExchangeNotifications import (
    build_exchange_notifications_request,
    normalize_exchange_notifications,
)
from QuantDataAPI.Equities.MarketMap import (
    MARKET_MAP_SCHEMA,
    build_market_map_request,
    normalize_market_map,
)
from QuantDataAPI.Equities.StockPriceOverTime import (
    STOCK_PRICE_OVER_TIME_SCHEMA,
    build_stock_price_over_time_request,
    normalize_stock_price_over_time,
)
from QuantDataAPI.News.NewsArticles import (
    build_news_articles_request,
    normalize_news_articles,
)
from QuantDataAPI.OptionsEndpoint.ContractStatistics import (
    CONTRACT_STATISTICS_SCHEMA,
    build_contract_statistics_request,
    normalize_contract_statistics,
)
from QuantDataAPI.OptionsEndpoint.ContractTradeSideStatistics import (
    CONTRACT_TRADE_SIDE_STATISTICS_SCHEMA,
    build_contract_trade_side_statistics_request,
    normalize_contract_trade_side_statistics,
)
from QuantDataAPI.OptionsEndpoint.ExposureByExpiration import (
    EXPOSURE_BY_EXPIRATION_SCHEMA,
    build_exposure_by_expiration_request,
    normalize_exposure_by_expiration,
)
from QuantDataAPI.OptionsEndpoint.ExposureByStrike import (
    EXPOSURE_BY_STRIKE_SCHEMA,
    build_exposure_by_strike_request,
    normalize_exposure_by_strike,
)
from QuantDataAPI.OptionsEndpoint.GainersLosers import (
    GAINERS_LOSERS_SCHEMA,
    build_gainers_losers_request,
    normalize_gainers_losers,
)
from QuantDataAPI.OptionsEndpoint.HeatMap import (
    build_heat_map_request,
    normalize_heat_map,
)
from QuantDataAPI.OptionsEndpoint.IntervalMap import (
    INTERVAL_MAP_SCHEMA,
    build_interval_map_request,
    normalize_interval_map,
)
from QuantDataAPI.OptionsEndpoint.IVRank import (
    IV_RANK_SCHEMA,
    build_iv_rank_request,
    normalize_iv_rank,
)
from QuantDataAPI.OptionsEndpoint.MarketShare import (
    MARKET_SHARE_SCHEMA,
    build_market_share_request,
    normalize_market_share,
)
from QuantDataAPI.OptionsEndpoint.MaxPain import (
    MAX_PAIN_SCHEMA,
    build_max_pain_request,
    normalize_max_pain,
)
from QuantDataAPI.OptionsEndpoint.MaxPainOverTime import (
    MAX_PAIN_OVER_TIME_SCHEMA,
    build_max_pain_over_time_request,
    normalize_max_pain_over_time,
)
from QuantDataAPI.OptionsEndpoint.NetDrift import (
    NET_DRIFT_SCHEMA,
    build_net_drift_request,
    normalize_net_drift,
)
from QuantDataAPI.OptionsEndpoint.NetFlow import (
    NET_FLOW_SCHEMA,
    build_net_flow_request,
    normalize_net_flow,
)
from QuantDataAPI.OptionsEndpoint.OpenInterestByExpiration import (
    OPEN_INTEREST_BY_EXPIRATION_SCHEMA,
    build_open_interest_by_expiration_request,
    normalize_open_interest_by_expiration,
)
from QuantDataAPI.OptionsEndpoint.OpenInterestByStrike import (
    OPEN_INTEREST_BY_STRIKE_SCHEMA,
    build_open_interest_by_strike_request,
    normalize_open_interest_by_strike,
)
from QuantDataAPI.OptionsEndpoint.OpenInterestChange import (
    build_open_interest_change_request,
    normalize_open_interest_change,
)
from QuantDataAPI.OptionsEndpoint.OpenInterestOverTime import (
    OPEN_INTEREST_OVER_TIME_SCHEMA,
    build_open_interest_over_time_request,
    normalize_open_interest_over_time,
)
from QuantDataAPI.OptionsEndpoint.OptionPriceOverTime import (
    OPTION_PRICE_OVER_TIME_SCHEMA,
    build_option_price_over_time_request,
    normalize_option_price_over_time,
)
from QuantDataAPI.OptionsEndpoint.OrderFlowConsolidated import (
    build_order_flow_consolidated_request,
    normalize_order_flow_consolidated,
)
from QuantDataAPI.OptionsEndpoint.OrderFlowUnconsolidated import (
    build_order_flow_unconsolidated_request,
    normalize_order_flow_unconsolidated,
)
from QuantDataAPI.OptionsEndpoint.TermStructure import (
    TERM_STRUCTURE_SCHEMA,
    build_term_structure_request,
    normalize_term_structure,
)
from QuantDataAPI.OptionsEndpoint.VolatilityDrift import (
    VOLATILITY_DRIFT_SCHEMA,
    build_volatility_drift_request,
    normalize_volatility_drift,
)
from QuantDataAPI.OptionsEndpoint.VolatilitySkew import (
    VOLATILITY_SKEW_SCHEMA,
    build_volatility_skew_request,
    normalize_volatility_skew,
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
from QuantDataAPI.filterOptions import OptionTradeFilters
from QuantDataAPI.utility import (
    BASE_URL,
    CONTRACT_STATISTICS,
    CONTRACT_TRADE_SIDE_STATISTICS,
    DARK_FLOW,
    DARK_POOL_LEVELS,
    EQUITY_PRINTS,
    EXCHANGE_NOTIFICATIONS,
    EXPOSURE_BY_EXPIRATION,
    EXPOSURE_BY_STRIKE,
    GAINERS_LOSERS,
    HEAT_MAP,
    INTERVAL_MAP,
    IV_RANK,
    MARKET_MAP,
    MARKET_SHARE,
    MAX_PAIN,
    MAX_PAIN_OVER_TIME,
    NET_DRIFT,
    NET_FLOW,
    NEWS_ARTICLES,
    OPEN_INTEREST_BY_EXPIRATION,
    OPEN_INTEREST_BY_STRIKE,
    OPEN_INTEREST_CHANGE,
    OPEN_INTEREST_OVER_TIME,
    OPTION_PRICE_OVER_TIME,
    ORDER_FLOW_CONSOLIDATED,
    ORDER_FLOW_UNCONSOLIDATED,
    STOCK_PRICE_OVER_TIME,
    TERM_STRUCTURE,
    VOLATILITY_DRIFT,
    VOLATILITY_SKEW,
    JsonObject,
)

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
        api_key,
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
        if "T" not in value and " " not in value:
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
            if schema is None:
                return frame
            pandas_schema = {
                name: "datetime64[ns]" if dtype is date else dtype
                for name, dtype in schema.items()
            }
            return frame.astype(pandas_schema)

        return pl.DataFrame(converted_rows, schema=schema)

    def _require_json_output(self, endpoint_name: str) -> None:
        if self.output_type != "json":
            raise QuantDataConfigurationError(
                f"{endpoint_name} is paginated and only supports JSON output."
            )

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

    def get_dark_flow(
        self,
        ticker: str,
        *,
        sessionDate: date | datetime | str | None = None,
        startTime: datetime | str | None = None,
        endTime: datetime | str | None = None,
        aggregationPeriod: str | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return timestamp-bucketed dark-venue activity for one ticker."""
        request_body = build_dark_flow_request(
            ticker=ticker,
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            aggregationPeriod=aggregationPeriod,
        )
        payload = self._post(DARK_FLOW, request_body)
        rows = normalize_dark_flow(payload)
        return self._format_response(payload, rows=rows, schema=DARK_FLOW_SCHEMA)

    def get_equity_prints(
        self,
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
        """
        Return one validated Equity Prints page; JSON output only.
        https://quantdata.us/api/docs/endpoints/equity-prints
        """
        self._require_json_output("Equity Prints")
        request_body = build_equity_prints_request(
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            size=size,
            searchAfter=searchAfter,
            sortField=sortField,
            sortDirection=sortDirection,
            includes=includes,
            excludes=excludes,
            filterExpression=filterExpression,
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
        payload = self._post(EQUITY_PRINTS, request_body)
        normalize_equity_prints(payload)
        return self._format_response(payload, rows=[])

    def get_exchange_notifications(
        self,
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
        """Return one validated Exchange Notifications page; JSON output only."""
        self._require_json_output("Exchange Notifications")
        request_body = build_exchange_notifications_request(
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            size=size,
            searchAfter=searchAfter,
            sortField=sortField,
            sortDirection=sortDirection,
            includes=includes,
            excludes=excludes,
            filterExpression=filterExpression,
            tickers=tickers,
            types=types,
        )
        payload = self._post(EXCHANGE_NOTIFICATIONS, request_body)
        normalize_exchange_notifications(payload)
        return self._format_response(payload, rows=[])

    def get_market_map(
        self,
        *,
        sessionDate: date | datetime | str | None = None,
        snapshotTime: datetime | str | None = None,
        sectors: Sequence[str] | None = None,
        industries: Sequence[str] | None = None,
        filterExpression: Mapping[str, Any] | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return a market-wide company and price snapshot."""
        request_body = build_market_map_request(
            sessionDate=sessionDate,
            snapshotTime=snapshotTime,
            sectors=sectors,
            industries=industries,
            filterExpression=filterExpression,
        )
        payload = self._post(MARKET_MAP, request_body)
        rows = normalize_market_map(payload)
        return self._format_response(payload, rows=rows, schema=MARKET_MAP_SCHEMA)

    def get_stock_price_over_time(
        self,
        ticker: str,
        *,
        sessionDate: date | datetime | str | None = None,
        startTime: datetime | str | None = None,
        endTime: datetime | str | None = None,
        aggregationPeriod: str | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return timestamp-bucketed OHLC bars for one equity ticker."""
        request_body = build_stock_price_over_time_request(
            ticker=ticker,
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            aggregationPeriod=aggregationPeriod,
        )
        payload = self._post(STOCK_PRICE_OVER_TIME, request_body)
        rows = normalize_stock_price_over_time(payload)
        return self._format_response(
            payload,
            rows=rows,
            schema=STOCK_PRICE_OVER_TIME_SCHEMA,
        )

    def get_news_articles(
        self,
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
        """
        Return one validated News Articles page; JSON output only.

        """
        self._require_json_output("News Articles")
        request_body = build_news_articles_request(
            startTime=startTime,
            endTime=endTime,
            size=size,
            searchAfter=searchAfter,
            includes=includes,
            excludes=excludes,
            includeBody=includeBody,
            filterExpression=filterExpression,
            tickers=tickers,
            topics=topics,
            sentiments=sentiments,
        )
        payload = self._post(NEWS_ARTICLES, request_body)
        normalize_news_articles(payload)
        return self._format_response(payload, rows=[])

    def get_contract_statistics(
        self,
        *,
        sessionDate: date | datetime | str | None = None,
        startTime: datetime | str | None = None,
        endTime: datetime | str | None = None,
        filterExpression: Mapping[str, Any] | None = None,
        **filters: Unpack[OptionTradeFilters],
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return call-versus-put premium, trade-count, and volume totals."""
        request_body = build_contract_statistics_request(
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            filterExpression=filterExpression,
            **filters,
        )
        payload = self._post(CONTRACT_STATISTICS, request_body)
        rows = normalize_contract_statistics(payload)
        return self._format_response(
            payload,
            rows=rows,
            schema=CONTRACT_STATISTICS_SCHEMA,
        )

    def get_contract_trade_side_statistics(
        self,
        dataMode: str,
        *,
        sessionDate: date | datetime | str | None = None,
        startTime: datetime | str | None = None,
        endTime: datetime | str | None = None,
        filterExpression: Mapping[str, Any] | None = None,
        **filters: Unpack[OptionTradeFilters],
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return the selected metric by contract type and aggressor side."""
        request_body = build_contract_trade_side_statistics_request(
            dataMode=dataMode,
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            filterExpression=filterExpression,
            **filters,
        )
        data_mode = request_body["dataMode"]
        payload = self._post(CONTRACT_TRADE_SIDE_STATISTICS, request_body)
        rows = normalize_contract_trade_side_statistics(payload, data_mode)
        return self._format_response(
            payload,
            rows=rows,
            schema=CONTRACT_TRADE_SIDE_STATISTICS_SCHEMA,
        )

    def get_exposure_by_expiration(
        self,
        ticker: str,
        greekMode: str,
        representationMode: str,
        *,
        sessionDate: date | datetime | str | None = None,
        snapshotTime: datetime | str | None = None,
        filterExpression: Mapping[str, Any] | None = None,
        expirationDates: Sequence[str] | None = None,
        expirationDateRange: Mapping[str, Any] | None = None,
        strikePrices: Sequence[int | float] | None = None,
        strikePriceRange: Mapping[str, Any] | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """
        Return Greek exposure rolled up by expiration and strike.
        https://quantdata.us/api/docs/endpoints/exposure-by-expiration
        """
        request_body = build_exposure_by_expiration_request(
            ticker=ticker,
            greekMode=greekMode,
            representationMode=representationMode,
            sessionDate=sessionDate,
            snapshotTime=snapshotTime,
            filterExpression=filterExpression,
            expirationDates=expirationDates,
            expirationDateRange=expirationDateRange,
            strikePrices=strikePrices,
            strikePriceRange=strikePriceRange,
        )
        payload = self._post(EXPOSURE_BY_EXPIRATION, request_body)
        rows = normalize_exposure_by_expiration(payload)
        return self._format_response(
            payload,
            rows=rows,
            schema=EXPOSURE_BY_EXPIRATION_SCHEMA,
        )

    def get_exposure_by_strike(
        self,
        ticker: str,
        greekMode: str,
        representationMode: str,
        *,
        sessionDate: date | datetime | str | None = None,
        snapshotTime: datetime | str | None = None,
        filterExpression: Mapping[str, Any] | None = None,
        expirationDate: date | datetime | str | None = None,
        expirationDates: Sequence[str] | None = None,
        expirationDateRange: Mapping[str, Any] | None = None,
        strikePrices: Sequence[int | float] | None = None,
        strikePriceRange: Mapping[str, Any] | None = None,
        moneyTypes: Sequence[str] | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """
        Return Greek exposure aggregated by expiration and strike.
        https://quantdata.us/api/docs/endpoints/exposure-by-strike
        """
        request_body = build_exposure_by_strike_request(
            ticker=ticker,
            greekMode=greekMode,
            representationMode=representationMode,
            sessionDate=sessionDate,
            snapshotTime=snapshotTime,
            filterExpression=filterExpression,
            expirationDate=expirationDate,
            expirationDates=expirationDates,
            expirationDateRange=expirationDateRange,
            strikePrices=strikePrices,
            strikePriceRange=strikePriceRange,
            moneyTypes=moneyTypes,
        )
        payload = self._post(EXPOSURE_BY_STRIKE, request_body)
        rows = normalize_exposure_by_strike(payload)
        return self._format_response(
            payload,
            rows=rows,
            schema=EXPOSURE_BY_STRIKE_SCHEMA,
        )

    def get_gainers_losers(
        self,
        *,
        sessionDate: date | datetime | str | None = None,
        startTime: datetime | str | None = None,
        endTime: datetime | str | None = None,
        filterExpression: Mapping[str, Any] | None = None,
        tickers: Sequence[str] | None = None,
        sectors: Sequence[str] | None = None,
        industries: Sequence[str] | None = None,
        expirationDates: Sequence[str] | None = None,
        expirationDateRange: Mapping[str, Any] | None = None,
        dteRange: Mapping[str, Any] | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return ticker-level bullish and bearish option-flow summaries."""
        request_body = build_gainers_losers_request(
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            filterExpression=filterExpression,
            tickers=tickers,
            sectors=sectors,
            industries=industries,
            expirationDates=expirationDates,
            expirationDateRange=expirationDateRange,
            dteRange=dteRange,
        )
        payload = self._post(GAINERS_LOSERS, request_body)
        rows = normalize_gainers_losers(payload)
        return self._format_response(payload, rows=rows, schema=GAINERS_LOSERS_SCHEMA)

    def get_heat_map(
        self,
        ticker: str,
        dataMode: str,
        *,
        sessionDate: date | datetime | str | None = None,
        snapshotTime: datetime | str | None = None,
        filterExpression: Mapping[str, Any] | None = None,
        expirationDate: date | datetime | str | None = None,
        expirationDates: Sequence[str] | None = None,
        expirationDateRange: Mapping[str, Any] | None = None,
        strikePrices: Sequence[int | float] | None = None,
        strikePriceRange: Mapping[str, Any] | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return a mode-specific expiration-by-strike heat-map grid."""
        request_body = build_heat_map_request(
            ticker=ticker,
            dataMode=dataMode,
            sessionDate=sessionDate,
            snapshotTime=snapshotTime,
            filterExpression=filterExpression,
            expirationDate=expirationDate,
            expirationDates=expirationDates,
            expirationDateRange=expirationDateRange,
            strikePrices=strikePrices,
            strikePriceRange=strikePriceRange,
        )
        payload = self._post(HEAT_MAP, request_body)
        rows, schema = normalize_heat_map(payload)
        return self._format_response(payload, rows=rows, schema=schema)

    def get_interval_map(
        self,
        ticker: str,
        greekMode: str,
        *,
        sessionDate: date | datetime | str | None = None,
        startTime: datetime | str | None = None,
        endTime: datetime | str | None = None,
        aggregationPeriod: str | None = None,
        expirationDate: date | datetime | str | None = None,
        minStrikePrice: int | float | None = None,
        maxStrikePrice: int | float | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return time-bucketed Greek exposure across a contract chain."""
        request_body = build_interval_map_request(
            ticker=ticker,
            greekMode=greekMode,
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            aggregationPeriod=aggregationPeriod,
            expirationDate=expirationDate,
            minStrikePrice=minStrikePrice,
            maxStrikePrice=maxStrikePrice,
        )
        payload = self._post(INTERVAL_MAP, request_body)
        rows = normalize_interval_map(payload)
        return self._format_response(payload, rows=rows, schema=INTERVAL_MAP_SCHEMA)

    def get_iv_rank(
        self,
        ticker: str,
        lookBackPeriod: int,
        maturity: int,
        *,
        contractTypes: Sequence[str] | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return per-session implied-volatility window statistics."""
        request_body = build_iv_rank_request(
            ticker=ticker,
            lookBackPeriod=lookBackPeriod,
            maturity=maturity,
            contractTypes=contractTypes,
        )
        payload = self._post(IV_RANK, request_body)
        rows = normalize_iv_rank(payload)
        return self._format_response(payload, rows=rows, schema=IV_RANK_SCHEMA)

    def get_market_share(
        self,
        *,
        sessionDate: date | datetime | str | None = None,
        startTime: datetime | str | None = None,
        endTime: datetime | str | None = None,
        filterExpression: Mapping[str, Any] | None = None,
        **filters: Unpack[OptionTradeFilters],
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return options activity totals grouped by exchange."""
        request_body = build_market_share_request(
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            filterExpression=filterExpression,
            **filters,
        )
        payload = self._post(MARKET_SHARE, request_body)
        rows = normalize_market_share(payload)
        return self._format_response(payload, rows=rows, schema=MARKET_SHARE_SCHEMA)

    def get_max_pain(
        self,
        ticker: str,
        expirationDate: date | datetime | str,
        *,
        sessionDate: date | datetime | str | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return per-strike intrinsic values and max-pain metadata."""
        request_body = build_max_pain_request(
            ticker=ticker,
            expirationDate=expirationDate,
            sessionDate=sessionDate,
        )
        payload = self._post(MAX_PAIN, request_body)
        rows = normalize_max_pain(payload)
        return self._format_response(payload, rows=rows, schema=MAX_PAIN_SCHEMA)

    def get_max_pain_over_time(
        self,
        ticker: str,
        *,
        sessionDate: date | datetime | str | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return the max-pain strike for each expiration in a chain."""
        request_body = build_max_pain_over_time_request(
            ticker=ticker,
            sessionDate=sessionDate,
        )
        payload = self._post(MAX_PAIN_OVER_TIME, request_body)
        rows = normalize_max_pain_over_time(payload)
        return self._format_response(
            payload,
            rows=rows,
            schema=MAX_PAIN_OVER_TIME_SCHEMA,
        )

    def get_net_drift(
        self,
        *,
        sessionDate: date | datetime | str | None = None,
        startTime: datetime | str | None = None,
        endTime: datetime | str | None = None,
        aggregationPeriod: str | None = None,
        filterExpression: Mapping[str, Any] | None = None,
        ticker: str | None = None,
        tickers: Sequence[str] | None = None,
        expirationDates: Sequence[str] | None = None,
        expirationDateRange: Mapping[str, Any] | None = None,
        strikePrices: Sequence[int | float] | None = None,
        strikePriceRange: Mapping[str, Any] | None = None,
        moneyTypes: Sequence[str] | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return per-bucket call and put premium drift."""
        request_body = build_net_drift_request(
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            aggregationPeriod=aggregationPeriod,
            filterExpression=filterExpression,
            ticker=ticker,
            tickers=tickers,
            expirationDates=expirationDates,
            expirationDateRange=expirationDateRange,
            strikePrices=strikePrices,
            strikePriceRange=strikePriceRange,
            moneyTypes=moneyTypes,
        )
        payload = self._post(NET_DRIFT, request_body)
        rows = normalize_net_drift(payload)
        return self._format_response(payload, rows=rows, schema=NET_DRIFT_SCHEMA)

    def get_net_flow(
        self,
        dataMode: str,
        *,
        sessionDate: date | datetime | str | None = None,
        startTime: datetime | str | None = None,
        endTime: datetime | str | None = None,
        aggregationPeriod: str | None = None,
        filterExpression: Mapping[str, Any] | None = None,
        ticker: str | None = None,
        tickers: Sequence[str] | None = None,
        expirationDates: Sequence[str] | None = None,
        expirationDateRange: Mapping[str, Any] | None = None,
        strikePrices: Sequence[int | float] | None = None,
        strikePriceRange: Mapping[str, Any] | None = None,
        moneyTypes: Sequence[str] | None = None,
        tradeSideCodes: Sequence[str] | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return per-bucket call and put net premium or volume."""
        request_body = build_net_flow_request(
            dataMode=dataMode,
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            aggregationPeriod=aggregationPeriod,
            filterExpression=filterExpression,
            ticker=ticker,
            tickers=tickers,
            expirationDates=expirationDates,
            expirationDateRange=expirationDateRange,
            strikePrices=strikePrices,
            strikePriceRange=strikePriceRange,
            moneyTypes=moneyTypes,
            tradeSideCodes=tradeSideCodes,
        )
        payload = self._post(NET_FLOW, request_body)
        rows = normalize_net_flow(payload)
        return self._format_response(payload, rows=rows, schema=NET_FLOW_SCHEMA)

    def get_open_interest_by_expiration(
        self,
        ticker: str,
        *,
        sessionDate: date | datetime | str | None = None,
        strikePrice: int | float | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return call and put open interest grouped by expiration."""
        request_body = build_open_interest_by_expiration_request(
            ticker=ticker,
            sessionDate=sessionDate,
            strikePrice=strikePrice,
        )
        payload = self._post(OPEN_INTEREST_BY_EXPIRATION, request_body)
        rows = normalize_open_interest_by_expiration(payload)
        return self._format_response(
            payload,
            rows=rows,
            schema=OPEN_INTEREST_BY_EXPIRATION_SCHEMA,
        )

    def get_open_interest_by_strike(
        self,
        ticker: str,
        *,
        sessionDate: date | datetime | str | None = None,
        expirationDate: date | datetime | str | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return call and put open interest grouped by strike."""
        request_body = build_open_interest_by_strike_request(
            ticker=ticker,
            sessionDate=sessionDate,
            expirationDate=expirationDate,
        )
        payload = self._post(OPEN_INTEREST_BY_STRIKE, request_body)
        rows = normalize_open_interest_by_strike(payload)
        return self._format_response(
            payload,
            rows=rows,
            schema=OPEN_INTEREST_BY_STRIKE_SCHEMA,
        )

    def get_open_interest_change(
        self,
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
        """Return one validated Open Interest Change page; JSON output only."""
        self._require_json_output("Open Interest Change")
        request_body = build_open_interest_change_request(
            sessionDate=sessionDate,
            size=size,
            searchAfter=searchAfter,
            sortField=sortField,
            sortDirection=sortDirection,
            includes=includes,
            excludes=excludes,
            filterExpression=filterExpression,
            tickers=tickers,
            contractTypes=contractTypes,
            strikePrices=strikePrices,
            strikePriceRange=strikePriceRange,
            expirationDates=expirationDates,
            expirationDateRange=expirationDateRange,
            previousOpenInterestRange=previousOpenInterestRange,
            currentOpenInterestRange=currentOpenInterestRange,
            changeInOpenInterestRange=changeInOpenInterestRange,
            percentChangeInOpenInterestRange=percentChangeInOpenInterestRange,
        )
        payload = self._post(OPEN_INTEREST_CHANGE, request_body)
        normalize_open_interest_change(payload)
        return self._format_response(payload, rows=[])

    def get_open_interest_over_time(
        self,
        ticker: str,
        *,
        expirationDate: date | datetime | str | None = None,
        strikePrice: int | float | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return call and put open interest across available sessions."""
        request_body = build_open_interest_over_time_request(
            ticker=ticker,
            expirationDate=expirationDate,
            strikePrice=strikePrice,
        )
        payload = self._post(OPEN_INTEREST_OVER_TIME, request_body)
        rows = normalize_open_interest_over_time(payload)
        return self._format_response(
            payload,
            rows=rows,
            schema=OPEN_INTEREST_OVER_TIME_SCHEMA,
        )

    def get_option_price_over_time(
        self,
        *,
        sessionDate: date | datetime | str | None = None,
        startTime: datetime | str | None = None,
        endTime: datetime | str | None = None,
        aggregationPeriod: str | None = None,
        osi: str | None = None,
        ticker: str | None = None,
        expirationDate: date | datetime | str | None = None,
        strikePrice: int | float | None = None,
        contractType: str | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return OHLCV bars for exactly one options contract."""
        request_body = build_option_price_over_time_request(
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            aggregationPeriod=aggregationPeriod,
            osi=osi,
            ticker=ticker,
            expirationDate=expirationDate,
            strikePrice=strikePrice,
            contractType=contractType,
        )
        payload = self._post(OPTION_PRICE_OVER_TIME, request_body)
        rows = normalize_option_price_over_time(payload)
        return self._format_response(
            payload,
            rows=rows,
            schema=OPTION_PRICE_OVER_TIME_SCHEMA,
        )

    def get_order_flow_consolidated(
        self,
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
        """Return one validated Consolidated Order Flow page; JSON only."""
        self._require_json_output("Order Flow Consolidated")
        request_body = build_order_flow_consolidated_request(
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            size=size,
            searchAfter=searchAfter,
            sortField=sortField,
            sortDirection=sortDirection,
            includes=includes,
            excludes=excludes,
            includeComprisingTrades=includeComprisingTrades,
            includeStatistics=includeStatistics,
            filterExpression=filterExpression,
            **filters,
        )
        payload = self._post(ORDER_FLOW_CONSOLIDATED, request_body)
        normalize_order_flow_consolidated(payload)
        return self._format_response(payload, rows=[])

    def get_order_flow_unconsolidated(
        self,
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
        """Return one validated Unconsolidated Order Flow page; JSON only."""
        self._require_json_output("Order Flow Unconsolidated")
        request_body = build_order_flow_unconsolidated_request(
            sessionDate=sessionDate,
            startTime=startTime,
            endTime=endTime,
            size=size,
            searchAfter=searchAfter,
            sortField=sortField,
            sortDirection=sortDirection,
            includes=includes,
            excludes=excludes,
            includeStatistics=includeStatistics,
            filterExpression=filterExpression,
            **filters,
        )
        payload = self._post(ORDER_FLOW_UNCONSOLIDATED, request_body)
        normalize_order_flow_unconsolidated(payload)
        return self._format_response(payload, rows=[])

    def get_term_structure(
        self,
        ticker: str,
        *,
        sessionDate: date | datetime | str | None = None,
        snapshotTime: datetime | str | None = None,
        expirationDates: Sequence[str] | None = None,
        expirationDateRange: Mapping[str, Any] | None = None,
        strikePrices: Sequence[int | float] | None = None,
        strikePriceRange: Mapping[str, Any] | None = None,
        moneyTypes: Sequence[str] | None = None,
        deltaRange: Mapping[str, Any] | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return delta, implied volatility, and moneyness across a chain."""
        request_body = build_term_structure_request(
            ticker=ticker,
            sessionDate=sessionDate,
            snapshotTime=snapshotTime,
            expirationDates=expirationDates,
            expirationDateRange=expirationDateRange,
            strikePrices=strikePrices,
            strikePriceRange=strikePriceRange,
            moneyTypes=moneyTypes,
            deltaRange=deltaRange,
        )
        payload = self._post(TERM_STRUCTURE, request_body)
        rows = normalize_term_structure(payload)
        return self._format_response(payload, rows=rows, schema=TERM_STRUCTURE_SCHEMA)

    def get_volatility_drift(
        self,
        ticker: str,
        *,
        sessionDate: date | datetime | str | None = None,
        expirationDate: date | datetime | str | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return one-minute realized and implied volatility buckets."""
        request_body = build_volatility_drift_request(
            ticker=ticker,
            sessionDate=sessionDate,
            expirationDate=expirationDate,
        )
        payload = self._post(VOLATILITY_DRIFT, request_body)
        rows = normalize_volatility_drift(payload)
        return self._format_response(
            payload,
            rows=rows,
            schema=VOLATILITY_DRIFT_SCHEMA,
        )

    def get_volatility_skew(
        self,
        ticker: str,
        *,
        sessionDate: date | datetime | str | None = None,
        snapshotTime: datetime | str | None = None,
        contractTypes: Sequence[str] | None = None,
        expirationDate: date | datetime | str | None = None,
        expirationDates: Sequence[str] | None = None,
        expirationDateRange: Mapping[str, Any] | None = None,
    ) -> JsonObject | pd.DataFrame | pl.DataFrame:
        """Return the implied-volatility surface for one ticker."""
        request_body = build_volatility_skew_request(
            ticker=ticker,
            sessionDate=sessionDate,
            snapshotTime=snapshotTime,
            contractTypes=contractTypes,
            expirationDate=expirationDate,
            expirationDates=expirationDates,
            expirationDateRange=expirationDateRange,
        )
        payload = self._post(VOLATILITY_SKEW, request_body)
        rows = normalize_volatility_skew(payload)
        return self._format_response(
            payload,
            rows=rows,
            schema=VOLATILITY_SKEW_SCHEMA,
        )
