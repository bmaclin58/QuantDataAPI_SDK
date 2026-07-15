from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo

JsonObject = dict[str, Any]

BASE_URL = "https://api.quantdata.us"

# Options Endpoints
CONTRACT_STATISTICS = "/v1/options/tool/contract-statistics"
CONTRACT_TRADE_SIDE_STATISTICS = "/v1/options/tool/contract-trade-side-statistics"
EXPOSURE_BY_EXPIRATION = "/v1/options/tool/exposure-by-expiration"
EXPOSURE_BY_STRIKE = "/v1/options/tool/exposure-by-strike"
GAINERS_LOSERS = "/v1/options/tool/gainers-losers"
HEAT_MAP = "/v1/options/tool/heat-map"
INTERVAL_MAP = "/v1/options/tool/interval-map"
IV_RANK = "/v1/options/tool/iv-rank"
MARKET_SHARE = "/v1/options/tool/market-share"
MAX_PAIN = "/v1/options/tool/max-pain"
MAX_PAIN_OVER_TIME = "/v1/options/tool/max-pain-over-time"
NET_DRIFT = "/v1/options/tool/net-drift"
NET_FLOW = "/v1/options/tool/net-flow"
OPEN_INTEREST_BY_EXPIRATION = "/v1/options/tool/open-interest-by-expiration"
OPEN_INTEREST_BY_STRIKE = "/v1/options/tool/open-interest-by-strike"
OPEN_INTEREST_CHANGE = "/v1/options/tool/open-interest-change"
OPEN_INTEREST_OVER_TIME = "/v1/options/tool/open-interest-over-time"
OPTION_PRICE_OVER_TIME = "/v1/options/tool/option-price-over-time"
ORDER_FLOW_CONSOLIDATED = "/v1/options/tool/order-flow/consolidated"
ORDER_FLOW_UNCONSOLIDATED = "/v1/options/tool/order-flow/unconsolidated"
TERM_STRUCTURE = "/v1/options/tool/term-structure"
VOLATILITY_DRIFT = "/v1/options/tool/volatility-drift"
VOLATILITY_SKEW = "/v1/options/tool/volatility-skew"

# Equities Endpoints
DARK_FLOW = "/v1/equities/tool/dark-flow"
DARK_POOL_LEVELS = "/v1/equities/tool/dark-pool-levels"
EQUITY_PRINTS = "/v1/equities/tool/equity-prints"
EXCHANGE_NOTIFICATIONS = "/v1/equities/tool/exchange-notifications"
MARKET_MAP = "/v1/equities/tool/market-map"
STOCK_PRICE_OVER_TIME = "/v1/equities/tool/stock-price-over-time"

# News Endpoints
NEWS_ARTICLES = "/v1/news/tool/news-articles"

OPTIONS_ENDPOINTS = (
    CONTRACT_STATISTICS,
    CONTRACT_TRADE_SIDE_STATISTICS,
    EXPOSURE_BY_EXPIRATION,
    EXPOSURE_BY_STRIKE,
    GAINERS_LOSERS,
    HEAT_MAP,
    INTERVAL_MAP,
    IV_RANK,
    MARKET_SHARE,
    MAX_PAIN,
    MAX_PAIN_OVER_TIME,
    NET_DRIFT,
    NET_FLOW,
    OPEN_INTEREST_BY_EXPIRATION,
    OPEN_INTEREST_BY_STRIKE,
    OPEN_INTEREST_CHANGE,
    OPEN_INTEREST_OVER_TIME,
    OPTION_PRICE_OVER_TIME,
    ORDER_FLOW_CONSOLIDATED,
    ORDER_FLOW_UNCONSOLIDATED,
    TERM_STRUCTURE,
    VOLATILITY_DRIFT,
    VOLATILITY_SKEW,
)

EQUITIES_ENDPOINTS = (
    DARK_FLOW,
    DARK_POOL_LEVELS,
    EQUITY_PRINTS,
    EXCHANGE_NOTIFICATIONS,
    MARKET_MAP,
    STOCK_PRICE_OVER_TIME,
)

NEWS_ENDPOINTS = (NEWS_ARTICLES,)

PAGINATED_ENDPOINTS = (ORDER_FLOW_CONSOLIDATED,
                       ORDER_FLOW_UNCONSOLIDATED,
                       EQUITY_PRINTS,
                       OPEN_INTEREST_CHANGE,
                       EXCHANGE_NOTIFICATIONS,
                       NEWS_ARTICLES
                       )

ALL_ENDPOINTS = OPTIONS_ENDPOINTS + EQUITIES_ENDPOINTS + NEWS_ENDPOINTS

CONTRACT_TYPES = {"CALL", "PUT"}
GREEK_MODES = {"CHARM", "DELTA", "GAMMA", "VANNA"}
REPRESENTATION_MODES = {"PER_ONE_DOLLAR_MOVE", "PER_ONE_PERCENT_MOVE", "RAW"}
TRADE_SIDE_STAT_DATA_MODES = {"PREMIUM", "TRADE_COUNT", "VOLUME"}
NET_FLOW_DATA_MODES = {"NET_PREMIUM", "NET_VOLUME"}
SORT_DIRECTIONS = {"ASCENDING", "DESCENDING"}

HEAT_MAP_DATA_MODES = {
    "NET_CHARM_EXPOSURE",
    "NET_DELTA_EXPOSURE",
    "NET_GAMMA_EXPOSURE",
    "NET_VANNA_EXPOSURE",
    "NET_OPEN_INTEREST",
    "NET_PREMIUM",
    "NET_TRADE_COUNT",
    "NET_VOLUME",
}
for _leg in ("CALL", "PUT"):
    for _metric in (
            "ASK_PRICE",
            "BID_PRICE",
            "CHARM",
            "COLOR",
            "DELTA",
            "GAMMA",
            "IMPLIED_VOLATILITY",
            "OMEGA",
            "OPTION_PRICE",
            "RHO",
            "SIGMA",
            "SPEED",
            "THETA",
            "ULTIMA",
            "VANNA",
            "VEGA",
            "VETA",
            "VOMMA",
            "ZOMMA",
    ): HEAT_MAP_DATA_MODES.add(f"{_leg}_{_metric}")


def clean_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return to_quantdata_utc_instant(value)
    if isinstance(value, date):
        return to_quantdata_date(value)
    if isinstance(value, Mapping):
        return clean_dict(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [clean_value(item) for item in value]
    return value


def clean_dict(values: Mapping[str, Any]) -> JsonObject:
    return {
        key: clean_value(value)
        for key, value in values.items()
        if value is not None
    }


def to_quantdata_date(value: date | datetime | str) -> str:
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str):
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("Dates must be formatted as YYYY-MM-DD.") from exc
        if parsed.strftime("%Y-%m-%d") != value:
            raise ValueError("Dates must be formatted as YYYY-MM-DD.")
        return value
    raise TypeError("Dates must be date, datetime, or YYYY-MM-DD strings.")


def to_quantdata_utc_instant(dt: datetime | str, LocalTZ: str = "America/New_York") -> str:
    if isinstance(dt, str):
        return dt
    local_Timezone = ZoneInfo(LocalTZ)
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=local_Timezone)
    return (
        dt.astimezone(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )

def _as_float(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise TypeError("numeric value expected")
    return float(value)