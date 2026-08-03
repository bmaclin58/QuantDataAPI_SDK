from datetime import date, datetime, timezone
import inspect
import unittest
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pandas as pd
import polars as pl

from QuantDataAPI.client import QuantDataAPI_Client
from QuantDataAPI.errors import QuantDataClientError, QuantDataConfigurationError


DARK_POOL_PAYLOAD = {
    "latestStockPrice": 218.42,
    "data": {
        "215.00": {
            "notionalValue": 18_420_100.0,
            "size": 85_675,
            "tradeCount": 612,
        },
        "210.00": {
            "notionalValue": 4_820_100.0,
            "size": 22_950,
            "tradeCount": 184,
        },
    },
}


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.headers = {}
        self.text = ""

    def json(self):
        return self._payload


class ClientConfigurationTests(unittest.TestCase):
    def test_client_is_exported_from_package_root(self):
        from QuantDataAPI import QuantDataAPI_Client as ExportedClient

        self.assertIs(ExportedClient, QuantDataAPI_Client)

    def test_constructor_normalizes_output_and_configures_transport(self):
        client = QuantDataAPI_Client("test-key", output_type=" Polars ")

        self.assertEqual(client.output_type, "polars")
        self.assertEqual(
            client._session.headers["Authorization"],
            "Bearer test-key",
        )
        retry = client._session.get_adapter("https://").max_retries
        self.assertEqual(retry.total, 2)
        self.assertEqual(retry.allowed_methods, frozenset({"POST"}))
        self.assertTrue({429, 500, 502, 503, 504}.issubset(retry.status_forcelist))
        self.assertTrue(retry.respect_retry_after_header)

    def test_constructor_exposes_approved_keyword_order(self):
        parameters = list(inspect.signature(QuantDataAPI_Client).parameters)

        self.assertEqual(
            parameters,
            [
                "api_key",
                "output_type",
                "timezone",
                "convertTimezone",
                "base_url",
                "timeout",
            ],
        )

    def test_constructor_rejects_invalid_configuration(self):
        cases = (
            ({"api_key": " "}, "api_key"),
            ({"api_key": "key", "output_type": "xml"}, "output_type"),
            ({"api_key": "key", "timezone": "Not/A_Zone"}, "timezone"),
            ({"api_key": "key", "convertTimezone": 1}, "convertTimezone"),
            ({"api_key": "key", "timeout": 0}, "timeout"),
        )

        for kwargs, field in cases:
            with self.subTest(field=field):
                with self.assertRaisesRegex(QuantDataConfigurationError, field):
                    QuantDataAPI_Client(**kwargs)


class ClientTimezoneTests(unittest.TestCase):
    def test_request_times_use_configured_timezone_and_dst(self):
        client = QuantDataAPI_Client("key", timezone="America/New_York")
        values = client._serialize_request_value(
            {
                "winter": datetime(2026, 1, 5, 9, 30),
                "summer": "2026-07-05T09:30:00",
                "snapshotTime": "2026-05-13 20:00",
                "aware": datetime(2026, 7, 5, 13, 30, tzinfo=timezone.utc),
                "date": date(2026, 7, 5),
                "ticker": "AAPL",
            }
        )

        self.assertEqual(values["winter"], "2026-01-05T14:30:00Z")
        self.assertEqual(values["summer"], "2026-07-05T13:30:00Z")
        self.assertEqual(values["snapshotTime"], "2026-05-14T00:00:00Z")
        self.assertEqual(values["aware"], "2026-07-05T13:30:00Z")
        self.assertEqual(values["date"], "2026-07-05")
        self.assertEqual(values["ticker"], "AAPL")

    def test_json_response_converts_only_utc_timestamps(self):
        client = QuantDataAPI_Client("key", timezone="America/New_York")
        payload = {
            "createdAt": "2026-07-05T13:30:00Z",
            "nested": ["2026-01-05T14:30:00+00:00", "AAPL", "2026-07-05"],
        }

        result = client._format_response(payload, rows=[])

        self.assertEqual(result["createdAt"], "2026-07-05T09:30:00-04:00")
        self.assertEqual(result["nested"][0], "2026-01-05T09:30:00-05:00")
        self.assertEqual(result["nested"][1:], ["AAPL", "2026-07-05"])

    def test_convert_timezone_false_preserves_values(self):
        client = QuantDataAPI_Client("key", convertTimezone=False)
        request = client._serialize_request_value(
            {
                "naive": datetime(2026, 7, 5, 9, 30),
                "local": "2026-05-13 20:00",
                "text": "2026-07-05T13:30:00Z",
            }
        )
        response = client._format_response(
            {"time": "2026-07-05T13:30:00Z"},
            rows=[],
        )

        self.assertEqual(request["naive"], "2026-07-05T09:30:00")
        self.assertEqual(request["local"], "2026-05-13 20:00")
        self.assertEqual(request["text"], "2026-07-05T13:30:00Z")
        self.assertEqual(response["time"], "2026-07-05T13:30:00Z")

    def test_dataframe_outputs_use_timezone_aware_datetimes(self):
        for output_type in ("pandas", "polars"):
            with self.subTest(output_type=output_type):
                client = QuantDataAPI_Client("key", output_type=output_type)
                frame = client._format_response(
                    {},
                    rows=[{"timestamp": "2026-07-05T13:30:00Z"}],
                )

                self.assertEqual(frame["timestamp"][0].hour, 9)
                self.assertIn("America/New_York", str(frame["timestamp"].dtype))

    def test_timestamp_schema_adds_native_datetime_column(self):
        for output_type in ("pandas", "polars"):
            with self.subTest(output_type=output_type):
                client = QuantDataAPI_Client("key", output_type=output_type)
                frame = client._format_response(
                    {},
                    rows=[
                        {"timestamp": 1785124800000, "price": 1.0},
                        {"timestamp": 1785182400000, "price": 2.0},
                    ],
                    schema={"timestamp": int, "price": float},
                )

                self.assertEqual(
                    list(frame.columns),
                    ["timestamp", "ConvertedDateTime", "price"],
                )
                self.assertEqual(
                    frame["ConvertedDateTime"].to_list(),
                    [
                        datetime(
                            2026,
                            7,
                            27,
                            tzinfo=ZoneInfo("America/New_York"),
                        ),
                        datetime(
                            2026,
                            7,
                            27,
                            16,
                            tzinfo=ZoneInfo("America/New_York"),
                        ),
                    ],
                )
                if output_type == "pandas":
                    self.assertIsInstance(
                        frame["ConvertedDateTime"].dtype,
                        pd.DatetimeTZDtype,
                    )
                else:
                    self.assertEqual(
                        frame.schema["ConvertedDateTime"],
                        pl.Datetime("us", "America/New_York"),
                    )

    def test_timestamp_schema_uses_utc_when_conversion_is_disabled(self):
        for output_type in ("pandas", "polars"):
            with self.subTest(output_type=output_type):
                client = QuantDataAPI_Client(
                    "key",
                    output_type=output_type,
                    convertTimezone=False,
                )
                frame = client._format_response(
                    {},
                    rows=[{"timestamp": 1785124800000}],
                    schema={"timestamp": int},
                )

                self.assertEqual(
                    frame["ConvertedDateTime"].to_list(),
                    [datetime(2026, 7, 27, 4, tzinfo=timezone.utc)],
                )

    def test_timestamp_schema_rejects_out_of_range_epoch(self):
        client = QuantDataAPI_Client("key", output_type="pandas")

        with self.assertRaisesRegex(
            QuantDataClientError,
            "timestamp must be valid Unix milliseconds",
        ):
            client._format_response(
                {},
                rows=[{"timestamp": 10**30}],
                schema={"timestamp": int},
            )


