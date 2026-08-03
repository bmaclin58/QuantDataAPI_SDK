from datetime import date
import unittest

import pandas as pd
import polars as pl

from QuantDataAPI.errors import QuantDataClientError, QuantDataConfigurationError
from tests.endpoint_test_support import client_with_payload


CONTRACT_STATISTICS_PAYLOAD = {
    "data": {
        "PUT": {"premium": 10_283_745.25, "tradeCount": 15_319, "volume": 31_441},
        "CALL": {"premium": 18_420_330.50, "tradeCount": 28_472, "volume": 61_208},
    }
}

TRADE_SIDE_PAYLOAD = {
    "data": {
        "CALL": {
            "ABOVE_ASK": {"premium": 5.0},
            "ASK": {"premium": 4.0},
            "MID_MARKET": {"premium": 3.0},
            "BID": {"premium": 2.0},
            "BELOW_BID": {"premium": 1.0},
        }
    }
}

GAINERS_LOSERS_PAYLOAD = {
    "data": {
        "NVDA": {
            "bearishPremium": 9.0,
            "bullishPremium": 0.0,
            "premium": 9.0,
            "premiumRatio": 0.0,
            "tradeCount": 25,
            "volume": 58,
        },
        "AAPL": {
            "bearishPremium": 4.0,
            "bullishPremium": 6.0,
            "premium": 10.0,
            "premiumRatio": 0.667,
            "tradeCount": 18,
            "volume": 41,
        },
    }
}

MARKET_SHARE_PAYLOAD = {
    "data": {
        "CBOE": {
            "equityCallPremium": 18.0,
            "equityCallTradeCount": 28,
            "equityCallVolume": 61,
            "equityPutPremium": 10.0,
            "equityPutTradeCount": 15,
            "equityPutVolume": 31,
            "indexPremium": 8.0,
            "indexTradeCount": 8,
            "indexVolume": 18,
        }
    }
}

MAX_PAIN_PAYLOAD = {
    "data": {
        "220.0": {"callIntrinsicValue": 815_240.0, "putIntrinsicValue": 412_050.0},
        "210.0": {"callIntrinsicValue": 1_842_010.0, "putIntrinsicValue": 92_410.0},
    },
    "maxPainStrikePrice": 220.0,
    "stockPrice": 218.42,
}

MAX_PAIN_OVER_TIME_PAYLOAD = {
    "data": {"2026-05-23": 220.0, "2026-05-16": 217.5}
}

OI_BY_EXPIRATION_PAYLOAD = {
    "data": {
        "2026-05-23": {"callOpenInterest": 88_010, "putOpenInterest": 41_200},
        "2026-05-16": {"callOpenInterest": 184_201, "putOpenInterest": 92_410},
    }
}

OI_BY_STRIKE_PAYLOAD = {
    "data": {
        "220.0": {"callOpenInterest": 132_045, "putOpenInterest": 75_320},
        "210.0": {"callOpenInterest": 184_201, "putOpenInterest": 92_410},
    }
}

OI_OVER_TIME_PAYLOAD = {
    "data": {
        "2026-05-13": {"callOpenInterest": 184_201, "putOpenInterest": 92_410},
        "2026-05-09": {"callOpenInterest": 162_034, "putOpenInterest": 75_320},
    }
}

NET_DRIFT_PAYLOAD = {
    "data": {
        "1747137900000": {
            "midMarketCallPremium": 2.91,
            "midMarketPutPremium": 1.88,
            "netCallPremium": 221_340.75,
            "netCallVolume": 7_102,
            "netPutPremium": 95_412.40,
            "netPutVolume": 3_608,
        },
        "1747137600000": {
            "midMarketCallPremium": 2.85,
            "midMarketPutPremium": 1.92,
            "netCallPremium": 184_201.50,
            "netCallVolume": 6_428,
            "netPutPremium": 102_837.25,
            "netPutVolume": 3_915,
            "stockPrice": 213.45,
        },
    }
}

NET_FLOW_PAYLOAD = {
    "data": {
        "1747137900000": {"callSum": 22_134_075, "putSum": 9_541_240},
        "1747137600000": {
            "callSum": 18_420_150,
            "putSum": 10_283_725,
            "stockPrice": 213.45,
        },
    }
}

OPTION_PRICE_PAYLOAD = {
    "data": {
        "1747137900000": {
            "openPrice": 2.92,
            "highPrice": 3.05,
            "lowPrice": 2.90,
            "closePrice": 3.01,
            "volume": 2_103,
        },
        "1747137600000": {
            "openPrice": 2.85,
            "highPrice": 2.94,
            "lowPrice": 2.81,
            "closePrice": 2.92,
            "volume": 1_428,
        },
    }
}

VOLATILITY_DRIFT_PAYLOAD = {
    "data": {
        "1747137660000": {"arv": 0.2420, "iv": None, "stockPrice": 213.51},
        "1747137600000": {"arv": None, "iv": 0.2538, "stockPrice": 213.45},
    }
}

EXPOSURE_PAYLOAD = {
    "data": {
        "AAPL": {
            "exposureMap": {
                "2026-05-16": {
                    "220.0": {"putExposure": -110_205},
                    "215.0": {"callExposure": 184_201, "putExposure": -92_410},
                }
            },
            "stockPrice": 218.45,
        }
    }
}

HEAT_MAP_CONTRACT_PAYLOAD = {
    "type": "contract",
    "data": {
        "2026-05-16": {
            "220.0": {"callValue": 221_340, "putValue": -110_205},
            "215.0": {"callValue": 184_201, "putValue": -92_410},
        }
    },
}
HEAT_MAP_SINGLE_PAYLOAD = {
    "type": "single",
    "data": {"2026-05-16": {"215.0": {"value": 0.612}}},
}

INTERVAL_MAP_PAYLOAD = {
    "data": {
        "1782245700000": {
            "2026-06-23": {"730.0": {"CALL": 10, "PUT": -20}}
        },
        "1782245640000": {
            "2026-06-23": {"729.0": {"PUT": -151_883_390}}
        },
    }
}

IV_RANK_PAYLOAD = {
    "expirationDates": ["2026-05-16", "2026-05-23"],
    "data": {
        "2026-05-13": {
            "contractTypeToIVData": {
                "PUT": {"lastIv": 0.2502, "windowMaxIv": 0.3210, "windowMinIv": 0.1910},
                "CALL": {"lastIv": 0.2412, "windowMaxIv": 0.3120, "windowMinIv": 0.1840},
            },
            "expirationDate": "2026-05-16",
            "stockPrice": 213.45,
        }
    },
}

TERM_STRUCTURE_PAYLOAD = {
    "stockPrice": 218.45,
    "data": {
        "2026-05-16": {
            "215.0": {
                "PUT": {"delta": -0.388, "iv": 0.2612, "moneyType": "OTM"},
                "CALL": {"delta": 0.612, "iv": 0.2538, "moneyType": "ITM"},
            }
        }
    },
}

VOLATILITY_SKEW_PAYLOAD = {
    "stockPrice": 218.45,
    "data": {
        "2026-05-16": {
            "215.0": {"PUT": 0.2778, "CALL": 0.2622},
            "220.0": {"CALL": 0.2538},
        }
    },
}

OPEN_INTEREST_CHANGE_PAGE = {
    "data": [
        {
            "id": "5f4c2e9a",
            "ticker": "AAPL",
            "changeInOpenInterest": 18_102,
        }
    ],
    "nextSearchAfter": ["18102", "5f4c2e9a"],
}

ORDER_FLOW_CONSOLIDATED_PAGE = {
    "data": [{"id": "5f4c2e9a", "ticker": "AAPL", "premium": 142_500.0}],
    "statistics": {"CALL": {"ABOVE_ASK": {"premium": 142_500.0}}},
    "nextSearchAfter": ["1747137612000", "5f4c2e9a"],
}

