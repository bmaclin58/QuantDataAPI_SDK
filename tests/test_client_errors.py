import importlib
import unittest

from QuantDataAPI.errors import (
    QuantDataAuthenticationError,
    QuantDataAuthorizationError,
    QuantDataBadRequestError,
    QuantDataDataUnavailableError,
    QuantDataHttpError,
    QuantDataInternalError,
    QuantDataOpraAgreementRequiredError,
    QuantDataRateLimitError,
    QuantDataValidationError,
)


class FakeResponse:
    def __init__(self, status_code, problem):
        self.status_code = status_code
        self._problem = problem
        self.headers = {"X-Test": "value"}
        self.text = "fallback response text"

    def json(self):
        return self._problem


class ClientImportTests(unittest.TestCase):
    def test_client_module_imports(self):
        importlib.import_module("QuantDataAPI.client")


class ClientErrorRoutingTests(unittest.TestCase):
    def test_routes_documented_problem_types_to_specific_errors(self):
        from QuantDataAPI.client import QuantDataAPI_Client

        cases = (
            ("validation", 400, QuantDataValidationError),
            ("bad-request", 400, QuantDataBadRequestError),
            ("authentication", 401, QuantDataAuthenticationError),
            ("authorization", 403, QuantDataAuthorizationError),
            ("opra-agreement-required", 403, QuantDataOpraAgreementRequiredError),
            ("data-unavailable", 422, QuantDataDataUnavailableError),
            ("rate-limit-exceeded", 429, QuantDataRateLimitError),
            ("internal", 500, QuantDataInternalError),
        )
        client = QuantDataAPI_Client("test-key")

        for category, status_code, expected_error in cases:
            with self.subTest(category=category):
                problem = {
                    "type": f"https://quantdata.us/errors/{category}",
                    "status": status_code,
                    "detail": f"{category} detail",
                }
                with self.assertRaises(expected_error) as caught:
                    client._handle(FakeResponse(status_code, problem))

                self.assertIs(caught.exception.problem, problem)
                self.assertEqual(caught.exception.headers, {"X-Test": "value"})
                self.assertEqual(caught.exception.detail, problem["detail"])

    def test_unknown_problem_type_uses_generic_http_error(self):
        from QuantDataAPI.client import QuantDataAPI_Client

        problem = {
            "type": "https://quantdata.us/errors/future-category",
            "status": 418,
            "detail": "Future error",
        }

        with self.assertRaises(QuantDataHttpError) as caught:
            QuantDataAPI_Client("test-key")._handle(FakeResponse(418, problem))

        self.assertIs(type(caught.exception), QuantDataHttpError)
        self.assertIs(caught.exception.problem, problem)


if __name__ == "__main__":
    unittest.main()
