import ast
import importlib
from pathlib import Path
import re
import unittest

from QuantDataAPI import utility
from QuantDataAPI.client import QuantDataAPI_Client


ROOT = Path(__file__).resolve().parents[1]

ENDPOINTS = {
    "Dark Flow": ("get_dark_flow", False),
    "Dark Pool Levels": ("get_dark_pool_levels", False),
    "Equity Prints": ("get_equity_prints", True),
    "Exchange Notifications": ("get_exchange_notifications", True),
    "Market Map": ("get_market_map", False),
    "Stock Price Over Time": ("get_stock_price_over_time", False),
    "Contract Statistics": ("get_contract_statistics", False),
    "Contract Trade Side Statistics": (
        "get_contract_trade_side_statistics",
        False,
    ),
    "Exposure By Expiration": ("get_exposure_by_expiration", False),
    "Exposure By Strike": ("get_exposure_by_strike", False),
    "Gainers / Losers": ("get_gainers_losers", False),
    "Heat Map": ("get_heat_map", False),
    "Interval Map": ("get_interval_map", False),
    "IV Rank": ("get_iv_rank", False),
    "Market Share": ("get_market_share", False),
    "Max Pain": ("get_max_pain", False),
    "Max Pain Over Time": ("get_max_pain_over_time", False),
    "Net Drift": ("get_net_drift", False),
    "Net Flow": ("get_net_flow", False),
    "Open Interest By Expiration": (
        "get_open_interest_by_expiration",
        False,
    ),
    "Open Interest By Strike": ("get_open_interest_by_strike", False),
    "Open Interest Change": ("get_open_interest_change", True),
    "Open Interest Over Time": ("get_open_interest_over_time", False),
    "Option Price Over Time": ("get_option_price_over_time", False),
    "Order Flow Consolidated": ("get_order_flow_consolidated", True),
    "Order Flow Unconsolidated": ("get_order_flow_unconsolidated", True),
    "Term Structure": ("get_term_structure", False),
    "Volatility Drift": ("get_volatility_drift", False),
    "Volatility Skew": ("get_volatility_skew", False),
    "News Articles": ("get_news_articles", True),
}

MODULES = {
    "Dark Flow": "QuantDataAPI.Equities.DarkFlow",
    "Dark Pool Levels": "QuantDataAPI.Equities.DarkPoolLevels",
    "Equity Prints": "QuantDataAPI.Equities.EquityPrints",
    "Exchange Notifications": "QuantDataAPI.Equities.ExchangeNotifications",
    "Market Map": "QuantDataAPI.Equities.MarketMap",
    "Stock Price Over Time": "QuantDataAPI.Equities.StockPriceOverTime",
    "Contract Statistics": "QuantDataAPI.OptionsEndpoint.ContractStatistics",
    "Contract Trade Side Statistics": "QuantDataAPI.OptionsEndpoint.ContractTradeSideStatistics",
    "Exposure By Expiration": "QuantDataAPI.OptionsEndpoint.ExposureByExpiration",
    "Exposure By Strike": "QuantDataAPI.OptionsEndpoint.ExposureByStrike",
    "Gainers / Losers": "QuantDataAPI.OptionsEndpoint.GainersLosers",
    "Heat Map": "QuantDataAPI.OptionsEndpoint.HeatMap",
    "Interval Map": "QuantDataAPI.OptionsEndpoint.IntervalMap",
    "IV Rank": "QuantDataAPI.OptionsEndpoint.IVRank",
    "Market Share": "QuantDataAPI.OptionsEndpoint.MarketShare",
    "Max Pain": "QuantDataAPI.OptionsEndpoint.MaxPain",
    "Max Pain Over Time": "QuantDataAPI.OptionsEndpoint.MaxPainOverTime",
    "Net Drift": "QuantDataAPI.OptionsEndpoint.NetDrift",
    "Net Flow": "QuantDataAPI.OptionsEndpoint.NetFlow",
    "Open Interest By Expiration": "QuantDataAPI.OptionsEndpoint.OpenInterestByExpiration",
    "Open Interest By Strike": "QuantDataAPI.OptionsEndpoint.OpenInterestByStrike",
    "Open Interest Change": "QuantDataAPI.OptionsEndpoint.OpenInterestChange",
    "Open Interest Over Time": "QuantDataAPI.OptionsEndpoint.OpenInterestOverTime",
    "Option Price Over Time": "QuantDataAPI.OptionsEndpoint.OptionPriceOverTime",
    "Order Flow Consolidated": "QuantDataAPI.OptionsEndpoint.OrderFlowConsolidated",
    "Order Flow Unconsolidated": "QuantDataAPI.OptionsEndpoint.OrderFlowUnconsolidated",
    "Term Structure": "QuantDataAPI.OptionsEndpoint.TermStructure",
    "Volatility Drift": "QuantDataAPI.OptionsEndpoint.VolatilityDrift",
    "Volatility Skew": "QuantDataAPI.OptionsEndpoint.VolatilitySkew",
    "News Articles": "QuantDataAPI.News.NewsArticles",
}

