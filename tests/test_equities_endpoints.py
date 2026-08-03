from datetime import date, datetime
import unittest
from zoneinfo import ZoneInfo

import pandas as pd
import polars as pl

from QuantDataAPI.errors import QuantDataClientError
from tests.endpoint_test_support import client_with_payload


DARK_FLOW_PAYLOAD = {
    "data": {
        "1747137900000": {
            "notionalValue": 22_104_550.90,
            "size": 103_441,
            "stockPrice": 213.78,
            "tradeCount": 218,
        },
        "1747137600000": {
            "notionalValue": 14_821_330.50,
            "size": 69_428,
            "stockPrice": 213.45,
            "tradeCount": 142,
        },
    }
}

MARKET_MAP_PAYLOAD = {
    "data": {
        "NVDA": {
            "companyName": "NVIDIA Corporation",
            "currentValue": 920.15,
            "industry": "Semiconductors",
            "previousValue": 908.42,
            "sector": "Technology",
            "size": 2_260_000_000_000.0,
        },
        "AAPL": {
            "companyName": "Apple Inc.",
            "currentValue": 218.42,
            "industry": "Consumer Electronics",
            "previousValue": 216.18,
            "sector": "Technology",
            "size": 3_320_000_000_000.0,
        },
    }
}

STOCK_PRICE_PAYLOAD = {
    "data": {
        "1747137900000": {
            "openPrice": 213.65,
            "highPrice": 214.04,
            "lowPrice": 213.50,
            "closePrice": 213.92,
        },
        "1747137600000": {
            "openPrice": 213.42,
            "highPrice": 213.81,
            "lowPrice": 213.10,
            "closePrice": 213.65,
        },
    }
}

EQUITY_PRINTS_PAYLOAD = {
    "data": [{"id": "5e0f1a2b", "ticker": "AAPL", "tradeTime": 1747137612000}],
    "nextSearchAfter": ["1747137612000", "5e0f1a2b"],
}

EXCHANGE_NOTIFICATIONS_PAYLOAD = {
    "data": [
        {"id": "9c2a4f08", "ticker": "AAPL", "type": "LUDP", "createdTime": 1747137612000}
    ],
    "nextSearchAfter": ["1747137612000", "9c2a4f08"],
}


class DarkFlowTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(DARK_FLOW_PAYLOAD)

        result = client.get_dark_flow(" AAPL ", sessionDate=date(2026, 5, 13))

        self.assertEqual(result, DARK_FLOW_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/equities/tool/dark-flow",
            json={
                "sessionDate": "2026-05-13",
                "filter": {"ticker": "AAPL"},
            },
            timeout=30,
        )

    def test_returns_typed_dataframes_in_timestamp_order(self):
        expected_columns = [
            "timestamp",
            "ConvertedDateTime",
            "notionalValue",
            "size",
            "stockPrice",
            "tradeCount",
        ]
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    DARK_FLOW_PAYLOAD,
                    output_type=output_type,
                )

                frame = client.get_dark_flow("AAPL")

                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), expected_columns)
                self.assertEqual(
                    frame["timestamp"].to_list(),
                    [1747137600000, 1747137900000],
                )
                self.assertTrue(str(frame["size"].dtype).lower().endswith("64"))

    def test_returns_typed_empty_dataframe(self):
        client = client_with_payload({"data": {}}, output_type="polars")

        frame = client.get_dark_flow("AAPL")

        self.assertEqual(frame.shape, (0, 6))
        self.assertEqual(frame.schema["timestamp"], pl.Int64)
        self.assertEqual(
            frame.schema["ConvertedDateTime"],
            pl.Datetime("us", "America/New_York"),
        )
        self.assertEqual(frame.schema["notionalValue"], pl.Float64)

    def test_rejects_blank_ticker_before_transport(self):
        client = client_with_payload(DARK_FLOW_PAYLOAD)

        with self.assertRaisesRegex((TypeError, ValueError), "ticker"):
            client.get_dark_flow(" ")

        client._session.post.assert_not_called()

    def test_rejects_malformed_success_payload(self):
        malformed_payloads = (
            {},
            {"data": []},
            {"data": {"1747137600000": {"notionalValue": 1.0}}},
            {
                "data": {
                    "1747137600000": {
                        "notionalValue": 1.0,
                        "size": 1.5,
                        "stockPrice": 2.0,
                        "tradeCount": 1,
                    }
                }
            },
        )
        for payload in malformed_payloads:
            with self.subTest(payload=payload):
                client = client_with_payload(payload)
                with self.assertRaisesRegex(QuantDataClientError, "dark flow response"):
                    client.get_dark_flow("AAPL")


class MarketMapTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(MARKET_MAP_PAYLOAD)

        result = client.get_market_map(
            snapshotTime="2026-05-13T16:30:00Z",
            sectors=["TECHNOLOGY"],
        )

        self.assertEqual(result, MARKET_MAP_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/equities/tool/market-map",
            json={
                "snapshotTime": "2026-05-13T16:30:00Z",
                "filter": {"sectors": ["TECHNOLOGY"]},
            },
            timeout=30,
        )

    def test_returns_ticker_sorted_typed_dataframes(self):
        expected_columns = [
            "ticker",
            "companyName",
            "currentValue",
            "industry",
            "previousValue",
            "sector",
            "size",
        ]
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    MARKET_MAP_PAYLOAD,
                    output_type=output_type,
                )

                frame = client.get_market_map()

                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), expected_columns)
                self.assertEqual(frame["ticker"].to_list(), ["AAPL", "NVDA"])

    def test_returns_typed_empty_dataframe(self):
        client = client_with_payload({"data": {}}, output_type="polars")

        frame = client.get_market_map()

        self.assertEqual(frame.shape, (0, 7))
        self.assertEqual(frame.schema["ticker"], pl.String)
        self.assertEqual(frame.schema["currentValue"], pl.Float64)

    def test_rejects_mutually_exclusive_snapshot_selectors(self):
        client = client_with_payload(MARKET_MAP_PAYLOAD)

        with self.assertRaisesRegex(ValueError, "mutually exclusive"):
            client.get_market_map(
                sessionDate="2026-05-13",
                snapshotTime="2026-05-13T16:30:00Z",
            )

        client._session.post.assert_not_called()

    def test_rejects_malformed_success_payload(self):
        malformed_payloads = (
            {},
            {"data": []},
            {"data": {"AAPL": {"companyName": "Apple Inc."}}},
            {
                "data": {
                    "AAPL": {
                        "companyName": "Apple Inc.",
                        "currentValue": 218.42,
                        "industry": "Consumer Electronics",
                        "previousValue": 216.18,
                        "sector": "Technology",
                        "size": "large",
                    }
                }
            },
        )
        for payload in malformed_payloads:
            with self.subTest(payload=payload):
                client = client_with_payload(payload)
                with self.assertRaisesRegex(QuantDataClientError, "market map response"):
                    client.get_market_map()


class StockPriceOverTimeTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(STOCK_PRICE_PAYLOAD)

        result = client.get_stock_price_over_time(
            " AAPL ",
            sessionDate="2026-05-13",
            aggregationPeriod="5m",
        )

        self.assertEqual(result, STOCK_PRICE_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/equities/tool/stock-price-over-time",
            json={
                "sessionDate": "2026-05-13",
                "aggregationPeriod": "5m",
                "filter": {"ticker": "AAPL"},
            },
            timeout=30,
        )

    def test_returns_typed_dataframes_in_timestamp_order(self):
        expected_columns = [
            "timestamp",
            "ConvertedDateTime",
            "openPrice",
            "highPrice",
            "lowPrice",
            "closePrice",
        ]
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    STOCK_PRICE_PAYLOAD,
                    output_type=output_type,
                )

                frame = client.get_stock_price_over_time("AAPL")

                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), expected_columns)
                self.assertEqual(
                    frame["timestamp"].to_list(),
                    [1747137600000, 1747137900000],
                )
                self.assertEqual(
                    frame["ConvertedDateTime"].to_list(),
                    [
                        datetime(
                            2025,
                            5,
                            13,
                            8,
                            tzinfo=ZoneInfo("America/New_York"),
                        ),
                        datetime(
                            2025,
                            5,
                            13,
                            8,
                            5,
                            tzinfo=ZoneInfo("America/New_York"),
                        ),
                    ],
                )

    def test_returns_typed_empty_dataframe(self):
        client = client_with_payload({"data": {}}, output_type="polars")

        frame = client.get_stock_price_over_time("AAPL")

        self.assertEqual(frame.shape, (0, 6))
        self.assertEqual(frame.schema["timestamp"], pl.Int64)
        self.assertEqual(
            frame.schema["ConvertedDateTime"],
            pl.Datetime("us", "America/New_York"),
        )
        self.assertEqual(frame.schema["closePrice"], pl.Float64)

    def test_rejects_blank_ticker_before_transport(self):
        client = client_with_payload(STOCK_PRICE_PAYLOAD)

        with self.assertRaisesRegex((TypeError, ValueError), "ticker"):
            client.get_stock_price_over_time("")

        client._session.post.assert_not_called()

    def test_rejects_malformed_success_payload(self):
        malformed_payloads = (
            {},
            {"data": []},
            {"data": {"1747137600000": {"openPrice": 213.42}}},
            {
                "data": {
                    "1747137600000": {
                        "openPrice": 213.42,
                        "highPrice": 213.81,
                        "lowPrice": 213.10,
                        "closePrice": None,
                    }
                }
            },
        )
        for payload in malformed_payloads:
            with self.subTest(payload=payload):
                client = client_with_payload(payload)
                with self.assertRaisesRegex(
                    QuantDataClientError,
                    "stock price over time response",
                ):
                    client.get_stock_price_over_time("AAPL")