ORDER_FLOW_UNCONSOLIDATED_PAGE = {
    "data": [
        {
            "id": "a1b2c3d4-7890-4321-aabb-ccddeeff0011",
            "ticker": "AAPL",
            "osi": "AAPL260516C00220000",
            "premium": 28_500.0,
        }
    ],
    "statistics": {"CALL": {"ABOVE_ASK": {"premium": 28_500.0}}},
    "nextSearchAfter": [
        "1747137612000",
        "a1b2c3d4-7890-4321-aabb-ccddeeff0011",
    ],
}


class ExpirationDateDataFrameTests(unittest.TestCase):
    def test_every_expiration_date_column_uses_native_date_type(self):
        cases = (
            (
                EXPOSURE_PAYLOAD,
                "get_exposure_by_expiration",
                ("AAPL", "DELTA", "RAW"),
            ),
            (HEAT_MAP_CONTRACT_PAYLOAD, "get_heat_map", ("AAPL", "NET_VOLUME")),
            (HEAT_MAP_SINGLE_PAYLOAD, "get_heat_map", ("AAPL", "CALL_DELTA")),
            (INTERVAL_MAP_PAYLOAD, "get_interval_map", ("SPY", "GAMMA")),
            (IV_RANK_PAYLOAD, "get_iv_rank", ("AAPL", 30, 30)),
            (
                MAX_PAIN_OVER_TIME_PAYLOAD,
                "get_max_pain_over_time",
                ("AAPL",),
            ),
            (
                OI_BY_EXPIRATION_PAYLOAD,
                "get_open_interest_by_expiration",
                ("AAPL",),
            ),
            (TERM_STRUCTURE_PAYLOAD, "get_term_structure", ("AAPL",)),
            (VOLATILITY_SKEW_PAYLOAD, "get_volatility_skew", ("AAPL",)),
        )

        for output_type in ("pandas", "polars"):
            for payload, method_name, args in cases:
                with self.subTest(output_type=output_type, method=method_name):
                    client = client_with_payload(payload, output_type=output_type)
                    frame = getattr(client, method_name)(*args)
                    if output_type == "pandas":
                        self.assertEqual(frame["expirationDate"].dtype.kind, "M")
                    else:
                        self.assertEqual(frame.schema["expirationDate"], pl.Date)


class ContractStatisticsTests(unittest.TestCase):
    def test_posts_empty_and_filtered_requests(self):
        cases = (
            ({}, {}),
            (
                {"sessionDate": "2026-05-13", "ticker": "AAPL"},
                {"sessionDate": "2026-05-13", "filter": {"ticker": "AAPL"}},
            ),
        )
        for kwargs, expected_body in cases:
            with self.subTest(kwargs=kwargs):
                client = client_with_payload(CONTRACT_STATISTICS_PAYLOAD)

                result = client.get_contract_statistics(**kwargs)

                self.assertEqual(result, CONTRACT_STATISTICS_PAYLOAD)
                client._session.post.assert_called_once_with(
                    "https://api.quantdata.us/v1/options/tool/contract-statistics",
                    json=expected_body,
                    timeout=30,
                )

    def test_returns_typed_dataframes(self):
        expected_columns = ["contractType", "premium", "tradeCount", "volume"]
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    CONTRACT_STATISTICS_PAYLOAD,
                    output_type=output_type,
                )

                frame = client.get_contract_statistics()

                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), expected_columns)
                self.assertEqual(frame["contractType"].to_list(), ["CALL", "PUT"])

    def test_returns_typed_empty_dataframe(self):
        client = client_with_payload({"data": {}}, output_type="polars")

        frame = client.get_contract_statistics()

        self.assertEqual(frame.shape, (0, 4))
        self.assertEqual(frame.schema["premium"], pl.Float64)
        self.assertEqual(frame.schema["tradeCount"], pl.Int64)

    def test_rejects_malformed_success_payload(self):
        for payload in ({}, {"data": []}, {"data": {"CALL": {"premium": 1.0}}}):
            with self.subTest(payload=payload):
                client = client_with_payload(payload)
                with self.assertRaisesRegex(
                    QuantDataClientError,
                    "contract statistics response",
                ):
                    client.get_contract_statistics()


class ContractTradeSideStatisticsTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(TRADE_SIDE_PAYLOAD)

        result = client.get_contract_trade_side_statistics(
            "premium",
            sessionDate="2026-05-13",
            ticker="AAPL",
        )

        self.assertEqual(result, TRADE_SIDE_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/contract-trade-side-statistics",
            json={
                "dataMode": "PREMIUM",
                "sessionDate": "2026-05-13",
                "filter": {"ticker": "AAPL"},
            },
            timeout=30,
        )

    def test_flattens_all_wire_trade_sides_for_dataframes(self):
        expected_sides = ["ABOVE_ASK", "ASK", "BELOW_BID", "BID", "MID_MARKET"]
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    TRADE_SIDE_PAYLOAD,
                    output_type=output_type,
                )

                frame = client.get_contract_trade_side_statistics("PREMIUM")

                self.assertIsInstance(frame, frame_type)
                self.assertEqual(
                    list(frame.columns),
                    ["contractType", "tradeSide", "dataMode", "value"],
                )
                self.assertEqual(frame["tradeSide"].to_list(), expected_sides)
                self.assertEqual(frame["dataMode"].to_list(), ["PREMIUM"] * 5)

    def test_validates_mode_and_returns_typed_empty_dataframe(self):
        client = client_with_payload({"data": {}}, output_type="polars")
        frame = client.get_contract_trade_side_statistics("VOLUME")
        self.assertEqual(frame.shape, (0, 4))
        self.assertEqual(frame.schema["value"], pl.Float64)

        client = client_with_payload(TRADE_SIDE_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "dataMode"):
            client.get_contract_trade_side_statistics("NOT_A_MODE")
        client._session.post.assert_not_called()

    def test_rejects_malformed_success_payload(self):
        malformed = {
            "data": {"CALL": {"ASK": {"tradeCount": 1}}}
        }
        client = client_with_payload(malformed)

        with self.assertRaisesRegex(
            QuantDataClientError,
            "contract trade-side statistics response",
        ):
            client.get_contract_trade_side_statistics("PREMIUM")


class GainersLosersTests(unittest.TestCase):
    def test_posts_empty_and_filtered_requests(self):
        cases = (
            ({}, {}),
            (
                {
                    "sessionDate": "2026-05-13",
                    "sectors": ["Technology"],
                    "dteRange": {"min": 0, "max": 7},
                },
                {
                    "sessionDate": "2026-05-13",
                    "filter": {
                        "sectors": ["Technology"],
                        "dteRange": {"min": 0, "max": 7},
                    },
                },
            ),
        )
        for kwargs, expected_body in cases:
            with self.subTest(kwargs=kwargs):
                client = client_with_payload(GAINERS_LOSERS_PAYLOAD)
                result = client.get_gainers_losers(**kwargs)
                self.assertEqual(result, GAINERS_LOSERS_PAYLOAD)
                client._session.post.assert_called_once_with(
                    "https://api.quantdata.us/v1/options/tool/gainers-losers",
                    json=expected_body,
                    timeout=30,
                )

    def test_returns_typed_dataframes_and_preserves_zero_ratio(self):
        columns = [
            "ticker",
            "bearishPremium",
            "bullishPremium",
            "premium",
            "premiumRatio",
            "tradeCount",
            "volume",
        ]
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    GAINERS_LOSERS_PAYLOAD,
                    output_type=output_type,
                )
                frame = client.get_gainers_losers()
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), columns)
                self.assertEqual(frame["ticker"].to_list(), ["AAPL", "NVDA"])
                self.assertEqual(frame["premiumRatio"].to_list()[1], 0.0)

    def test_empty_and_malformed_payloads(self):
        client = client_with_payload({"data": {}}, output_type="polars")
        frame = client.get_gainers_losers()
        self.assertEqual(frame.shape, (0, 7))
        self.assertEqual(frame.schema["tradeCount"], pl.Int64)

        client = client_with_payload({"data": {"AAPL": {"premium": 1.0}}})
        with self.assertRaisesRegex(QuantDataClientError, "gainers/losers response"):
            client.get_gainers_losers()


