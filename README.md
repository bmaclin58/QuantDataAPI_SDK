# QuantData.US Python SDK (Unofficial)

Unofficial Python client for the [QuantData.US API](https://quantdata.us/api).

> 🔑 **[API key at QuantData.us →](https://quantdata.us/api#pricing)** · 📚 [API documentation](https://quantdata.us/api/docs/introduction) ·

> **Work in progress:** This SDK is under active development. Endpoint interfaces and examples may change. Endpoint example blocks are intentionally empty until the interfaces are finalized.

```bash
pip install quantdataus-api
```

## Quick Start

```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client(
    "YOUR_API_KEY",
    output_type="Polars",
    timezone="America/New_York",
)

data = client.get_dark_pool_levels(
    ticker="AAPL",
    startDate="2026-07-05",
)
```

### Timezone handling

`timezone` accepts an [IANA timezone name](https://nodatime.org/TimeZones) and defaults to `America/New_York`. The
SDK uses it to interpret naive input datetimes before converting them to UTC timestamps for API requests. It will
convert the timestamps in response payloads unless `convertTimezone = False`.

## Equity Features

### [Dark Flow](https://quantdata.us/api/docs/endpoints/dark-flow)

Dark Flow returns off-exchange (dark pool) trading activity for one ticker, bucketed over time. Each bucket carries `notionalValue`, `size` (share count), `tradeCount`, and the underlying `stockPrice`. Use it to track dark-venue accumulation or distribution as the session unfolds.
```python

```

### [Dark Pool Levels](https://quantdata.us/api/docs/endpoints/dark-pool-levels)

Dark Pool Levels returns off-exchange print activity for one ticker, aggregated by price level over a date range. Each level carries the total notional, share count, and trade count of dark-venue prints at that price.
```python
from QuantDataAPI import QuantDataAPI_Client

client = QuantDataAPI_Client("YOUR_API_KEY", output_type="Polars")

levels = client.get_dark_pool_levels(
    ticker="AAPL",
    startDate="2026-07-05",
)
```

Pandas and Polars output contains `priceLevel`, `notionalValue`, `size`, `tradeCount`, and
`latestStockPrice`. When `endDate` is omitted, QuantData returns sessions from `startDate` through today.

### [Equity Prints](https://quantdata.us/api/docs/endpoints/equity-prints)

Equity Prints returns the trade-by-trade equity tape across both lit and dark venues. Each row is one print. Rows are paginated with cursor semantics, and every projectable field is returned by default. Use this when you need per-print visibility into how an equity is trading; for aggregated dark-venue activity over time, see Dark Flow.
```python

```

### [Exchange Notifications](https://quantdata.us/api/docs/endpoints/exchange-notifications)

Exchange Notifications returns paginated trade-halt, IPO, regulatory-event, and circuit-breaker notification records over a session or custom time window.
```python

```

### [Market Map](https://quantdata.us/api/docs/endpoints/market-map)

Market Map returns a market-wide snapshot of every supported ticker with its current and previous session prices, company name, sector, industry, and market capitalization. Suited for treemap-style visualizations of the whole equity universe in one request.
```python

```

### [Stock Price Over Time](https://quantdata.us/api/docs/endpoints/stock-price-over-time)

Stock Price Over Time returns OHLC bars for the underlying equity, bucketed over time. Each bucket carries `openPrice`, `highPrice`, `lowPrice`, and `closePrice`. There is no volume field on this endpoint.
```python

```

## Options Endpoints

### [Contract Statistics](https://quantdata.us/api/docs/endpoints/contract-statistics)

Contract Statistics returns a call vs put rollup of total premium, trade count, and contract volume for the requested window. Two entries in the response: one keyed by `CALL`, one by `PUT`. Contract types with no matching trades are omitted.
```python

```

### [Contract Trade Side Statistics](https://quantdata.us/api/docs/endpoints/contract-trade-side-statistics)

Contract Trade Side Statistics returns one aggregate per (contract type, trade side) cell. The metric in each cell is selected by `dataMode`: `PREMIUM`, `TRADE_COUNT`, or `VOLUME`. Trade-side keys on the wire are `ABOVE_ASK`, `ASK`, `MID_MARKET`, `BID`, `BELOW_BID`; the short codes `AA`, `A`, `M`, `B`, `BB` are accepted as input aliases on filters but never appear in responses.
```python

```

### [Exposure By Expiration](https://quantdata.us/api/docs/endpoints/exposure-by-expiration)

Exposure By Expiration returns Greek-weighted exposure rolled up by expiration date for one ticker at a snapshot in time. The response shape matches Exposure By Strike; the two endpoints differ in the underlying aggregation strategy, not the wire contract.
```python

```

### [Exposure By Strike](https://quantdata.us/api/docs/endpoints/exposure-by-strike)

Exposure By Strike returns Greek-weighted exposure aggregated by expiration and strike for one ticker at a snapshot in time. Each cell carries `callExposure` and `putExposure` in the units implied by `greekMode` and `representationMode`.
```python

```

### [Gainers / Losers](https://quantdata.us/api/docs/endpoints/gainers-losers)

Gainers / Losers returns one entry per ticker for the requested window, summarizing call vs put premium and trade activity. Each entry carries `bullishPremium`, `bearishPremium`, total `premium`, `premiumRatio` (bearish over bullish), `tradeCount`, and `volume`.
```python

```

### [Heat Map](https://quantdata.us/api/docs/endpoints/heat-map)

Heat Map returns an expiration by strike grid for one ticker at a snapshot in time. The metric in each cell is selected by `dataMode`. The response is polymorphic: net / aggregate modes return one value per leg per cell; per-leg modes return a single value per cell. A top-level `type` field advertises which shape was returned.
```python

```

### [Interval Map](https://quantdata.us/api/docs/endpoints/interval-map)

Interval Map returns Greek-weighted exposure for one ticker, bucketed over time. Each bucket is a nested grid: expiration date `->` strike (dollars) `->` contract type (`CALL` / `PUT`) `->` exposure aggregate. Use it to watch how positioning shifts across the chain as the session unfolds.
```python

```

### [IV Rank](https://quantdata.us/api/docs/endpoints/iv-rank)

IV Rank returns per-session-date implied-volatility context for one ticker, looking back over a window you control. For each session, the response gives the last IV, the window min, and the window max for both call and put legs. Compute rank as `(lastIv - windowMinIv) / (windowMaxIv - windowMinIv)` for the leg of interest.
```python

```

### [Market Share](https://quantdata.us/api/docs/endpoints/market-share)

Market Share returns one entry per exchange, summarizing options activity in three buckets: equity calls, equity puts, and index. For each bucket the response carries premium, trade count, and contract volume. Exchanges with no matching trades are omitted.
```python

```

### [Max Pain](https://quantdata.us/api/docs/endpoints/max-pain)

Max Pain returns the per-strike call and put intrinsic-value grid for a single ticker and expiration on one trading session, plus the strike that maximizes total writer-side intrinsic value (the max-pain strike) and the underlying stock price.
```python

```

### [Max Pain Over Time](https://quantdata.us/api/docs/endpoints/max-pain-over-time)

Max Pain Over Time returns the max-pain strike for each option expiration on a single trading session. The "over time" dimension is expiration date, not intra-session time: you get one max-pain strike per expiration in the chain.
```python

```

### [Net Drift](https://quantdata.us/api/docs/endpoints/net-drift)

Net Drift returns call vs put premium for a slice of the options chain, bucketed over time. Each bucket summarizes the trades that landed in that window: `netCallPremium`, `netCallVolume`, `netPutPremium`, `netPutVolume`, and the mid-market premium for both legs. When the filter narrows to a single ticker the response also includes the underlying `stockPrice` per bucket.
```python

```

### [Net Flow](https://quantdata.us/api/docs/endpoints/net-flow)

Net Flow returns aggregated call and put magnitude for a slice of the options chain, bucketed over time. The metric is selected by `dataMode`: `NET_PREMIUM` (cents) or `NET_VOLUME` (contracts). Each bucket carries `callSum`, `putSum`, and the underlying `stockPrice` when the request narrows to a single ticker.
```python

```

### [Open Interest By Expiration](https://quantdata.us/api/docs/endpoints/open-interest-by-expiration)

Open Interest By Expiration returns the per-expiration call and put open-interest snapshot for one ticker on a single trading session.
```python

```

### [Open Interest By Strike](https://quantdata.us/api/docs/endpoints/open-interest-by-strike)

Open Interest By Strike returns the per-strike call and put open-interest snapshot for one ticker on a single trading session.
```python

```

### [Open Interest Change](https://quantdata.us/api/docs/endpoints/open-interest-change)

Open Interest Change returns a paginated, sortable, projectable table of per-contract daily open-interest delta records for a single trading session. Each row carries previous OI, current OI, the signed delta, and the fractional percent change.
```python

```

### [Open Interest Over Time](https://quantdata.us/api/docs/endpoints/open-interest-over-time)

Open Interest Over Time returns the per-session call and put open-interest series for one ticker across every trading session with available data. There is no time-selection field on the request: the response inherently spans the full available history.
```python

```

### [Option Price Over Time](https://quantdata.us/api/docs/endpoints/option-price-over-time)

Option Price Over Time returns OHLC and volume bars for a single options contract, bucketed over time. Each bucket carries `openPrice`, `highPrice`, `lowPrice`, `closePrice`, and `volume`.
```python

```

### [Order Flow Consolidated](https://quantdata.us/api/docs/endpoints/order-flow-consolidated)

Order Flow Consolidated returns per-row consolidated option trades: blocks, splits, sweeps, and (when requested) their comprising trades. Rows are paginated with cursor semantics, and every projectable field is returned by default. Use this when you want per-trade visibility into how the tape is grouped.
```python

```

### [Order Flow Unconsolidated](https://quantdata.us/api/docs/endpoints/order-flow-unconsolidated)

Order Flow Unconsolidated returns the raw, trade-by-trade option tape with no consolidation. Each row is one print. Rows are paginated with cursor semantics, and every projectable field is returned by default. Use this when you need per-print visibility instead of grouped blocks / sweeps.
```python

```

### [Term Structure](https://quantdata.us/api/docs/endpoints/term-structure)

Term Structure returns delta, implied volatility, and moneyness for one ticker at a snapshot in time. The response walks expiration date `->` strike (dollars) `->` contract type, so you can index any cell by `(expiration, strike, CALL | PUT)`.
```python

```

### [Volatility Drift](https://quantdata.us/api/docs/endpoints/volatility-drift)

Volatility Drift returns realized and at-the-money implied volatility for one ticker, in fixed 1-minute buckets across a single trading session. Each bucket carries `arv` (adjusted realized volatility), `iv` (implied volatility from the nearest ATM trade), and the underlying `stockPrice`. Both `arv` and `iv` are fractional, where `0.25` means 25%.
```python

```

### [Volatility Skew](https://quantdata.us/api/docs/endpoints/volatility-skew)

Volatility Skew returns the implied-volatility surface for one ticker at a snapshot in time. The response walks expiration date `->` strike (dollars) `->`contract type, where the leaf is the contract's fractional implied volatility.
```python

```

## News

### [News Articles](https://quantdata.us/api/docs/endpoints/news-articles)

News Articles returns a paginated, cursor-pageable list of news articles tagged with tickers, topics, and per-ticker sentiment. The article body is opt-in via `includeBody: true` so default responses stay light.
```python

```
