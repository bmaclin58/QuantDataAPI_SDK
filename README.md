# QuantData.US Python SDK (Unofficial)

Unofficial Python client for the [QuantData.US API](https://quantdata.us/api).

> [Get an API key](https://quantdata.us/api#pricing) · [API documentation](https://quantdata.us/api/docs/introduction)

```bash
pip install quantdataus-api
```

## Quick Start

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client(
    "YOUR_API_KEY",
    output_type="polars",
    timezone="America/New_York",
)

data = client.get_dark_pool_levels(
    ticker="AAPL",
    startDate="2026-07-05",
)
```

`output_type` accepts `"json"` (the default), `"pandas"`, or `"polars"`. Non-paginated endpoints return the service JSON unchanged in JSON mode and normalized rows with the documented columns in DataFrame modes. The six cursor-paginated endpoints support JSON only and return exactly one page per call.

### Request and timezone rules

`timezone` accepts an [IANA timezone name](https://nodatime.org/TimeZones) and defaults to `America/New_York`. The SDK interprets naive input datetimes in that timezone, sends UTC instants, and converts response timestamps back to that timezone unless `convertTimezone=False`. DataFrame outputs whose schema contains `timestamp` retain the raw Unix-millisecond value and add an adjacent, timezone-aware `ConvertedDateTime` column using the native pandas or Polars datetime type; that column uses the configured timezone when conversion is enabled and UTC when it is disabled. Datetime inputs accept the human-readable `YYYY-MM-DD HH:MM` format; for example, `2026-05-13 20:00` means 8 PM in the configured timezone. ISO-8601 strings and Python `datetime` values are also supported.

Where supported, `sessionDate` and the `startTime`/`endTime` pair are mutually exclusive. Both time bounds are required together. Session or snapshot selectors are optional unless an endpoint says otherwise; omitting them asks QuantData for its latest available session or snapshot.

## Equity Features

### [Dark Flow](https://quantdata.us/api/docs/endpoints/dark-flow)

Dark Flow returns off-exchange activity for one ticker, bucketed over time.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
dark_flow = client.get_dark_flow(
    "AAPL",
    sessionDate="2026-05-13",
    aggregationPeriod="5m",
)
```

DataFrame columns: `timestamp`, `ConvertedDateTime`, `notionalValue`, `size`, `stockPrice`, `tradeCount`.

### [Dark Pool Levels](https://quantdata.us/api/docs/endpoints/dark-pool-levels)

Dark Pool Levels aggregates off-exchange prints by price level over a date range.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
levels = client.get_dark_pool_levels(
    ticker="AAPL",
    startDate="2026-07-05",
)
```

DataFrame columns: `priceLevel`, `notionalValue`, `size`, `tradeCount`, `latestStockPrice`. When `endDate` is omitted, the request covers `startDate` through today.

### [Equity Prints](https://quantdata.us/api/docs/endpoints/equity-prints)

Equity Prints returns the trade-by-trade equity tape across lit and dark venues.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="json")
first_page = client.get_equity_prints(
    sessionDate="2026-05-13",
    tickers=["AAPL"],
    size=100,
    sortField="tradeTime",
    sortDirection="DESCENDING",
)

cursor = first_page.get("nextSearchAfter")
if cursor is not None:
    second_page = client.get_equity_prints(
        sessionDate="2026-05-13",       # keep the query unchanged
        tickers=["AAPL"],
        size=100,
        sortField="tradeTime",
        sortDirection="DESCENDING",
        searchAfter=cursor,              # cursor from the first page
    )
```

**JSON only**: returns one page with `data` and optional `nextSearchAfter`. Pass that cursor as `searchAfter` in a new call to fetch the next page. Page size is 1–100.

### [Exchange Notifications](https://quantdata.us/api/docs/endpoints/exchange-notifications)

Exchange Notifications returns trade-halt, IPO, regulatory-event, and circuit-breaker records.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="json")
page = client.get_exchange_notifications(
    sessionDate="2026-05-13",
    tickers=["AAPL"],
    types=["LUDP"],
    size=50,
)
```

**JSON only**: returns one page with `data` and optional `nextSearchAfter`. Pass that cursor as `searchAfter` in a new call to fetch the next page. Page size is 1–100.

### [Market Map](https://quantdata.us/api/docs/endpoints/market-map)

Market Map returns a market-wide ticker snapshot for treemap-style analysis.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="pandas")
market = client.get_market_map(
    sessionDate="2026-05-13",
    sectors=["Technology"],
)
```

DataFrame columns: `ticker`, `companyName`, `currentValue`, `industry`, `previousValue`, `sector`, `size`.

### [Stock Price Over Time](https://quantdata.us/api/docs/endpoints/stock-price-over-time)

Stock Price Over Time returns underlying-equity OHLC bars; this endpoint has no volume field.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
bars = client.get_stock_price_over_time(
    "AAPL",
    sessionDate="2026-05-13",
    aggregationPeriod="5m",
)
```

DataFrame columns: `timestamp`, `ConvertedDateTime`, `openPrice`, `highPrice`, `lowPrice`, `closePrice`.

## Options Endpoints

### [Contract Statistics](https://quantdata.us/api/docs/endpoints/contract-statistics)

Contract Statistics returns call-versus-put premium, trade-count, and volume totals.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
statistics = client.get_contract_statistics(
    sessionDate="2026-05-13",
    ticker="AAPL",
)
```

DataFrame columns: `contractType`, `premium`, `tradeCount`, `volume`.

### [Contract Trade Side Statistics](https://quantdata.us/api/docs/endpoints/contract-trade-side-statistics)

Contract Trade Side Statistics returns one selected metric per contract-type/trade-side cell.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="pandas")
statistics = client.get_contract_trade_side_statistics(
    dataMode= "PREMIUM",
    sessionDate="2026-05-13",
    ticker="AAPL",
)
```

DataFrame columns: `contractType`, `tradeSide`, `dataMode`, `value`. `dataMode` accepts `PREMIUM`, `TRADE_COUNT`, or `VOLUME`.

### [Exposure By Expiration](https://quantdata.us/api/docs/endpoints/exposure-by-expiration)

Exposure By Expiration returns Greek-weighted exposure for one ticker at a session or snapshot.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
exposure = client.get_exposure_by_expiration(
    ticker = "AAPL",
    greekMode= "DELTA",
    representationMode= "RAW",
    sessionDate="2026-05-13",
)
```