class MarketShareTests(unittest.TestCase):
    def test_posts_empty_and_filtered_requests(self):
        for kwargs, body in (
            ({}, {}),
            (
                {"sessionDate": "2026-05-13", "tickers": ["AAPL", "NVDA"]},
                {
                    "sessionDate": "2026-05-13",
                    "filter": {"tickers": ["AAPL", "NVDA"]},
                },
            ),
        ):
            with self.subTest(kwargs=kwargs):
                client = client_with_payload(MARKET_SHARE_PAYLOAD)
                result = client.get_market_share(**kwargs)
                self.assertEqual(result, MARKET_SHARE_PAYLOAD)
                client._session.post.assert_called_once_with(
                    "https://api.quantdata.us/v1/options/tool/market-share",
                    json=body,
                    timeout=30,
                )

    def test_returns_typed_dataframes_with_all_nine_metrics(self):
        columns = ["exchange"] + list(next(iter(MARKET_SHARE_PAYLOAD["data"].values())))
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    MARKET_SHARE_PAYLOAD,
                    output_type=output_type,
                )
                frame = client.get_market_share()
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), columns)
                self.assertEqual(frame["exchange"].to_list(), ["CBOE"])

    def test_empty_and_malformed_payloads(self):
        client = client_with_payload({"data": {}}, output_type="polars")
        frame = client.get_market_share()
        self.assertEqual(frame.shape, (0, 10))
        self.assertEqual(frame.schema["indexVolume"], pl.Int64)

        client = client_with_payload({"data": {"CBOE": {"indexVolume": 1}}})
        with self.assertRaisesRegex(QuantDataClientError, "market share response"):
            client.get_market_share()


class MaxPainTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(MAX_PAIN_PAYLOAD)
        result = client.get_max_pain(
            " AAPL ",
            "2026-05-16",
            sessionDate="2026-05-13",
        )
        self.assertEqual(result, MAX_PAIN_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/max-pain",
            json={
                "sessionDate": "2026-05-13",
                "filter": {"ticker": "AAPL", "expirationDate": "2026-05-16"},
            },
            timeout=30,
        )

    def test_returns_sorted_typed_dataframes_with_repeated_metadata(self):
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(MAX_PAIN_PAYLOAD, output_type=output_type)
                frame = client.get_max_pain("AAPL", "2026-05-16")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(
                    list(frame.columns),
                    [
                        "strikePrice",
                        "callIntrinsicValue",
                        "putIntrinsicValue",
                        "maxPainStrikePrice",
                        "stockPrice",
                    ],
                )
                self.assertEqual(frame["strikePrice"].to_list(), [210.0, 220.0])
                self.assertEqual(frame["stockPrice"].to_list(), [218.42, 218.42])

    def test_validates_required_fields_and_success_payload(self):
        client = client_with_payload(MAX_PAIN_PAYLOAD)
        with self.assertRaisesRegex((TypeError, ValueError), "ticker"):
            client.get_max_pain(" ", "2026-05-16")
        client._session.post.assert_not_called()

        client = client_with_payload(
            {"data": {}, "maxPainStrikePrice": 220.0, "stockPrice": 218.42},
            output_type="polars",
        )
        self.assertEqual(client.get_max_pain("AAPL", "2026-05-16").shape, (0, 5))

        client = client_with_payload({"data": {}, "stockPrice": 218.42})
        with self.assertRaisesRegex(QuantDataClientError, "max pain response"):
            client.get_max_pain("AAPL", "2026-05-16")


class MaxPainOverTimeTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(MAX_PAIN_OVER_TIME_PAYLOAD)
        result = client.get_max_pain_over_time(
            " AAPL ",
            sessionDate="2026-05-13",
        )
        self.assertEqual(result, MAX_PAIN_OVER_TIME_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/max-pain-over-time",
            json={"sessionDate": "2026-05-13", "filter": {"ticker": "AAPL"}},
            timeout=30,
        )

    def test_returns_typed_dataframes_and_documented_empty(self):
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    MAX_PAIN_OVER_TIME_PAYLOAD,
                    output_type=output_type,
                )
                frame = client.get_max_pain_over_time("AAPL")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(
                    list(frame.columns),
                    ["expirationDate", "maxPainStrikePrice"],
                )
                self.assertEqual(
                    [
                        value.date() if hasattr(value, "date") else value
                        for value in frame["expirationDate"].to_list()
                    ],
                    [date(2026, 5, 16), date(2026, 5, 23)],
                )
                if output_type == "pandas":
                    self.assertEqual(frame["expirationDate"].dtype.kind, "M")
                else:
                    self.assertEqual(frame.schema["expirationDate"], pl.Date)

        empty_client = client_with_payload({"data": {}}, output_type="polars")
        empty = empty_client.get_max_pain_over_time("AAPL")
        self.assertEqual(empty.shape, (0, 2))
        self.assertEqual(empty.schema["maxPainStrikePrice"], pl.Float64)

    def test_rejects_blank_ticker_and_malformed_value(self):
        client = client_with_payload(MAX_PAIN_OVER_TIME_PAYLOAD)
        with self.assertRaisesRegex((TypeError, ValueError), "ticker"):
            client.get_max_pain_over_time("")
        client._session.post.assert_not_called()

        client = client_with_payload({"data": {"2026-05-16": None}})
        with self.assertRaisesRegex(
            QuantDataClientError,
            "max pain over time response",
        ):
            client.get_max_pain_over_time("AAPL")


class OpenInterestByExpirationTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(OI_BY_EXPIRATION_PAYLOAD)
        result = client.get_open_interest_by_expiration(
            " AAPL ",
            sessionDate="2026-05-13",
            strikePrice=215.0,
        )
        self.assertEqual(result, OI_BY_EXPIRATION_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/open-interest-by-expiration",
            json={
                "sessionDate": "2026-05-13",
                "filter": {"ticker": "AAPL", "strikePrice": 215.0},
            },
            timeout=30,
        )

    def test_returns_expiration_sorted_typed_dataframes(self):
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    OI_BY_EXPIRATION_PAYLOAD,
                    output_type=output_type,
                )
                frame = client.get_open_interest_by_expiration("AAPL")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(
                    list(frame.columns),
                    ["expirationDate", "callOpenInterest", "putOpenInterest"],
                )
                self.assertEqual(
                    [
                        value.date() if hasattr(value, "date") else value
                        for value in frame["expirationDate"].to_list()
                    ],
                    [date(2026, 5, 16), date(2026, 5, 23)],
                )

    def test_empty_invalid_strike_and_malformed_cell(self):
        client = client_with_payload({"data": {}}, output_type="polars")
        frame = client.get_open_interest_by_expiration("AAPL")
        self.assertEqual(frame.shape, (0, 3))
        self.assertEqual(frame.schema["callOpenInterest"], pl.Int64)

        client = client_with_payload(OI_BY_EXPIRATION_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "strikePrice"):
            client.get_open_interest_by_expiration("AAPL", strikePrice=0)
        client._session.post.assert_not_called()

        client = client_with_payload(
            {"data": {"2026-05-16": {"callOpenInterest": 1.5, "putOpenInterest": 2}}}
        )
        with self.assertRaisesRegex(
            QuantDataClientError,
            "open interest by expiration response",
        ):
            client.get_open_interest_by_expiration("AAPL")


class OpenInterestByStrikeTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(OI_BY_STRIKE_PAYLOAD)
        result = client.get_open_interest_by_strike(
            " AAPL ",
            sessionDate="2026-05-13",
            expirationDate="2026-05-16",
        )
        self.assertEqual(result, OI_BY_STRIKE_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/open-interest-by-strike",
            json={
                "sessionDate": "2026-05-13",
                "filter": {"ticker": "AAPL", "expirationDate": "2026-05-16"},
            },
            timeout=30,
        )

    def test_returns_strike_sorted_typed_dataframes(self):
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(OI_BY_STRIKE_PAYLOAD, output_type=output_type)
                frame = client.get_open_interest_by_strike("AAPL")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(
                    list(frame.columns),
                    ["strikePrice", "callOpenInterest", "putOpenInterest"],
                )
                self.assertEqual(frame["strikePrice"].to_list(), [210.0, 220.0])

    def test_empty_blank_ticker_and_malformed_cell(self):
        client = client_with_payload({"data": {}}, output_type="polars")
        frame = client.get_open_interest_by_strike("AAPL")
        self.assertEqual(frame.shape, (0, 3))
        self.assertEqual(frame.schema["strikePrice"], pl.Float64)

        client = client_with_payload(OI_BY_STRIKE_PAYLOAD)
        with self.assertRaisesRegex((TypeError, ValueError), "ticker"):
            client.get_open_interest_by_strike(" ")
        client._session.post.assert_not_called()

        client = client_with_payload(
            {"data": {"210.0": {"callOpenInterest": 1, "putOpenInterest": "2"}}}
        )
        with self.assertRaisesRegex(
            QuantDataClientError,
            "open interest by strike response",
        ):
            client.get_open_interest_by_strike("AAPL")


class OpenInterestOverTimeTests(unittest.TestCase):
    def test_posts_filter_only_request_and_returns_json(self):
        client = client_with_payload(OI_OVER_TIME_PAYLOAD)
        result = client.get_open_interest_over_time(
            " AAPL ",
            expirationDate="2026-05-16",
            strikePrice=215.0,
        )
        self.assertEqual(result, OI_OVER_TIME_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/open-interest-over-time",
            json={
                "filter": {
                    "ticker": "AAPL",
                    "expirationDate": "2026-05-16",
                    "strikePrice": 215.0,
                }
            },
            timeout=30,
        )

    def test_returns_session_sorted_typed_dataframes(self):
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(OI_OVER_TIME_PAYLOAD, output_type=output_type)
                frame = client.get_open_interest_over_time("AAPL")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(
                    list(frame.columns),
                    ["sessionDate", "callOpenInterest", "putOpenInterest"],
                )
                self.assertEqual(
                    frame["sessionDate"].to_list(),
                    ["2026-05-09", "2026-05-13"],
                )

    def test_empty_invalid_strike_and_malformed_cell(self):
        client = client_with_payload({"data": {}}, output_type="polars")
        frame = client.get_open_interest_over_time("AAPL")
        self.assertEqual(frame.shape, (0, 3))
        self.assertEqual(frame.schema["putOpenInterest"], pl.Int64)

        client = client_with_payload(OI_OVER_TIME_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "strikePrice"):
            client.get_open_interest_over_time("AAPL", strikePrice=-1)
        client._session.post.assert_not_called()

        client = client_with_payload(
            {"data": {"2026-05-13": {"callOpenInterest": True, "putOpenInterest": 2}}}
        )
        with self.assertRaisesRegex(
            QuantDataClientError,
            "open interest over time response",
        ):
            client.get_open_interest_over_time("AAPL")


class NetDriftTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(NET_DRIFT_PAYLOAD)
        result = client.get_net_drift(
            sessionDate="2026-05-13",
            aggregationPeriod="15m",
            tickers=["AAPL", "NVDA"],
        )
        self.assertEqual(result, NET_DRIFT_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/net-drift",
            json={
                "sessionDate": "2026-05-13",
                "aggregationPeriod": "15m",
                "filter": {"tickers": ["AAPL", "NVDA"]},
            },
            timeout=30,
        )

    def test_returns_sorted_typed_dataframes_with_nullable_stock_price(self):
        columns = [
            "timestamp",
            "ConvertedDateTime",
            "midMarketCallPremium",
            "midMarketPutPremium",
            "netCallPremium",
            "netCallVolume",
            "netPutPremium",
            "netPutVolume",
            "stockPrice",
        ]
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(NET_DRIFT_PAYLOAD, output_type=output_type)
                frame = client.get_net_drift()
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), columns)
                self.assertEqual(
                    frame["timestamp"].to_list(),
                    [1747137600000, 1747137900000],
                )
                self.assertTrue(pd.isna(frame["stockPrice"].to_list()[1]))

    def test_empty_and_malformed_payloads(self):
        client = client_with_payload({"data": {}}, output_type="polars")
        frame = client.get_net_drift()
        self.assertEqual(frame.shape, (0, 9))
        self.assertEqual(frame.schema["netCallVolume"], pl.Int64)

        client = client_with_payload(
            {"data": {"1": {"midMarketCallPremium": 1.0}}}
        )
        with self.assertRaisesRegex(QuantDataClientError, "net drift response"):
            client.get_net_drift()


class NetFlowTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(NET_FLOW_PAYLOAD)
        result = client.get_net_flow(
            "net_premium",
            sessionDate="2026-05-13",
            aggregationPeriod="5m",
            tickers=["AAPL"],
        )
        self.assertEqual(result, NET_FLOW_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/net-flow",
            json={
                "dataMode": "NET_PREMIUM",
                "sessionDate": "2026-05-13",
                "aggregationPeriod": "5m",
                "filter": {"tickers": ["AAPL"]},
            },
            timeout=30,
        )

    def test_returns_sorted_typed_dataframes_with_nullable_stock_price(self):
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(NET_FLOW_PAYLOAD, output_type=output_type)
                frame = client.get_net_flow("NET_VOLUME")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(
                    list(frame.columns),
                    [
                        "timestamp",
                        "ConvertedDateTime",
                        "callSum",
                        "putSum",
                        "stockPrice",
                    ],
                )
                self.assertEqual(
                    frame["timestamp"].to_list(),
                    [1747137600000, 1747137900000],
                )
                self.assertTrue(pd.isna(frame["stockPrice"].to_list()[1]))

    def test_validates_mode_and_payload(self):
        client = client_with_payload(NET_FLOW_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "dataMode"):
            client.get_net_flow("WRONG")
        client._session.post.assert_not_called()

        client = client_with_payload({"data": {}}, output_type="polars")
        self.assertEqual(client.get_net_flow("NET_VOLUME").shape, (0, 5))

        client = client_with_payload({"data": {"1": {"callSum": 1}}})
        with self.assertRaisesRegex(QuantDataClientError, "net flow response"):
            client.get_net_flow("NET_PREMIUM")


