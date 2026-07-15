from typing import Any, Mapping, Sequence
from datetime import date, datetime, timedelta, timezone

from QuantDataAPI.utility import clean_dict, to_quantdata_date, CONTRACT_TYPES, to_quantdata_utc_instant, \
    SORT_DIRECTIONS
from QuantDataAPI.validationChecks import validate_enum, validate_enum_sequence

JsonObject = dict[str, Any]

def add_filter(params: JsonObject, **filters: Any) -> None:
    values = clean_dict(filters)
    if values:
        params["filter"] = values

def option_trade_filters(
    *,
    ticker: str | None = None,
    tickers: Sequence[str] | None = None,
    sectors: Sequence[str] | None = None,
    industries: Sequence[str] | None = None,
    exchanges: Sequence[str] | None = None,
    expirationDate: date | datetime | str | None = None,
    expirationDates: Sequence[str] | None = None,
    expirationDateRange: Mapping[str, Any] | None = None,
    dte: int | float | None = None,
    dteRange: Mapping[str, Any] | None = None,
    contractType: str | None = None,
    contractTypes: Sequence[str] | None = None,
    osi: str | None = None,
    strikePrice: int | float | None = None,
    strikePrices: Sequence[int | float] | None = None,
    strikePriceRange: Mapping[str, Any] | None = None,
    stockPriceRange: Mapping[str, Any] | None = None,
    askPriceRange: Mapping[str, Any] | None = None,
    bidPriceRange: Mapping[str, Any] | None = None,
    bidAskSpreadRange: Mapping[str, Any] | None = None,
    optionPriceRange: Mapping[str, Any] | None = None,
    premiumRange: Mapping[str, Any] | None = None,
    sizeRange: Mapping[str, Any] | None = None,
    volumeRange: Mapping[str, Any] | None = None,
    openInterestRange: Mapping[str, Any] | None = None,
    impliedVolatilityRange: Mapping[str, Any] | None = None,
    moneynessInDollarsRange: Mapping[str, Any] | None = None,
    moneynessInPercentRange: Mapping[str, Any] | None = None,
    moneyType: str | None = None,
    moneyTypes: Sequence[str] | None = None,
    sentiment: str | None = None,
    sentimentTypes: Sequence[str] | None = None,
    tradeSideCode: str | None = None,
    tradeSideCodes: Sequence[str] | None = None,
    tradeTypes: Sequence[str] | None = None,
    tradeTimeRange: Mapping[str, Any] | None = None,
    tradeConsolidationTypes: Sequence[str] | None = None,
    isEtf: bool | None = None,
    isIndex: bool | None = None,
    isOpeningPosition: bool | None = None,
    isUnusual: bool | None = None,
    isVolumeGreaterThanOpenInterest: bool | None = None,
    isCancelled: bool | None = None,
    isComplex: bool | None = None,
    isComplexToComplex: bool | None = None,
    isElectronicCross: bool | None = None,
    isFloor: bool | None = None,
    isLegging: bool | None = None,
    isPriceImprovement: bool | None = None,
    isSimpleToSimple: bool | None = None,
    isTied: bool | None = None,
    isGoldenSweep: bool | None = None,
    deltaRange: Mapping[str, Any] | None = None,
    gammaRange: Mapping[str, Any] | None = None,
    thetaRange: Mapping[str, Any] | None = None,
    vegaRange: Mapping[str, Any] | None = None,
    rhoRange: Mapping[str, Any] | None = None,
    charmRange: Mapping[str, Any] | None = None,
    colorRange: Mapping[str, Any] | None = None,
    speedRange: Mapping[str, Any] | None = None,
    vannaRange: Mapping[str, Any] | None = None,
    vommaRange: Mapping[str, Any] | None = None,
    vetaRange: Mapping[str, Any] | None = None,
    omegaRange: Mapping[str, Any] | None = None,
    sigmaRange: Mapping[str, Any] | None = None,
    ultimaRange: Mapping[str, Any] | None = None,
    zommaRange: Mapping[str, Any] | None = None,
) -> JsonObject:
    return clean_dict({
        "ticker": ticker,
        "tickers": tickers,
        "sectors": sectors,
        "industries": industries,
        "exchanges": exchanges,
        "expirationDate": (
            to_quantdata_date(expirationDate)
            if expirationDate is not None
            else None
        ),
        "expirationDates": expirationDates,
        "expirationDateRange": expirationDateRange,
        "dte": dte,
        "dteRange": dteRange,
        "contractType": (
            validate_enum("contractType", contractType, CONTRACT_TYPES)
            if contractType is not None
            else None
        ),
        "contractTypes": validate_enum_sequence(
            "contractTypes",
            contractTypes,
            CONTRACT_TYPES,
        ),
        "osi": osi,
        "strikePrice": strikePrice,
        "strikePrices": strikePrices,
        "strikePriceRange": strikePriceRange,
        "stockPriceRange": stockPriceRange,
        "askPriceRange": askPriceRange,
        "bidPriceRange": bidPriceRange,
        "bidAskSpreadRange": bidAskSpreadRange,
        "optionPriceRange": optionPriceRange,
        "premiumRange": premiumRange,
        "sizeRange": sizeRange,
        "volumeRange": volumeRange,
        "openInterestRange": openInterestRange,
        "impliedVolatilityRange": impliedVolatilityRange,
        "moneynessInDollarsRange": moneynessInDollarsRange,
        "moneynessInPercentRange": moneynessInPercentRange,
        "moneyType": moneyType,
        "moneyTypes": moneyTypes,
        "sentiment": sentiment,
        "sentimentTypes": sentimentTypes,
        "tradeSideCode": tradeSideCode,
        "tradeSideCodes": tradeSideCodes,
        "tradeTypes": tradeTypes,
        "tradeTimeRange": tradeTimeRange,
        "tradeConsolidationTypes": tradeConsolidationTypes,
        "isEtf": isEtf,
        "isIndex": isIndex,
        "isOpeningPosition": isOpeningPosition,
        "isUnusual": isUnusual,
        "isVolumeGreaterThanOpenInterest": isVolumeGreaterThanOpenInterest,
        "isCancelled": isCancelled,
        "isComplex": isComplex,
        "isComplexToComplex": isComplexToComplex,
        "isElectronicCross": isElectronicCross,
        "isFloor": isFloor,
        "isLegging": isLegging,
        "isPriceImprovement": isPriceImprovement,
        "isSimpleToSimple": isSimpleToSimple,
        "isTied": isTied,
        "isGoldenSweep": isGoldenSweep,
        "deltaRange": deltaRange,
        "gammaRange": gammaRange,
        "thetaRange": thetaRange,
        "vegaRange": vegaRange,
        "rhoRange": rhoRange,
        "charmRange": charmRange,
        "colorRange": colorRange,
        "speedRange": speedRange,
        "vannaRange": vannaRange,
        "vommaRange": vommaRange,
        "vetaRange": vetaRange,
        "omegaRange": omegaRange,
        "sigmaRange": sigmaRange,
        "ultimaRange": ultimaRange,
        "zommaRange": zommaRange,
    })