DataFrame columns: `ticker`, `expirationDate`, `strikePrice`, `callExposure`, `putExposure`, `stockPrice`.

### [Exposure By Strike](https://quantdata.us/api/docs/endpoints/exposure-by-strike)

Exposure By Strike returns Greek-weighted exposure aggregated by expiration and strike.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
exposure = client.get_exposure_by_strike(
    ticker = "AAPL",
    greekMode= "DELTA",
    representationMode= "RAW",
    sessionDate="2026-05-13",
    expirationDate="2026-05-16",
)
```

DataFrame columns: `ticker`, `expirationDate`, `strikePrice`, `callExposure`, `putExposure`, `stockPrice`.

### [Gainers / Losers](https://quantdata.us/api/docs/endpoints/gainers-losers)

Gainers / Losers summarizes bullish and bearish options activity by ticker.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="pandas")
movers = client.get_gainers_losers(
    sessionDate="2026-05-13",
    tickers=["AAPL", "NVDA"],
)
```

DataFrame columns: `ticker`, `bearishPremium`, `bullishPremium`, `premium`, `premiumRatio`, `tradeCount`, `volume`.

### [Heat Map](https://quantdata.us/api/docs/endpoints/heat-map)

Heat Map returns an expiration-by-strike grid whose shape depends on `dataMode`.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
heat_map = client.get_heat_map(
    "AAPL",
    "NET_DELTA_EXPOSURE",
    sessionDate="2026-05-13",
)
```

DataFrame columns: contract-shaped modes use `type`, `expirationDate`, `strikePrice`, `callValue`, `putValue`; single-leg modes use `type`, `expirationDate`, `strikePrice`, `value`. The top-level response `type` selects the schema.

### [Interval Map](https://quantdata.us/api/docs/endpoints/interval-map)

Interval Map returns Greek exposure by time bucket, expiration, strike, and contract type.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
intervals = client.get_interval_map(
    "SPY",
    "GAMMA",
    sessionDate="2026-05-13",
    aggregationPeriod="5m",
)
```

DataFrame columns: `timestamp`, `ConvertedDateTime`, `expirationDate`, `strikePrice`, `contractType`, `exposure`.

### [IV Rank](https://quantdata.us/api/docs/endpoints/iv-rank)

