"""

https://quantdata.us/api/docs/errors
"""
from typing import Any


class QuantDataClientError(Exception):
    """Base error for QuantData request failures."""


class QuantDataConfigurationError(QuantDataClientError):
    """Raised when required QuantData settings are missing."""


class QuantDataHttpError(QuantDataClientError):
    problem_type: str | None = None
    default_status_code: int | None = None

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        headers: dict[str, Any] | None = None,
        problem: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.headers = headers if headers is not None else {}
        self.problem = problem if problem is not None else {}
        self.type = self.problem.get("type", self.problem_type)
        self.title = self.problem.get("title")
        self.status = self.problem.get("status", status_code)
        self.detail = self.problem.get("detail", message)
        self.instance = self.problem.get("instance")


class QuantDataValidationError(QuantDataHttpError):
    problem_type = "https://quantdata.us/errors/validation"
    default_status_code = 400

    @property
    def errors(self) -> list[dict[str, Any]]:
        return self.problem.get("errors", [])


class QuantDataBadRequestError(QuantDataHttpError):
    problem_type = "https://quantdata.us/errors/bad-request"
    default_status_code = 400


class QuantDataAuthenticationError(QuantDataHttpError):
    problem_type = "https://quantdata.us/errors/authentication"
    default_status_code = 401


class QuantDataAuthorizationError(QuantDataHttpError):
    problem_type = "https://quantdata.us/errors/authorization"
    default_status_code = 403


class QuantDataOpraAgreementRequiredError(QuantDataHttpError):
    problem_type = "https://quantdata.us/errors/opra-agreement-required"
    default_status_code = 403

    @property
    def agreement_url(self) -> str | None:
        return self.problem.get("agreementUrl")


class QuantDataDataUnavailableError(QuantDataHttpError):
    problem_type = "https://quantdata.us/errors/data-unavailable"
    default_status_code = 422


class QuantDataRateLimitError(QuantDataHttpError):
    problem_type = "https://quantdata.us/errors/rate-limit-exceeded"
    default_status_code = 429

    @property
    def limit(self) -> int | None:
        return self.problem.get("limit")

    @property
    def window_seconds(self) -> int | None:
        return self.problem.get("windowSeconds")

    @property
    def burst_limit(self) -> int | None:
        return self.problem.get("burstLimit")

    @property
    def burst_window_seconds(self) -> int | None:
        return self.problem.get("burstWindowSeconds")

    @property
    def retry_after_seconds(self) -> int | None:
        return self.problem.get("retryAfterSeconds")


class QuantDataInternalError(QuantDataHttpError):
    problem_type = "https://quantdata.us/errors/internal"
    default_status_code = 500