PAGINATED_METHOD_PATHS = {
    "get_equity_prints": utility.EQUITY_PRINTS,
    "get_exchange_notifications": utility.EXCHANGE_NOTIFICATIONS,
    "get_open_interest_change": utility.OPEN_INTEREST_CHANGE,
    "get_order_flow_consolidated": utility.ORDER_FLOW_CONSOLIDATED,
    "get_order_flow_unconsolidated": utility.ORDER_FLOW_UNCONSOLIDATED,
    "get_news_articles": utility.NEWS_ARTICLES,
}

METHOD_WIRE_CONSTANTS = {
    "get_dark_flow": ("DARK_FLOW", utility.DARK_FLOW),
    "get_dark_pool_levels": ("DARK_POOL_LEVELS", utility.DARK_POOL_LEVELS),
    "get_equity_prints": ("EQUITY_PRINTS", utility.EQUITY_PRINTS),
    "get_exchange_notifications": (
        "EXCHANGE_NOTIFICATIONS",
        utility.EXCHANGE_NOTIFICATIONS,
    ),
    "get_market_map": ("MARKET_MAP", utility.MARKET_MAP),
    "get_stock_price_over_time": (
        "STOCK_PRICE_OVER_TIME",
        utility.STOCK_PRICE_OVER_TIME,
    ),
    "get_contract_statistics": (
        "CONTRACT_STATISTICS",
        utility.CONTRACT_STATISTICS,
    ),
    "get_contract_trade_side_statistics": (
        "CONTRACT_TRADE_SIDE_STATISTICS",
        utility.CONTRACT_TRADE_SIDE_STATISTICS,
    ),
    "get_exposure_by_expiration": (
        "EXPOSURE_BY_EXPIRATION",
        utility.EXPOSURE_BY_EXPIRATION,
    ),
    "get_exposure_by_strike": (
        "EXPOSURE_BY_STRIKE",
        utility.EXPOSURE_BY_STRIKE,
    ),
    "get_gainers_losers": ("GAINERS_LOSERS", utility.GAINERS_LOSERS),
    "get_heat_map": ("HEAT_MAP", utility.HEAT_MAP),
    "get_interval_map": ("INTERVAL_MAP", utility.INTERVAL_MAP),
    "get_iv_rank": ("IV_RANK", utility.IV_RANK),
    "get_market_share": ("MARKET_SHARE", utility.MARKET_SHARE),
    "get_max_pain": ("MAX_PAIN", utility.MAX_PAIN),
    "get_max_pain_over_time": (
        "MAX_PAIN_OVER_TIME",
        utility.MAX_PAIN_OVER_TIME,
    ),
    "get_net_drift": ("NET_DRIFT", utility.NET_DRIFT),
    "get_net_flow": ("NET_FLOW", utility.NET_FLOW),
    "get_open_interest_by_expiration": (
        "OPEN_INTEREST_BY_EXPIRATION",
        utility.OPEN_INTEREST_BY_EXPIRATION,
    ),
    "get_open_interest_by_strike": (
        "OPEN_INTEREST_BY_STRIKE",
        utility.OPEN_INTEREST_BY_STRIKE,
    ),
    "get_open_interest_change": (
        "OPEN_INTEREST_CHANGE",
        utility.OPEN_INTEREST_CHANGE,
    ),
    "get_open_interest_over_time": (
        "OPEN_INTEREST_OVER_TIME",
        utility.OPEN_INTEREST_OVER_TIME,
    ),
    "get_option_price_over_time": (
        "OPTION_PRICE_OVER_TIME",
        utility.OPTION_PRICE_OVER_TIME,
    ),
    "get_order_flow_consolidated": (
        "ORDER_FLOW_CONSOLIDATED",
        utility.ORDER_FLOW_CONSOLIDATED,
    ),
    "get_order_flow_unconsolidated": (
        "ORDER_FLOW_UNCONSOLIDATED",
        utility.ORDER_FLOW_UNCONSOLIDATED,
    ),
    "get_term_structure": ("TERM_STRUCTURE", utility.TERM_STRUCTURE),
    "get_volatility_drift": (
        "VOLATILITY_DRIFT",
        utility.VOLATILITY_DRIFT,
    ),
    "get_volatility_skew": ("VOLATILITY_SKEW", utility.VOLATILITY_SKEW),
    "get_news_articles": ("NEWS_ARTICLES", utility.NEWS_ARTICLES),
}


def read_readme_sections() -> dict[str, str]:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    matches = list(re.finditer(r"^### \[([^]]+)]\([^\n]+\)\s*$", text, re.MULTILINE))
    return {
        match.group(1): text[
            match.start() : matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        ]
        for index, match in enumerate(matches)
    }


