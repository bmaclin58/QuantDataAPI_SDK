"""Volatility Skew request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Sequence

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import add_filter, add_session_or_snapshot
from QuantDataAPI.utility import CONTRACT_TYPES, _as_float, to_quantdata_date
from QuantDataAPI.validationChecks import (
    validate_enum_sequence,
    validate_non_empty_string,
)

VOLATILITY_SKEW_SCHEMA = {
    "expirationDate": date,
    "strikePrice": float,
    "contractType": str,
    "impliedVolatility": float,
    "stockPrice": float,
}


def build_volatility_skew_request(
    *,
    ticker: str,
    sessionDate: date | datetime | str | None = None,
    snapshotTime: datetime | str | None = None,
    contractTypes: Sequence[str] | None = None,
    expirationDate: date | datetime | str | None = None,
    expirationDates: Sequence[str] | None = None,
    expirationDateRange: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the documented Volatility Skew request body."""
    body: dict[str, Any] = {}
    add_session_or_snapshot(
        body,
        sessionDate=sessionDate,
        snapshotTime=snapshotTime,
    )
    add_filter(
        body,
        ticker=validate_non_empty_string("ticker", ticker),
        contractTypes=validate_enum_sequence(
            "contractTypes",
            contractTypes,
            CONTRACT_TYPES,
        ),
        expirationDate=(
            to_quantdata_date(expirationDate)
            if expirationDate is not None
            else None
        ),
        expirationDates=expirationDates,
        expirationDateRange=expirationDateRange,
    )
    return body


def normalize_volatility_skew(
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Flatten expiration/strike/contract implied-volatility leaves into rows."""
    try:
        stock_price = _as_float(payload["stockPrice"])
        data = payload["data"]
        if not isinstance(data, Mapping):
            raise TypeError("data must be an object")
        rows = []
        for expiration, strikes in data.items():
            if not isinstance(expiration, str) or not isinstance(strikes, Mapping):
                raise TypeError("expiration data must be keyed objects")
            for strike, contracts in strikes.items():
                if not isinstance(contracts, Mapping):
                    raise TypeError("strike data must be an object")
                for contract_type, implied_volatility in contracts.items():
                    if contract_type not in CONTRACT_TYPES:
                        raise TypeError("contract type must be CALL or PUT")
                    rows.append(
                        {
                            "expirationDate": date.fromisoformat(expiration),
                            "strikePrice": _as_float(strike),
                            "contractType": contract_type,
                            "impliedVolatility": _as_float(implied_volatility),
                            "stockPrice": stock_price,
                        }
                    )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected volatility skew response: {exc}"
        ) from exc
    return sorted(
        rows,
        key=lambda row: (
            row["expirationDate"],
            row["strikePrice"],
            row["contractType"],
        ),
    )