class OptionPriceOverTimeTests(unittest.TestCase):
    def test_posts_osi_and_per_field_identifier_requests(self):
        cases = (
            (
                {"osi": "AAPL260516C00220000", "sessionDate": "2026-05-13"},
                {
                    "sessionDate": "2026-05-13",
                    "filter": {"osi": "AAPL260516C00220000"},
                },
            ),
            (
                {
                    "ticker": "AAPL",
                    "expirationDate": "2026-05-16",
                    "strikePrice": 220.0,
                    "contractType": "call",
                },
                {
                    "filter": {
                        "ticker": "AAPL",
                        "expirationDate": "2026-05-16",
                        "strikePrice": 220.0,
                        "contractType": "CALL",
                    }
                },
            ),
        )
        for kwargs, body in cases:
            with self.subTest(kwargs=kwargs):
                client = client_with_payload(OPTION_PRICE_PAYLOAD)
                result = client.get_option_price_over_time(**kwargs)
                self.assertEqual(result, OPTION_PRICE_PAYLOAD)
                client._session.post.assert_called_once_with(
                    "https://api.quantdata.us/v1/options/tool/option-price-over-time",
                    json=body,
                    timeout=30,
                )

    def test_rejects_conflicting_and_incomplete_identifiers(self):
        cases = (
            {"osi": "AAPL260516C00220000", "ticker": "AAPL"},
            {"ticker": "AAPL", "expirationDate": "2026-05-16"},
            {},
        )
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                client = client_with_payload(OPTION_PRICE_PAYLOAD)
                with self.assertRaisesRegex(ValueError, "osi|Provide"):
                    client.get_option_price_over_time(**kwargs)
                client._session.post.assert_not_called()

    def test_returns_sorted_typed_dataframes(self):
        columns = [
            "timestamp",
            "ConvertedDateTime",
            "openPrice",
            "highPrice",
            "lowPrice",
            "closePrice",
            "volume",
        ]
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(OPTION_PRICE_PAYLOAD, output_type=output_type)
                frame = client.get_option_price_over_time(osi="AAPL260516C00220000")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), columns)
                self.assertEqual(
                    frame["timestamp"].to_list(),
                    [1747137600000, 1747137900000],
                )

    def test_empty_and_malformed_bars(self):
        client = client_with_payload({"data": {}}, output_type="polars")
        frame = client.get_option_price_over_time(osi="AAPL260516C00220000")
        self.assertEqual(frame.shape, (0, 7))
        self.assertEqual(frame.schema["volume"], pl.Int64)

        client = client_with_payload({"data": {"1": {"openPrice": 1.0}}})
        with self.assertRaisesRegex(
            QuantDataClientError,
            "option price over time response",
        ):
            client.get_option_price_over_time(osi="AAPL260516C00220000")


class VolatilityDriftTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(VOLATILITY_DRIFT_PAYLOAD)
        result = client.get_volatility_drift(
            " AAPL ",
            sessionDate="2026-05-13",
            expirationDate="2026-05-16",
        )
        self.assertEqual(result, VOLATILITY_DRIFT_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/volatility-drift",
            json={
                "sessionDate": "2026-05-13",
                "filter": {"ticker": "AAPL", "expirationDate": "2026-05-16"},
            },
            timeout=30,
        )

    def test_returns_sorted_typed_dataframes_with_nullable_volatility(self):
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    VOLATILITY_DRIFT_PAYLOAD,
                    output_type=output_type,
                )
                frame = client.get_volatility_drift("AAPL")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(
                    list(frame.columns),
                    [
                        "timestamp",
                        "ConvertedDateTime",
                        "arv",
                        "iv",
                        "stockPrice",
                    ],
                )
                self.assertEqual(
                    frame["timestamp"].to_list(),
                    [1747137600000, 1747137660000],
                )
                self.assertTrue(pd.isna(frame["arv"].to_list()[0]))
                self.assertTrue(pd.isna(frame["iv"].to_list()[1]))

    def test_empty_blank_ticker_and_malformed_values(self):
        client = client_with_payload({"data": {}}, output_type="polars")
        frame = client.get_volatility_drift("AAPL")
        self.assertEqual(frame.shape, (0, 5))
        self.assertEqual(frame.schema["arv"], pl.Float64)

        client = client_with_payload(VOLATILITY_DRIFT_PAYLOAD)
        with self.assertRaisesRegex((TypeError, ValueError), "ticker"):
            client.get_volatility_drift(" ")
        client._session.post.assert_not_called()

        client = client_with_payload(
            {"data": {"1": {"arv": 0.2, "iv": 0.3, "stockPrice": None}}}
        )
        with self.assertRaisesRegex(QuantDataClientError, "volatility drift response"):
            client.get_volatility_drift("AAPL")


class ExposureByExpirationTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(EXPOSURE_PAYLOAD)
        result = client.get_exposure_by_expiration(
            " AAPL ",
            "gamma",
            "raw",
            snapshotTime="2026-05-13T16:30:00Z",
            expirationDateRange={
                "startDate": "2026-05-16",
                "endDate": "2026-06-20",
            },
        )
        self.assertEqual(result, EXPOSURE_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/exposure-by-expiration",
            json={
                "greekMode": "GAMMA",
                "representationMode": "RAW",
                "snapshotTime": "2026-05-13T16:30:00Z",
                "filter": {
                    "ticker": "AAPL",
                    "expirationDateRange": {
                        "startDate": "2026-05-16",
                        "endDate": "2026-06-20",
                    },
                },
            },
            timeout=30,
        )

    def test_flattens_nested_rows_with_nullable_legs(self):
        columns = [
            "ticker",
            "expirationDate",
            "strikePrice",
            "callExposure",
            "putExposure",
            "stockPrice",
        ]
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(EXPOSURE_PAYLOAD, output_type=output_type)
                frame = client.get_exposure_by_expiration("AAPL", "DELTA", "RAW")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), columns)
                self.assertEqual(frame["strikePrice"].to_list(), [215.0, 220.0])
                self.assertTrue(pd.isna(frame["callExposure"].to_list()[1]))
                self.assertEqual(frame["stockPrice"].to_list(), [218.45, 218.45])

    def test_validates_enums_selectors_and_typed_empty(self):
        client = client_with_payload(EXPOSURE_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "greekMode"):
            client.get_exposure_by_expiration("AAPL", "RHO", "RAW")
        with self.assertRaisesRegex(ValueError, "mutually exclusive"):
            client.get_exposure_by_expiration(
                "AAPL",
                "DELTA",
                "RAW",
                sessionDate="2026-05-13",
                snapshotTime="2026-05-13T16:30:00Z",
            )
        client._session.post.assert_not_called()

        empty_client = client_with_payload({"data": {}}, output_type="polars")
        empty = empty_client.get_exposure_by_expiration("AAPL", "DELTA", "RAW")
        self.assertEqual(empty.shape, (0, 6))
        self.assertEqual(empty.schema["callExposure"], pl.Float64)

    def test_rejects_malformed_nested_payload(self):
        client = client_with_payload(
            {"data": {"AAPL": {"exposureMap": [], "stockPrice": 218.45}}}
        )
        with self.assertRaisesRegex(
            QuantDataClientError,
            "exposure by expiration response",
        ):
            client.get_exposure_by_expiration("AAPL", "DELTA", "RAW")


