from datetime import datetime
from inspect import signature
import unittest

from QuantDataAPI import validationChecks
from QuantDataAPI.errors import QuantDataConfigurationError
from QuantDataAPI.filterOptions import add_pagination, add_session_or_time_range
from tests.endpoint_test_support import client_with_payload


class SharedEndpointFrameworkTests(unittest.TestCase):
    def test_non_empty_string_validation(self):
        validator = getattr(validationChecks, "validate_non_empty_string", None)
        self.assertIsNotNone(validator)
        self.assertEqual(validator("ticker", " AAPL "), "AAPL")
        for value in (None, "", "   ", 123):
            with self.subTest(value=value), self.assertRaises((TypeError, ValueError)):
                validator("ticker", value)

    def test_time_range_uses_client_timezone_at_transport_boundary(self):
        body = {}
        start = datetime(2026, 7, 5, 9, 30)
        end = datetime(2026, 7, 5, 10, 0)
        add_session_or_time_range(body, startTime=start, endTime=end)

        self.assertIs(body["timeRange"]["startTime"], start)
        client = client_with_payload({"data": {}}, timezone="America/Chicago")
        client._post("/test", body)

        request = client._session.post.call_args.kwargs["json"]
        self.assertEqual(
            request["timeRange"]["startTime"],
            "2026-07-05T14:30:00Z",
        )

    def test_paginated_guard_rejects_dataframe_output_before_post(self):
        client = client_with_payload({"data": []}, output_type="pandas")
        guard = getattr(client, "_require_json_output", None)
        self.assertIsNotNone(guard)

        with self.assertRaisesRegex(QuantDataConfigurationError, "JSON"):
            guard("Equity Prints")

        client._session.post.assert_not_called()

    def test_pagination_rejects_non_integer_page_sizes(self):
        for value in (True, "50", 1.5):
            with self.subTest(value=value), self.assertRaises(TypeError):
                add_pagination({}, size=value)

    def test_all_time_range_endpoints_accept_local_datetime_strings(self):
        cases = {
            "get_contract_statistics": ({"data": {}}, (), {}),
            "get_contract_trade_side_statistics": (
                {"data": {}},
                ("PREMIUM",),
                {},
            ),
            "get_dark_flow": ({"data": {}}, ("AAPL",), {}),
            "get_equity_prints": ({"data": []}, (), {}),
            "get_exchange_notifications": ({"data": []}, (), {}),
            "get_gainers_losers": ({"data": {}}, (), {}),
            "get_interval_map": ({"data": {}}, ("SPY", "GAMMA"), {}),
            "get_market_share": ({"data": {}}, (), {}),
            "get_net_drift": ({"data": {}}, (), {}),
            "get_net_flow": ({"data": {}}, ("NET_PREMIUM",), {}),
            "get_news_articles": ({"data": []}, (), {}),
            "get_option_price_over_time": (
                {"data": {}},
                (),
                {"osi": "AAPL260516C00220000"},
            ),
            "get_order_flow_consolidated": ({"data": []}, (), {}),
            "get_order_flow_unconsolidated": ({"data": []}, (), {}),
            "get_stock_price_over_time": ({"data": {}}, ("AAPL",), {}),
        }
        inventory_client = client_with_payload({"data": {}})
        client_methods = {
            name
            for name in dir(inventory_client)
            if name.startswith("get_")
            and {"startTime", "endTime"}.issubset(
                signature(getattr(inventory_client, name)).parameters
            )
        }
        self.assertEqual(set(cases), client_methods)

        for method_name, (payload, args, kwargs) in cases.items():
            with self.subTest(endpoint=method_name):
                client = client_with_payload(payload)
                getattr(client, method_name)(
                    *args,
                    startTime="2026-05-13 20:00",
                    endTime="2026-05-13 21:00",
                    **kwargs,
                )
                request = client._session.post.call_args.kwargs["json"]
                self.assertEqual(
                    request["timeRange"],
                    {
                        "startTime": "2026-05-14T00:00:00Z",
                        "endTime": "2026-05-14T01:00:00Z",
                    },
                )


if __name__ == "__main__":
    unittest.main()
