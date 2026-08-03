import importlib
import unittest
from unittest.mock import MagicMock, patch

import polars as pl
import QuantDataAPI


EXPECTED_COLUMNS = [
    "askPrice",
    "bidAskSpread",
    "bidPrice",
    "contractType",
    "expirationDate",
    "dte",
    "greek_charm",
    "greek_color",
    "greek_delta",
    "greek_gamma",
    "greek_omega",
    "greek_rho",
    "greek_sigma",
    "greek_speed",
    "greek_theta",
    "greek_ultima",
    "greek_vanna",
    "greek_vega",
    "greek_veta",
    "greek_vomma",
    "greek_zomma",
    "impliedVolatility",
    "isGoldenSweep",
    "isOpeningPosition",
    "isUnusual",
    "isVolumeGreaterThanOpenInterest",
    "moneyness_degree",
    "moneyness_degreeInPercent",
    "moneyness_moneyType",
    "openInterest",
    "optionPrice",
    "premium",
    "sentimentType",
    "size",
    "stockPrice",
    "strikePrice",
    "tradeConsolidationType",
    "tradeTime",
    "tradeType",
    "volume",
]


def import_target():
    client = MagicMock()
    client.get_order_flow_consolidated.return_value = {
        "data": [],
        "nextSearchAfter": None,
    }
    with patch.object(QuantDataAPI, "QuantDataAPI_Client", return_value=client):
        return importlib.import_module("src.Research.populateDuckDB")


class PopulateDuckDBTests(unittest.TestCase):
    def test_rows_to_dataframe_flattens_fields_and_converts_trade_time(self):
        module = import_target()
        self.assertTrue(hasattr(module, "rows_to_dataframe"))
        frame = module.rows_to_dataframe(
            [
                {
                    "askPrice": 0.75,
                    "bidAskSpread": 0.1,
                    "bidPrice": 0.65,
                    "contractType": "CALL",
                    "expirationDate": "2026-07-27",
                    "dte": 0.07918981481481481,
                    "greeks": {
                        "charm": -1.351836460212895,
                        "color": -1.4191783744972009,
                        "delta": 0.0837116361850721,
                        "gamma": 0.008374124893420454,
                        "omega": 880.6677502202508,
                        "rho": 0.0013441665519043963,
                        "sigma": 0.16832351684570312,
                        "speed": 0.0006281851048530003,
                        "theta": -17.928145909654766,
                        "ultima": -12.340156901672016,
                        "vanna": 0.012639777925801706,
                        "vega": 0.16789165866754988,
                        "veta": 3.0968317506351934,
                        "vomma": 190.43991965084874,
                        "zomma": 0.04523772596269477,
                    },
                    "impliedVolatility": 16.832351684570312,
                    "isGoldenSweep": False,
                    "isOpeningPosition": False,
                    "isUnusual": False,
                    "isVolumeGreaterThanOpenInterest": True,
                    "moneyness": {
                        "degree": 25.58,
                        "degreeInPercent": 0.3452361993246435,
                        "moneyType": "OUT_OF_THE_MONEY",
                    },
                    "openInterest": 563,
                    "optionPrice": 0.69,
                    "premium": 16447.0,
                    "sentimentType": "BEARISH",
                    "size": 235,
                    "stockPrice": 7409.42,
                    "strikePrice": 7435.0,
                    "tradeConsolidationType": "SPLIT",
                    "tradeTime": 1785179157543,
                    "tradeType": "MULTI_AUTO_COB",
                    "volume": 56699,
                    "exchange": "CBOE",
                },
                {"tradeTime": None},
            ]
        )

        self.assertEqual(frame.columns, EXPECTED_COLUMNS)
        self.assertEqual(frame.shape, (2, 40))
        self.assertEqual(frame["greek_color"][0], -1.4191783744972009)
        self.assertEqual(frame["moneyness_moneyType"][0], "OUT_OF_THE_MONEY")
        self.assertEqual(
            frame["tradeTime"].dtype,
            pl.Datetime("ms", "America/New_York"),
        )
        self.assertEqual(
            frame["tradeTime"][0].isoformat(),
            "2026-07-27T15:05:57.543000-04:00",
        )
        self.assertIsNone(frame["greek_color"][1])

    def test_rows_to_dataframe_preserves_columns_when_empty(self):
        module = import_target()
        self.assertTrue(hasattr(module, "rows_to_dataframe"))
        frame = module.rows_to_dataframe([])

        self.assertEqual(frame.columns, EXPECTED_COLUMNS)
        self.assertEqual(frame.shape, (0, 40))


if __name__ == "__main__":
    unittest.main()