IV Rank returns per-session implied-volatility context over a requested lookback and maturity.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="pandas")
iv_context = client.get_iv_rank(
    "AAPL",
    lookBackPeriod=252,
    maturity=30,
    contractTypes=["CALL", "PUT"],
)
```

DataFrame columns: `sessionDate`, `contractType`, `lastIv`, `windowMinIv`, `windowMaxIv`, `expirationDate`, `stockPrice`.

### [Market Share](https://quantdata.us/api/docs/endpoints/market-share)

Market Share summarizes equity-call, equity-put, and index options activity by exchange.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
share = client.get_market_share(
    sessionDate="2026-05-13",
    tickers=["AAPL"],
)
```

DataFrame columns: `exchange`, `equityCallPremium`, `equityCallTradeCount`, `equityCallVolume`, `equityPutPremium`, `equityPutTradeCount`, `equityPutVolume`, `indexPremium`, `indexTradeCount`, `indexVolume`.

### [Max Pain](https://quantdata.us/api/docs/endpoints/max-pain)

Max Pain returns intrinsic values by strike plus the max-pain strike and stock price.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="pandas")
max_pain = client.get_max_pain(
    "AAPL",
    "2026-05-16",
    sessionDate="2026-05-13",
)
```

DataFrame columns: `strikePrice`, `callIntrinsicValue`, `putIntrinsicValue`, `maxPainStrikePrice`, `stockPrice`.

### [Max Pain Over Time](https://quantdata.us/api/docs/endpoints/max-pain-over-time)

Max Pain Over Time returns one max-pain strike per expiration for a session.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
series = client.get_max_pain_over_time(
    "AAPL",
    sessionDate="2026-05-13",
)
```

DataFrame columns: `expirationDate`, `maxPainStrikePrice`.

### [Net Drift](https://quantdata.us/api/docs/endpoints/net-drift)

Net Drift returns call-versus-put premium and volume measures bucketed over time.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
drift = client.get_net_drift(
    sessionDate="2026-05-13",
    aggregationPeriod="5m",
    ticker="AAPL",
)
```

DataFrame columns: `timestamp`, `ConvertedDateTime`, `midMarketCallPremium`, `midMarketPutPremium`, `netCallPremium`, `netCallVolume`, `netPutPremium`, `netPutVolume`, `stockPrice`.

### [Net Flow](https://quantdata.us/api/docs/endpoints/net-flow)

Net Flow returns the selected call and put magnitude bucketed over time.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="pandas")
flow = client.get_net_flow(
    "NET_PREMIUM",
    sessionDate="2026-05-13",
    aggregationPeriod="5m",
    ticker="AAPL",
)
```

DataFrame columns: `timestamp`, `ConvertedDateTime`, `callSum`, `putSum`, `stockPrice`. `dataMode` accepts `NET_PREMIUM` or `NET_VOLUME`.

### [Open Interest By Expiration](https://quantdata.us/api/docs/endpoints/open-interest-by-expiration)

Open Interest By Expiration returns call and put open interest for each expiration.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
open_interest = client.get_open_interest_by_expiration(
    "AAPL",
    sessionDate="2026-05-13",
)
```

DataFrame columns: `expirationDate`, `callOpenInterest`, `putOpenInterest`.

### [Open Interest By Strike](https://quantdata.us/api/docs/endpoints/open-interest-by-strike)

Open Interest By Strike returns call and put open interest for each strike.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
open_interest = client.get_open_interest_by_strike(
    "AAPL",
    sessionDate="2026-05-13",
    expirationDate="2026-05-16",
)
```

DataFrame columns: `strikePrice`, `callOpenInterest`, `putOpenInterest`.

### [Open Interest Change](https://quantdata.us/api/docs/endpoints/open-interest-change)

Open Interest Change returns per-contract daily open-interest deltas for one session.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="json")
page = client.get_open_interest_change(
    sessionDate="2026-05-13",
    tickers=["AAPL"],
    size=100,
    sortField="changeInOpenInterest",
    sortDirection="DESCENDING",
)
```

**JSON only**: returns one page with `data` and optional `nextSearchAfter`. Pass that cursor as `searchAfter` in a new call to fetch the next page. Page size is 1–100.

### [Open Interest Over Time](https://quantdata.us/api/docs/endpoints/open-interest-over-time)

Open Interest Over Time returns the full available per-session open-interest history; it has no time selector.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="pandas")
history = client.get_open_interest_over_time(
    "AAPL",
    expirationDate="2026-05-16",
    strikePrice=220.0,
)
```

DataFrame columns: `sessionDate`, `callOpenInterest`, `putOpenInterest`.

### [Option Price Over Time](https://quantdata.us/api/docs/endpoints/option-price-over-time)