class DarkPoolLevelsTests(unittest.TestCase):
    def _client_with_response(self, output_type="json", payload=None):
        client = QuantDataAPI_Client("key", output_type=output_type, timeout=12)
        client._session.post = Mock(
            return_value=FakeResponse(DARK_POOL_PAYLOAD if payload is None else payload)
        )
        return client

    def test_dark_pool_levels_posts_exact_request_and_returns_json(self):
        client = self._client_with_response()

        result = client.get_dark_pool_levels(
            ticker=" AAPL ",
            startDate=date(2026, 7, 5),
        )

        self.assertEqual(result, DARK_POOL_PAYLOAD)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/equities/tool/dark-pool-levels",
            json={
                "sessionDateRange": {"startDate": "2026-07-05"},
                "filter": {"ticker": "AAPL"},
            },
            timeout=12,
        )

    def test_dark_pool_levels_returns_typed_dataframes(self):
        expected_columns = [
            "priceLevel",
            "notionalValue",
            "size",
            "tradeCount",
            "latestStockPrice",
        ]

        for output_type, frame_type in (("pandas", pd.DataFrame), ("polars", pl.DataFrame)):
            with self.subTest(output_type=output_type):
                client = self._client_with_response(output_type)
                frame = client.get_dark_pool_levels("AAPL", "2026-07-05")

                self.assertIsInstance(frame, frame_type)
                self.assertEqual(list(frame.columns), expected_columns)
                self.assertEqual(frame["priceLevel"].to_list(), [210.0, 215.0])
                self.assertEqual(frame["latestStockPrice"].to_list(), [218.42, 218.42])
                self.assertTrue(str(frame["priceLevel"].dtype).lower().endswith("64"))
                self.assertTrue(str(frame["size"].dtype).lower().endswith("64"))

    def test_dark_pool_levels_returns_typed_empty_dataframe(self):
        client = self._client_with_response(
            "polars",
            payload={"latestStockPrice": 218.42, "data": {}},
        )

        frame = client.get_dark_pool_levels("AAPL", "2026-07-05")

        self.assertEqual(frame.shape, (0, 5))
        self.assertEqual(frame.schema["priceLevel"], pl.Float64)
        self.assertEqual(frame.schema["size"], pl.Int64)

    def test_dark_pool_levels_rejects_malformed_success_payload(self):
        client = self._client_with_response(payload={"data": {"210.00": {}}})

        with self.assertRaisesRegex(QuantDataClientError, "dark-pool levels response"):
            client.get_dark_pool_levels("AAPL", "2026-07-05")

    def test_dark_pool_levels_rejects_blank_ticker(self):
        client = self._client_with_response()

        with self.assertRaisesRegex(ValueError, "ticker"):
            client.get_dark_pool_levels(" ", "2026-07-05")

        client._session.post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