class ExposureByStrikeTests(unittest.TestCase):
    def test_posts_distinct_filtered_request_and_returns_json(self):
        client = client_with_payload(EXPOSURE_PAYLOAD)
        result = client.get_exposure_by_strike(
            " AAPL ",
            "gamma",
            "raw",
            snapshotTime="2026-05-13T16:30:00Z",
            expirationDate="2026-05-16",
            moneyTypes=["ATM", "ITM"],
        )
        self.assertEqual(result, EXPOSURE_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/exposure-by-strike",
            json={
                "greekMode": "GAMMA",
                "representationMode": "RAW",
                "snapshotTime": "2026-05-13T16:30:00Z",
                "filter": {
                    "ticker": "AAPL",
                    "expirationDate": "2026-05-16",
                    "moneyTypes": ["ATM", "ITM"],
                },
            },
            timeout=30,
        )

    def test_returns_both_typed_dataframe_formats(self):
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(EXPOSURE_PAYLOAD, output_type=output_type)
                frame = client.get_exposure_by_strike("AAPL", "DELTA", "RAW")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(frame["strikePrice"].to_list(), [215.0, 220.0])
                self.assertTrue(pd.isna(frame["callExposure"].to_list()[1]))

    def test_empty_and_malformed_nested_payload(self):
        empty_client = client_with_payload({"data": {}}, output_type="polars")
        empty = empty_client.get_exposure_by_strike("AAPL", "DELTA", "RAW")
        self.assertEqual(empty.shape, (0, 6))

        client = client_with_payload(
            {"data": {"AAPL": {"exposureMap": {}, "stockPrice": None}}}
        )
        with self.assertRaisesRegex(
            QuantDataClientError,
            "exposure by strike response",
        ):
            client.get_exposure_by_strike("AAPL", "DELTA", "RAW")


class HeatMapTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(HEAT_MAP_CONTRACT_PAYLOAD)
        result = client.get_heat_map(
            " AAPL ",
            "net_delta_exposure",
            sessionDate="2026-05-13",
            expirationDates=["2026-05-16"],
        )
        self.assertEqual(result, HEAT_MAP_CONTRACT_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/heat-map",
            json={
                "dataMode": "NET_DELTA_EXPOSURE",
                "sessionDate": "2026-05-13",
                "filter": {"ticker": "AAPL", "expirationDates": ["2026-05-16"]},
            },
            timeout=30,
        )

    def test_contract_type_uses_contract_schema(self):
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    HEAT_MAP_CONTRACT_PAYLOAD,
                    output_type=output_type,
                )
                frame = client.get_heat_map("AAPL", "NET_DELTA_EXPOSURE")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(
                    list(frame.columns),
                    ["type", "expirationDate", "strikePrice", "callValue", "putValue"],
                )
                self.assertEqual(frame["strikePrice"].to_list(), [215.0, 220.0])

    def test_single_type_uses_single_schema(self):
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    HEAT_MAP_SINGLE_PAYLOAD,
                    output_type=output_type,
                )
                frame = client.get_heat_map("AAPL", "CALL_DELTA")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(
                    list(frame.columns),
                    ["type", "expirationDate", "strikePrice", "value"],
                )
                self.assertEqual(frame["value"].to_list(), [0.612])

    def test_returns_mode_specific_typed_empty_frames(self):
        contract = client_with_payload(
            {"type": "contract", "data": {}},
            output_type="polars",
        ).get_heat_map("AAPL", "NET_VOLUME")
        single = client_with_payload(
            {"type": "single", "data": {}},
            output_type="polars",
        ).get_heat_map("AAPL", "PUT_DELTA")
        self.assertEqual(contract.shape, (0, 5))
        self.assertEqual(single.shape, (0, 4))
        self.assertEqual(contract.schema["callValue"], pl.Float64)
        self.assertEqual(single.schema["value"], pl.Float64)

    def test_rejects_invalid_mode_type_and_leaf_shape(self):
        client = client_with_payload(HEAT_MAP_CONTRACT_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "dataMode"):
            client.get_heat_map("AAPL", "WRONG")
        client._session.post.assert_not_called()

        for payload in (
            {"type": "future", "data": {}},
            {"type": "single", "data": {"2026-05-16": {"215.0": {"callValue": 1}}}},
        ):
            with self.subTest(payload=payload):
                client = client_with_payload(payload)
                with self.assertRaisesRegex(QuantDataClientError, "heat map response"):
                    client.get_heat_map("AAPL", "CALL_DELTA")


class IntervalMapTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(INTERVAL_MAP_PAYLOAD)
        result = client.get_interval_map(
            " SPY ",
            "gamma",
            sessionDate="2026-06-23",
            aggregationPeriod="1m",
            expirationDate="2026-06-23",
            minStrikePrice=725.0,
            maxStrikePrice=735.0,
        )
        self.assertEqual(result, INTERVAL_MAP_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/interval-map",
            json={
                "greekMode": "GAMMA",
                "sessionDate": "2026-06-23",
                "aggregationPeriod": "1m",
                "filter": {
                    "ticker": "SPY",
                    "expirationDate": "2026-06-23",
                    "minStrikePrice": 725.0,
                    "maxStrikePrice": 735.0,
                },
            },
            timeout=30,
        )

    def test_flattens_each_contract_leg_into_typed_rows(self):
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(INTERVAL_MAP_PAYLOAD, output_type=output_type)
                frame = client.get_interval_map("SPY", "GAMMA")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(
                    list(frame.columns),
                    [
                        "timestamp",
                        "ConvertedDateTime",
                        "expirationDate",
                        "strikePrice",
                        "contractType",
                        "exposure",
                    ],
                )
                self.assertEqual(
                    frame["contractType"].to_list(),
                    ["PUT", "CALL", "PUT"],
                )

    def test_empty_validation_and_malformed_leaf(self):
        empty = client_with_payload(
            {"data": {}},
            output_type="polars",
        ).get_interval_map("SPY", "GAMMA")
        self.assertEqual(empty.shape, (0, 6))
        self.assertEqual(empty.schema["exposure"], pl.Float64)

        client = client_with_payload(INTERVAL_MAP_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "greekMode"):
            client.get_interval_map("SPY", "RHO")
        client._session.post.assert_not_called()

        client = client_with_payload(
            {"data": {"1": {"2026-06-23": {"729.0": {"OTHER": 1}}}}}
        )
        with self.assertRaisesRegex(QuantDataClientError, "interval map response"):
            client.get_interval_map("SPY", "GAMMA")


class IVRankTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_json(self):
        client = client_with_payload(IV_RANK_PAYLOAD)
        result = client.get_iv_rank(
            " AAPL ",
            90,
            14,
            contractTypes=["call"],
        )
        self.assertEqual(result, IV_RANK_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/iv-rank",
            json={
                "lookBackPeriod": 90,
                "maturity": 14,
                "filter": {"ticker": "AAPL", "contractTypes": ["CALL"]},
            },
            timeout=30,
        )

    def test_flattens_session_and_contract_rows(self):
        columns = [
            "sessionDate",
            "contractType",
            "lastIv",
            "windowMinIv",
            "windowMaxIv",
            "expirationDate",
            "stockPrice",
        ]
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(IV_RANK_PAYLOAD, output_type=output_type)
                frame = client.get_iv_rank("AAPL", 30, 30)
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), columns)
                self.assertEqual(frame["contractType"].to_list(), ["CALL", "PUT"])

    def test_validates_period_boundaries_and_typed_empty(self):
        for value in (0, 366):
            with self.subTest(value=value):
                client = client_with_payload(IV_RANK_PAYLOAD)
                with self.assertRaisesRegex(ValueError, "lookBackPeriod"):
                    client.get_iv_rank("AAPL", value, 30)
                client._session.post.assert_not_called()

        for value in (1, 365):
            client = client_with_payload({"expirationDates": [], "data": {}}, output_type="polars")
            frame = client.get_iv_rank("AAPL", value, value)
            self.assertEqual(frame.shape, (0, 7))
            self.assertEqual(frame.schema["lastIv"], pl.Float64)

    def test_rejects_malformed_top_level_and_iv_cells(self):
        for payload in (
            {"expirationDates": {}, "data": {}},
            {
                "expirationDates": ["2026-05-16"],
                "data": {
                    "2026-05-13": {
                        "contractTypeToIVData": {"CALL": {"lastIv": 0.2}},
                        "expirationDate": "2026-05-16",
                        "stockPrice": 213.45,
                    }
                },
            },
        ):
            with self.subTest(payload=payload):
                client = client_with_payload(payload)
                with self.assertRaisesRegex(QuantDataClientError, "IV rank response"):
                    client.get_iv_rank("AAPL", 30, 30)


