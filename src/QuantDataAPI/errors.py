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
        """Initialize an HTTP error from an RFC 9457 problem response.

        Args:
            status_code: HTTP response status used when `problem["status"]` is
                absent.
            message: Fallback exception message and `detail` value.
            headers: Response headers; defaults to an empty dictionary.
            problem: Parsed problem object; defaults to an empty dictionary.

        Returns:
            None. The instance exposes `status_code`, `headers`, `problem`, and
            the RFC 9457 `type`, `title`, `status`, `detail`, and `instance`
            fields. Optional fields are `None` when absent; `type`, `status`,
            and `detail` use the documented fallbacks above.

        Raises:
            AttributeError: If `problem` is not a dictionary-like object with
                a `get` method.
        """
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
        """Expose the problem `errors` extension.

        Returns:
            Field-level validation errors, or an empty list when `errors` is
            absent. An explicit JSON null is returned as `None`.
        """
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
        """Expose the problem `agreementUrl` extension.

        Returns:
            The OPRA agreement URL, or `None` when the field is absent or null.
        """
        return self.problem.get("agreementUrl")


class QuantDataDataUnavailableError(QuantDataHttpError):
    problem_type = "https://quantdata.us/errors/data-unavailable"
    default_status_code = 422


class QuantDataRateLimitError(QuantDataHttpError):
    problem_type = "https://quantdata.us/errors/rate-limit-exceeded"
    default_status_code = 429

    @property
    def limit(self) -> int | None:
        """Expose the problem `limit` extension.

        Returns:
            The sustained request limit, or `None` when the field is absent or
            null.
        """
        return self.problem.get("limit")

    @property
    def window_seconds(self) -> int | None:
        """Expose the problem `windowSeconds` extension.

        Returns:
            The sustained-limit window in seconds, or `None` when the field is
            absent or null.
        """
        return self.problem.get("windowSeconds")

    @property
    def burst_limit(self) -> int | None:
        """Expose the problem `burstLimit` extension.

        Returns:
            The burst request limit, or `None` when the field is absent or null.
        """
        return self.problem.get("burstLimit")

    @property
    def burst_window_seconds(self) -> int | None:
        """Expose the problem `burstWindowSeconds` extension.

        Returns:
            The burst-limit window in seconds, or `None` when the field is
            absent or null.
        """
        return self.problem.get("burstWindowSeconds")

    @property
    def retry_after_seconds(self) -> int | None:
        """Expose the problem `retryAfterSeconds` extension.

        Returns:
            The suggested retry delay in seconds, or `None` when the field is
            absent or null.
        """
        return self.problem.get("retryAfterSeconds")


class QuantDataInternalError(QuantDataHttpError):
    problem_type = "https://quantdata.us/errors/internal"
    default_status_code = 500