Option Price Over Time returns OHLCV bars for one option contract.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
bars = client.get_option_price_over_time(
    osi="AAPL260516C00220000",
    sessionDate="2026-05-13",
    aggregationPeriod="5m",
)
```

DataFrame columns: `timestamp`, `ConvertedDateTime`, `openPrice`, `highPrice`, `lowPrice`, `closePrice`, `volume`. Identify the contract with `osi`, or provide the complete `ticker` + `expirationDate` + `strikePrice` + `contractType` set; the two selector forms are mutually exclusive.

### [Order Flow Consolidated](https://quantdata.us/api/docs/endpoints/order-flow-consolidated)

Order Flow Consolidated returns blocks, splits, sweeps, and optionally their comprising trades.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="json")
page = client.get_order_flow_consolidated(
    sessionDate="2026-05-13",
    ticker="AAPL",
    tradeConsolidationTypes=["SWEEP"],
    includeComprisingTrades=True,
    includeStatistics=True,
    size=100,
)
```

**JSON only**: returns one page with `data`, optional first-page `statistics`, and optional `nextSearchAfter`. Pass that cursor as `searchAfter` in a new call to fetch the next page. Page size is 1–100.

The SDK returns one page per call. To collect every matching row, keep the request unchanged, pass each `nextSearchAfter` value back as `searchAfter`, and stop only when the cursor is `None`:

```python
request = {
    "sessionDate": "2026-05-13",
    "ticker": "AAPL",
    "expirationDate": "2026-05-13",
    "sentimentTypes": ["BEARISH"],
}
all_rows = []
search_after = None

while True:
    page = client.get_order_flow_consolidated(
        **request,
        size=100,
        searchAfter=search_after,
    )
    all_rows.extend(page["data"])
    search_after = page.get("nextSearchAfter")
    if search_after is None:
        break
```

### [Order Flow Unconsolidated](https://quantdata.us/api/docs/endpoints/order-flow-unconsolidated)

Order Flow Unconsolidated returns the raw option tape, one row per print.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="json")
page = client.get_order_flow_unconsolidated(
    sessionDate="2026-05-13",
    osi="AAPL260516C00220000",
    includeStatistics=True,
    size=1000,
)
```

**JSON only**: returns one page with `data`, optional first-page `statistics`, and optional `nextSearchAfter`. Pass that cursor as `searchAfter` in a new call to fetch the next page. Page size is 1–1000. Consolidated-only filters such as `isGoldenSweep` and `tradeConsolidationTypes` are rejected.

### [Term Structure](https://quantdata.us/api/docs/endpoints/term-structure)

Term Structure returns delta, implied volatility, and moneyness by expiration, strike, and contract type.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
term_structure = client.get_term_structure(
    "AAPL",
    sessionDate="2026-05-13",
    moneyTypes=["OTM"],
)
```

DataFrame columns: `expirationDate`, `strikePrice`, `contractType`, `delta`, `iv`, `moneyType`, `stockPrice`.

### [Volatility Drift](https://quantdata.us/api/docs/endpoints/volatility-drift)

Volatility Drift returns 1-minute realized and at-the-money implied volatility for one session.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="pandas")
volatility = client.get_volatility_drift(
    "AAPL",
    sessionDate="2026-05-13",
)
```

DataFrame columns: `timestamp`, `ConvertedDateTime`, `arv`, `iv`, `stockPrice`.

### [Volatility Skew](https://quantdata.us/api/docs/endpoints/volatility-skew)

Volatility Skew returns implied volatility by expiration, strike, and contract type.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="polars")
skew = client.get_volatility_skew(
    "AAPL",
    sessionDate="2026-05-13",
    contractTypes=["CALL", "PUT"],
)
```

DataFrame columns: `expirationDate`, `strikePrice`, `contractType`, `impliedVolatility`, `stockPrice`.

## News

### [News Articles](https://quantdata.us/api/docs/endpoints/news-articles)

News Articles returns articles tagged with topics, tickers, and per-ticker sentiment.

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="json")
page = client.get_news_articles(
    startTime="2026-05-13 09:30",
    endTime="2026-05-13 20:00",
    tickers=["AAPL", "NVDA"],
    topics=["EARNINGS_BEATS"],
    includeBody=True,
    size=50,
)
```

**JSON only**: returns one page with `data` and optional `nextSearchAfter`. Pass that cursor as `searchAfter` in a new call to fetch the next page. Page size is 1–100; results are always ordered by `publishedTime` descending and no sort field is accepted.