class TermStructureTests(unittest.TestCase):
    def test_posts_exact_filtered_request_and_returns_json(self):
        client = client_with_payload(TERM_STRUCTURE_PAYLOAD)
        result = client.get_term_structure(
            " AAPL ",
            snapshotTime="2026-05-13T16:30:00Z",
            expirationDateRange={
                "startDate": "2026-05-16",
                "endDate": "2026-06-20",
            },
            deltaRange={"min": 0.3, "max": 0.7},
        )
        self.assertEqual(result, TERM_STRUCTURE_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/term-structure",
            json={
                "snapshotTime": "2026-05-13T16:30:00Z",
                "filter": {
                    "ticker": "AAPL",
                    "expirationDateRange": {
                        "startDate": "2026-05-16",
                        "endDate": "2026-06-20",
                    },
                    "deltaRange": {"min": 0.3, "max": 0.7},
                },
            },
            timeout=30,
        )

    def test_flattens_contract_cells_and_repeats_stock_price(self):
        columns = [
            "expirationDate",
            "strikePrice",
            "contractType",
            "delta",
            "iv",
            "moneyType",
            "stockPrice",
        ]
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(TERM_STRUCTURE_PAYLOAD, output_type=output_type)
                frame = client.get_term_structure("AAPL")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), columns)
                self.assertEqual(frame["contractType"].to_list(), ["CALL", "PUT"])
                self.assertEqual(frame["stockPrice"].to_list(), [218.45, 218.45])

    def test_typed_empty_and_selector_validation(self):
        empty = client_with_payload(
            {"stockPrice": 218.45, "data": {}},
            output_type="polars",
        ).get_term_structure("AAPL")
        self.assertEqual(empty.shape, (0, 7))
        self.assertEqual(empty.schema["moneyType"], pl.String)

        client = client_with_payload(TERM_STRUCTURE_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "mutually exclusive"):
            client.get_term_structure(
                "AAPL",
                sessionDate="2026-05-13",
                snapshotTime="2026-05-13T16:30:00Z",
            )
        client._session.post.assert_not_called()

    def test_rejects_malformed_cells(self):
        client = client_with_payload(
            {"stockPrice": 218.45, "data": {"2026-05-16": {"215.0": {"CALL": {}}}}}
        )
        with self.assertRaisesRegex(QuantDataClientError, "term structure response"):
            client.get_term_structure("AAPL")


class VolatilitySkewTests(unittest.TestCase):
    def test_posts_exact_filtered_request_and_returns_json(self):
        client = client_with_payload(VOLATILITY_SKEW_PAYLOAD)
        result = client.get_volatility_skew(
            " AAPL ",
            snapshotTime="2026-05-13T16:30:00Z",
            contractTypes=["call"],
            expirationDate="2026-05-16",
        )
        self.assertEqual(result, VOLATILITY_SKEW_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/volatility-skew",
            json={
                "snapshotTime": "2026-05-13T16:30:00Z",
                "filter": {
                    "ticker": "AAPL",
                    "contractTypes": ["CALL"],
                    "expirationDate": "2026-05-16",
                },
            },
            timeout=30,
        )

    def test_flattens_iv_leaves_and_repeats_stock_price(self):
        columns = [
            "expirationDate",
            "strikePrice",
            "contractType",
            "impliedVolatility",
            "stockPrice",
        ]
        for output_type, frame_type in (
            ("pandas", pd.DataFrame),
            ("polars", pl.DataFrame),
        ):
            with self.subTest(output_type=output_type):
                client = client_with_payload(
                    VOLATILITY_SKEW_PAYLOAD,
                    output_type=output_type,
                )
                frame = client.get_volatility_skew("AAPL")
                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), columns)
                self.assertEqual(
                    frame["contractType"].to_list(),
                    ["CALL", "PUT", "CALL"],
                )
                self.assertEqual(frame["stockPrice"].to_list(), [218.45] * 3)

    def test_documented_empty_and_selector_validation(self):
        empty = client_with_payload(
            {"stockPrice": 0.0, "data": {}},
            output_type="polars",
        ).get_volatility_skew("AAPL")
        self.assertEqual(empty.shape, (0, 5))
        self.assertEqual(empty.schema["impliedVolatility"], pl.Float64)

        client = client_with_payload(VOLATILITY_SKEW_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "mutually exclusive"):
            client.get_volatility_skew(
                "AAPL",
                sessionDate="2026-05-13",
                snapshotTime="2026-05-13T16:30:00Z",
            )
        client._session.post.assert_not_called()

    def test_rejects_malformed_leaves(self):
        client = client_with_payload(
            {"stockPrice": 218.45, "data": {"2026-05-16": {"215.0": {"OTHER": 0.2}}}}
        )
        with self.assertRaisesRegex(QuantDataClientError, "volatility skew response"):
            client.get_volatility_skew("AAPL")


class OpenInterestChangeTests(unittest.TestCase):
    def test_posts_exact_request_and_returns_complete_json_page(self):
        client = client_with_payload(OPEN_INTEREST_CHANGE_PAGE)
        result = client.get_open_interest_change(
            sessionDate="2026-05-13",
            size=50,
            searchAfter=["18000", "prior-id"],
            sortField="changeInOpenInterest",
            sortDirection="descending",
            includes=["TICKER", "CHANGE_IN_OPEN_INTEREST"],
            tickers=["AAPL", "NVDA"],
            contractTypes=["CALL"],
            strikePriceRange={"min": 200.0, "max": 250.0},
            expirationDateRange={"startDate": "2026-05-16", "endDate": "2026-06-20"},
            changeInOpenInterestRange={"min": 5_000, "max": None},
            percentChangeInOpenInterestRange={"min": 0.05, "max": None},
            filterExpression={"field": "currentOpenInterest", "gte": 1_000},
        )
        self.assertEqual(result, OPEN_INTEREST_CHANGE_PAGE)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/open-interest-change",
            json={
                "sessionDate": "2026-05-13",
                "size": 50,
                "searchAfter": ["18000", "prior-id"],
                "sort": {
                    "field": "changeInOpenInterest",
                    "direction": "DESCENDING",
                },
                "includes": ["TICKER", "CHANGE_IN_OPEN_INTEREST"],
                "filter": {
                    "tickers": ["AAPL", "NVDA"],
                    "contractTypes": ["CALL"],
                    "strikePriceRange": {"min": 200.0, "max": 250.0},
                    "expirationDateRange": {
                        "startDate": "2026-05-16",
                        "endDate": "2026-06-20",
                    },
                    "changeInOpenInterestRange": {"min": 5_000},
                    "percentChangeInOpenInterestRange": {"min": 0.05},
                },
                "filterExpression": {
                    "field": "currentOpenInterest",
                    "gte": 1_000,
                },
            },
            timeout=30,
        )

    def test_validates_page_size_data_and_cursor(self):
        client = client_with_payload(OPEN_INTEREST_CHANGE_PAGE)
        with self.assertRaisesRegex(ValueError, "between 1 and 100"):
            client.get_open_interest_change(size=101)
        with self.assertRaisesRegex(ValueError, "strikePrices.*strikePriceRange"):
            client.get_open_interest_change(
                strikePrices=[215.0],
                strikePriceRange={"min": 210.0, "max": 220.0},
            )
        with self.assertRaisesRegex(
            ValueError,
            "expirationDates.*expirationDateRange",
        ):
            client.get_open_interest_change(
                expirationDates=["2026-05-16"],
                expirationDateRange={
                    "startDate": "2026-05-16",
                    "endDate": "2026-06-20",
                },
            )
        client._session.post.assert_not_called()

        for payload in ({"data": {}}, {"data": [], "nextSearchAfter": "bad"}):
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(
                    QuantDataClientError,
                    "open interest change response",
                ):
                    client_with_payload(payload).get_open_interest_change()

    def test_accepts_omitted_or_null_cursor(self):
        self.assertEqual(
            client_with_payload({"data": []}).get_open_interest_change(),
            {"data": []},
        )
        self.assertEqual(
            client_with_payload(
                {"data": [], "nextSearchAfter": None}
            ).get_open_interest_change(),
            {"data": [], "nextSearchAfter": None},
        )

    def test_rejects_dataframe_output_before_transport(self):
        client = client_with_payload(OPEN_INTEREST_CHANGE_PAGE, output_type="pandas")
        with self.assertRaisesRegex(
            QuantDataConfigurationError,
            "only supports JSON output",
        ):
            client.get_open_interest_change()
        client._session.post.assert_not_called()


