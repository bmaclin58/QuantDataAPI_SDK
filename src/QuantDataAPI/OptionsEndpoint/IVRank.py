"""IV Rank request and response helpers."""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping, Sequence

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import add_filter
from QuantDataAPI.utility import CONTRACT_TYPES, _as_float
from QuantDataAPI.validationChecks import (
    validate_enum_sequence,
    validate_non_empty_string,
    validate_period_days,
)

IV_RANK_SCHEMA = {
    "sessionDate": str,
    "contractType": str,
    "lastIv": float,
    "windowMinIv": float,
    "windowMaxIv": float,
    "expirationDate": date,
    "stockPrice": float,
}


def build_iv_rank_request(
    *,
    ticker: str,
    lookBackPeriod: int,
    maturity: int,
    contractTypes: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Build the documented IV Rank request body."""
    body: dict[str, Any] = {
        "lookBackPeriod": validate_period_days("lookBackPeriod", lookBackPeriod),
        "maturity": validate_period_days("maturity", maturity),
    }
    add_filter(
        body,
        ticker=validate_non_empty_string("ticker", ticker),
        contractTypes=validate_enum_sequence(
            "contractTypes",
            contractTypes,
            CONTRACT_TYPES,
        ),
    )
    return body


def normalize_iv_rank(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Flatten session/contract IV summaries into DataFrame-ready rows."""
    try:
        expiration_dates = payload["expirationDates"]
        data = payload["data"]
        if (
            not isinstance(expiration_dates, Sequence)
            or isinstance(expiration_dates, (str, bytes))
            or any(not isinstance(value, str) for value in expiration_dates)
        ):
            raise TypeError("expirationDates must be an array of dates")
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for session, session_data in data.items():
            if not isinstance(session, str) or not isinstance(session_data, Mapping):
                raise TypeError("session data must be keyed objects")
            contract_data = session_data["contractTypeToIVData"]
            expiration = session_data["expirationDate"]
            stock_price = _as_float(session_data["stockPrice"])
            if not isinstance(contract_data, Mapping) or not isinstance(expiration, str):
                raise TypeError("invalid session IV metadata")
            for contract_type, cell in contract_data.items():
                if contract_type not in CONTRACT_TYPES or not isinstance(cell, Mapping):
                    raise TypeError("contract IV cells must be CALL/PUT objects")
                rows.append(
                    {
                        "sessionDate": session,
                        "contractType": contract_type,
                        "lastIv": _as_float(cell["lastIv"]),
                        "windowMinIv": _as_float(cell["windowMinIv"]),
                        "windowMaxIv": _as_float(cell["windowMaxIv"]),
                        "expirationDate": date.fromisoformat(expiration),
                        "stockPrice": stock_price,
                    }
                )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(f"Unexpected IV rank response: {exc}") from exc
    return sorted(rows, key=lambda row: (row["sessionDate"], row["contractType"]))