OPTION_TRADE_FILTER_NAMES = tuple(option_trade_filters.__kwdefaults__ or {})

def add_filter_expression(
    params: JsonObject,
    filterExpression: Mapping[str, Any] | None = None,
) -> None:
    if filterExpression is not None:
        params["filterExpression"] = dict(filterExpression)


def add_session_or_time_range(
    params: JsonObject,
    *,
    sessionDate: date | datetime | str | None = None,
    startTime: datetime | str | None = None,
    endTime: datetime | str | None = None,
) -> None:
    has_time = startTime is not None or endTime is not None
    if sessionDate is not None and has_time:
        raise ValueError("sessionDate and timeRange are mutually exclusive.")
    if (startTime is None) != (endTime is None):
        raise ValueError("startTime and endTime must both be provided together.")
    if startTime is not None and endTime is not None:
        if isinstance(startTime, datetime) and isinstance(endTime, datetime):
            if endTime <= startTime:
                raise ValueError("endTime must be after startTime.")
        params["timeRange"] = {
            "startTime": to_quantdata_utc_instant(startTime),
            "endTime": to_quantdata_utc_instant(endTime),
        }
    elif sessionDate is not None:
        params["sessionDate"] = to_quantdata_date(sessionDate)


def add_session_or_snapshot(
    params: JsonObject,
    *,
    sessionDate: date | datetime | str | None = None,
    snapshotTime: datetime | str | None = None,
) -> None:
    if sessionDate is not None and snapshotTime is not None:
        raise ValueError("sessionDate and snapshotTime are mutually exclusive.")
    if snapshotTime is not None:
        params["snapshotTime"] = to_quantdata_utc_instant(snapshotTime)
    elif sessionDate is not None:
        params["sessionDate"] = to_quantdata_date(sessionDate)


def add_session(
    params: JsonObject,
    sessionDate: date | datetime | str | None = None,
) -> None:
    if sessionDate is not None:
        params["sessionDate"] = to_quantdata_date(sessionDate)


def add_session_date_range(
    params: JsonObject,
    *,
    startDate: date | datetime | str,
    endDate: date | datetime | str | None = None,
) -> None:
    value = {"startDate": to_quantdata_date(startDate)}
    if endDate is not None:
        value["endDate"] = to_quantdata_date(endDate)
    params["sessionDateRange"] = value


def add_aggregation(
    params: JsonObject,
    aggregationPeriod: str | None = None,
) -> None:
    if aggregationPeriod is not None:
        params["aggregationPeriod"] = aggregationPeriod


def add_pagination(
    params: JsonObject,
    *,
    size: int | None = None,
    searchAfter: Sequence[Any] | None = None,
    sortField: str | None = None,
    sortDirection: str | None = None,
    max_size: int = 100,
) -> None:
    if size is not None:
        if not 1 <= int(size) <= max_size:
            raise ValueError(f"size must be between 1 and {max_size}.")
        params["size"] = int(size)
    if searchAfter is not None:
        params["searchAfter"] = list(searchAfter)
    if sortField is not None or sortDirection is not None:
        if sortField is None or sortDirection is None:
            raise ValueError("sortField and sortDirection must be provided together.")
        params["sort"] = {
            "field": sortField,
            "direction": validate_enum("sortDirection", sortDirection, SORT_DIRECTIONS),
        }

def add_projection(
    params: JsonObject,
    *,
    includes: Sequence[str] | None = None,
    excludes: Sequence[str] | None = None,
) -> None:
    if includes is not None and excludes is not None:
        raise ValueError("includes and excludes are mutually exclusive.")
    if includes is not None:
        params["includes"] = list(includes)
    if excludes is not None:
        params["excludes"] = list(excludes)