class EquityPrintsTests(unittest.TestCase):
    def test_posts_exact_page_request_and_returns_complete_json(self):
        client = client_with_payload(EQUITY_PRINTS_PAYLOAD)
        result = client.get_equity_prints(
            sessionDate="2026-05-13",
            size=50,
            searchAfter=["cursor", "id"],
            sortField="tradeTime",
            sortDirection="descending",
            includes=["ID", "TICKER", "TRADE_TIME"],
            tickers=["AAPL"],
            equityPrintTypes=["DARK_POOL"],
        )
        self.assertEqual(result, EQUITY_PRINTS_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/equities/tool/equity-prints",
            json={
                "sessionDate": "2026-05-13",
                "size": 50,
                "searchAfter": ["cursor", "id"],
                "sort": {"field": "tradeTime", "direction": "DESCENDING"},
                "includes": ["ID", "TICKER", "TRADE_TIME"],
                "filter": {
                    "tickers": ["AAPL"],
                    "equityPrintTypes": ["DARK_POOL"],
                },
            },
            timeout=30,
        )

    def test_accepts_absent_null_and_list_terminal_cursors(self):
        for payload in (
            {"data": []},
            {"data": [], "nextSearchAfter": None},
            {"data": [], "nextSearchAfter": [1, "id"]},
        ):
            with self.subTest(payload=payload):
                client = client_with_payload(payload)
                self.assertEqual(client.get_equity_prints(), payload)

    def test_rejects_invalid_page_options_and_payloads(self):
        for size in (0, 101):
            client = client_with_payload(EQUITY_PRINTS_PAYLOAD)
            with self.subTest(size=size), self.assertRaisesRegex(ValueError, "size"):
                client.get_equity_prints(size=size)
            client._session.post.assert_not_called()

        client = client_with_payload(EQUITY_PRINTS_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "mutually exclusive"):
            client.get_equity_prints(includes=["ID"], excludes=["TICKER"])

        for payload in ({"data": {}}, {"data": [], "nextSearchAfter": "bad"}):
            with self.subTest(payload=payload):
                client = client_with_payload(payload)
                with self.assertRaisesRegex(QuantDataClientError, "equity prints response"):
                    client.get_equity_prints()

    def test_rejects_dataframe_output_before_transport(self):
        for output_type in ("pandas", "polars"):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    EQUITY_PRINTS_PAYLOAD,
                    output_type=output_type,
                )
                with self.assertRaisesRegex(Exception, "JSON"):
                    client.get_equity_prints()
                client._session.post.assert_not_called()


class ExchangeNotificationsTests(unittest.TestCase):
    def test_posts_exact_page_request_and_returns_complete_json(self):
        expression = {"field": "TYPE", "comparator": "EQUALS", "value": "LUDP"}
        client = client_with_payload(EXCHANGE_NOTIFICATIONS_PAYLOAD)
        result = client.get_exchange_notifications(
            sessionDate="2026-05-13",
            size=25,
            searchAfter=["cursor", "id"],
            sortField="createdTime",
            sortDirection="descending",
            excludes=["ID"],
            tickers=["AAPL"],
            types=["LUDP"],
            filterExpression=expression,
        )
        self.assertEqual(result, EXCHANGE_NOTIFICATIONS_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/equities/tool/exchange-notifications",
            json={
                "sessionDate": "2026-05-13",
                "size": 25,
                "searchAfter": ["cursor", "id"],
                "sort": {"field": "createdTime", "direction": "DESCENDING"},
                "excludes": ["ID"],
                "filter": {"tickers": ["AAPL"], "types": ["LUDP"]},
                "filterExpression": expression,
            },
            timeout=30,
        )

    def test_accepts_terminal_page_cursor_shapes(self):
        for payload in ({"data": []}, {"data": [], "nextSearchAfter": None}):
            with self.subTest(payload=payload):
                client = client_with_payload(payload)
                self.assertEqual(client.get_exchange_notifications(), payload)

    def test_rejects_invalid_page_shape_and_size(self):
        client = client_with_payload(EXCHANGE_NOTIFICATIONS_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "size"):
            client.get_exchange_notifications(size=101)
        client._session.post.assert_not_called()

        for payload in ({"data": {}}, {"data": [], "nextSearchAfter": "bad"}):
            with self.subTest(payload=payload):
                client = client_with_payload(payload)
                with self.assertRaisesRegex(
                    QuantDataClientError,
                    "exchange notifications response",
                ):
                    client.get_exchange_notifications()

    def test_rejects_dataframe_output_before_transport(self):
        client = client_with_payload(
            EXCHANGE_NOTIFICATIONS_PAYLOAD,
            output_type="pandas",
        )
        with self.assertRaisesRegex(Exception, "JSON"):
            client.get_exchange_notifications()
        client._session.post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