class ReadmeCoverageTests(unittest.TestCase):
    def test_all_endpoint_sections_have_examples_and_return_contracts(self):
        sections = read_readme_sections()
        self.assertEqual(set(sections), set(ENDPOINTS))

        for name, (method_name, paginated) in ENDPOINTS.items():
            with self.subTest(endpoint=name):
                section = sections[name]
                fence = re.search(r"```python\s*(.*?)```", section, re.DOTALL)
                self.assertIsNotNone(fence)
                example = fence.group(1)
                self.assertIn("QuantDataAPI_Client", example)
                self.assertIn(f"client.{method_name}(", example)
                if paginated:
                    self.assertIn("JSON only", section)
                    self.assertIn("searchAfter", section)
                    self.assertIn("nextSearchAfter", section)
                else:
                    self.assertIn("DataFrame columns:", section)


class EndpointInventoryTests(unittest.TestCase):
    def test_all_modules_methods_and_endpoint_test_classes_exist(self):
        self.assertEqual(set(MODULES), set(ENDPOINTS))
        self.assertEqual(len(MODULES), 30)

        for name, module_name in MODULES.items():
            with self.subTest(endpoint=name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)

                method_name = ENDPOINTS[name][0]
                self.assertTrue(callable(getattr(QuantDataAPI_Client, method_name)))
                endpoint_slug = method_name.removeprefix("get_")
                self.assertTrue(
                    callable(getattr(module, f"build_{endpoint_slug}_request"))
                )
                self.assertTrue(
                    callable(getattr(module, f"normalize_{endpoint_slug}"))
                )

                endpoint_class = f"{module_name.rsplit('.', 1)[1]}Tests"
                if name == "Dark Pool Levels":
                    test_module_name = "tests.test_client_framework"
                elif ".Equities." in module_name:
                    test_module_name = "tests.test_equities_endpoints"
                elif ".News." in module_name:
                    test_module_name = "tests.test_news_endpoints"
                else:
                    test_module_name = "tests.test_options_endpoints"
                test_module = importlib.import_module(test_module_name)
                self.assertTrue(
                    isinstance(getattr(test_module, endpoint_class), type),
                    f"Missing {test_module_name}.{endpoint_class}",
                )

    def test_29_new_modules_have_no_legacy_transport_or_placeholders(self):
        forbidden = re.compile(r"market_data\.services|query_quantdata|\bpass\b")
        scoped_modules = {
            name: module_name
            for name, module_name in MODULES.items()
            if name != "Dark Pool Levels"
        }
        self.assertEqual(len(scoped_modules), 29)

        for name, module_name in scoped_modules.items():
            with self.subTest(endpoint=name):
                module = importlib.import_module(module_name)
                source_path = Path(module.__file__)
                source = source_path.read_text(encoding="utf-8")
                self.assertIsNone(forbidden.search(source))

    def test_json_only_methods_and_paginated_paths_match_exactly(self):
        expected_methods = {
            method_name
            for method_name, paginated in ENDPOINTS.values()
            if paginated
        }
        self.assertEqual(set(PAGINATED_METHOD_PATHS), expected_methods)
        self.assertEqual(
            set(PAGINATED_METHOD_PATHS.values()),
            set(utility.PAGINATED_ENDPOINTS),
        )
        self.assertEqual(len(utility.PAGINATED_ENDPOINTS), 6)

        client_tree = ast.parse((ROOT / "src/QuantDataAPI/client.py").read_text())
        guarded_methods = {
            node.name
            for node in ast.walk(client_tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any(
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and call.func.attr == "_require_json_output"
                for call in ast.walk(node)
            )
        }
        self.assertEqual(guarded_methods, expected_methods)

    def test_every_public_method_posts_to_its_inventory_path(self):
        expected_methods = {method for method, _ in ENDPOINTS.values()}
        self.assertEqual(set(METHOD_WIRE_CONSTANTS), expected_methods)
        self.assertEqual(
            {path for _, path in METHOD_WIRE_CONSTANTS.values()},
            set(utility.ALL_ENDPOINTS),
        )

        client_tree = ast.parse((ROOT / "src/QuantDataAPI/client.py").read_text())
        methods = {
            node.name: node
            for node in ast.walk(client_tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        for method_name, (constant_name, _) in METHOD_WIRE_CONSTANTS.items():
            with self.subTest(method=method_name):
                post_calls = [
                    call
                    for call in ast.walk(methods[method_name])
                    if isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute)
                    and call.func.attr == "_post"
                ]
                self.assertEqual(len(post_calls), 1)
                self.assertIsInstance(post_calls[0].args[0], ast.Name)
                self.assertEqual(post_calls[0].args[0].id, constant_name)


if __name__ == "__main__":
    unittest.main()