class OrderFlowConsolidatedTests(unittest.TestCase):
    def test_posts_exact_time_range_filter_request_and_preserves_page(self):
        client = client_with_payload(ORDER_FLOW_CONSOLIDATED_PAGE)
        result = client.get_order_flow_consolidated(
            startTime="2026-05-13T13:30:00Z",
            endTime="2026-05-13T14:30:00Z",
            size=100,
            searchAfter=["1747137600000", "prior-id"],
            sortField="tradeTime",
            sortDirection="descending",
            includes=["ID", "TICKER", "PREMIUM"],
            includeComprisingTrades=True,
            includeStatistics=True,
            ticker="AAPL",
            contractTypes=["call"],
            premiumRange={"min": 1_000_000},
            tradeConsolidationTypes=["SWEEP"],
            isGoldenSweep=False,
            deltaRange={"min": 0.5},
            filterExpression={"field": "isUnusual", "eq": True},
        )
        self.assertEqual(result, ORDER_FLOW_CONSOLIDATED_PAGE)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/order-flow/consolidated",
            json={
                "timeRange": {
                    "startTime": "2026-05-13T13:30:00Z",
                    "endTime": "2026-05-13T14:30:00Z",
                },
                "size": 100,
                "searchAfter": ["1747137600000", "prior-id"],
                "sort": {"field": "tradeTime", "direction": "DESCENDING"},
                "includes": ["ID", "TICKER", "PREMIUM"],
                "includeComprisingTrades": True,
                "includeStatistics": True,
                "filter": {
                    "ticker": "AAPL",
                    "contractTypes": ["CALL"],
                    "premiumRange": {"min": 1_000_000},
                    "tradeConsolidationTypes": ["SWEEP"],
                    "isGoldenSweep": False,
                    "deltaRange": {"min": 0.5},
                },
                "filterExpression": {"field": "isUnusual", "eq": True},
            },
            timeout=30,
        )

    def test_validates_selector_size_and_page_shape(self):
        client = client_with_payload(ORDER_FLOW_CONSOLIDATED_PAGE)
        with self.assertRaisesRegex(ValueError, "mutually exclusive"):
            client.get_order_flow_consolidated(
                sessionDate="2026-05-13",
                startTime="2026-05-13T13:30:00Z",
                endTime="2026-05-13T14:30:00Z",
            )
        with self.assertRaisesRegex(ValueError, "between 1 and 100"):
            client.get_order_flow_consolidated(size=101)
        client._session.post.assert_not_called()

        for payload in ({"data": {}}, {"data": [], "nextSearchAfter": {}}):
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(
                    QuantDataClientError,
                    "order flow consolidated response",
                ):
                    client_with_payload(payload).get_order_flow_consolidated()

    def test_accepts_optional_statistics_and_cursor_variants(self):
        for payload in (
            {"data": []},
            {"data": [], "nextSearchAfter": None},
            {"data": [], "statistics": None},
            {"data": [], "statistics": {}},
        ):
            with self.subTest(payload=payload):
                self.assertEqual(
                    client_with_payload(payload).get_order_flow_consolidated(),
                    payload,
                )

    def test_rejects_dataframe_output_before_transport(self):
        client = client_with_payload(
            ORDER_FLOW_CONSOLIDATED_PAGE,
            output_type="polars",
        )
        with self.assertRaisesRegex(
            QuantDataConfigurationError,
            "only supports JSON output",
        ):
            client.get_order_flow_consolidated()
        client._session.post.assert_not_called()


class OrderFlowUnconsolidatedTests(unittest.TestCase):
    def test_posts_exact_session_filter_request_and_preserves_page(self):
        client = client_with_payload(ORDER_FLOW_UNCONSOLIDATED_PAGE)
        result = client.get_order_flow_unconsolidated(
            sessionDate="2026-05-13",
            size=1_000,
            searchAfter=["1747137600000", "prior-id"],
            sortField="tradeTime",
            sortDirection="ascending",
            excludes=["GREEKS"],
            includeStatistics=True,
            osi="AAPL260516C00220000",
            premiumRange={"min": 10_000},
            isUnusual=False,
            isCancelled=False,
            vannaRange={"min": -0.2, "max": 0.2},
            filterExpression={"field": "tradeSideCode", "eq": "ABOVE_ASK"},
        )
        self.assertEqual(result, ORDER_FLOW_UNCONSOLIDATED_PAGE)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/options/tool/order-flow/unconsolidated",
            json={
                "sessionDate": "2026-05-13",
                "size": 1_000,
                "searchAfter": ["1747137600000", "prior-id"],
                "sort": {"field": "tradeTime", "direction": "ASCENDING"},
                "excludes": ["GREEKS"],
                "includeStatistics": True,
                "filter": {
                    "osi": "AAPL260516C00220000",
                    "premiumRange": {"min": 10_000},
                    "isUnusual": False,
                    "isCancelled": False,
                    "vannaRange": {"min": -0.2, "max": 0.2},
                },
                "filterExpression": {
                    "field": "tradeSideCode",
                    "eq": "ABOVE_ASK",
                },
            },
            timeout=30,
        )

    def test_validates_max_size_page_shape_and_endpoint_specific_filters(self):
        client = client_with_payload(ORDER_FLOW_UNCONSOLIDATED_PAGE)
        with self.assertRaisesRegex(ValueError, "between 1 and 1000"):
            client.get_order_flow_unconsolidated(size=1_001)
        with self.assertRaisesRegex(TypeError, "not supported"):
            client.get_order_flow_unconsolidated(isGoldenSweep=True)
        client._session.post.assert_not_called()

        for payload in (
            {"data": "bad"},
            {"data": [], "nextSearchAfter": "bad"},
            {"data": [], "statistics": []},
        ):
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(
                    QuantDataClientError,
                    "order flow unconsolidated response",
                ):
                    client_with_payload(payload).get_order_flow_unconsolidated()

    def test_accepts_optional_statistics_and_cursor_variants(self):
        for payload in (
            {"data": []},
            {"data": [], "nextSearchAfter": None},
            {"data": [], "statistics": None},
            {"data": [], "statistics": {}},
        ):
            with self.subTest(payload=payload):
                self.assertEqual(
                    client_with_payload(payload).get_order_flow_unconsolidated(),
                    payload,
                )

    def test_rejects_dataframe_output_before_transport(self):
        client = client_with_payload(
            ORDER_FLOW_UNCONSOLIDATED_PAGE,
            output_type="pandas",
        )
        with self.assertRaisesRegex(
            QuantDataConfigurationError,
            "only supports JSON output",
        ):
            client.get_order_flow_unconsolidated()
        client._session.post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
