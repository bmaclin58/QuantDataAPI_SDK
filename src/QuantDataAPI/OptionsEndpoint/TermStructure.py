"""Term Structure request and response helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Sequence

from QuantDataAPI.errors import QuantDataClientError
from QuantDataAPI.filterOptions import add_filter, add_session_or_snapshot
from QuantDataAPI.utility import CONTRACT_TYPES, _as_float
from QuantDataAPI.validationChecks import validate_non_empty_string

TERM_STRUCTURE_SCHEMA = {
    "expirationDate": str,
    "strikePrice": float,
    "contractType": str,
    "delta": float,
    "iv": float,
    "moneyType": str,
    "stockPrice": float,
}


def build_term_structure_request(
    *,
    ticker: str,
    sessionDate: date | datetime | str | None = None,
    snapshotTime: datetime | str | None = None,
    expirationDates: Sequence[str] | None = None,
    expirationDateRange: Mapping[str, Any] | None = None,
    strikePrices: Sequence[int | float] | None = None,
    strikePriceRange: Mapping[str, Any] | None = None,
    moneyTypes: Sequence[str] | None = None,
    deltaRange: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the documented Term Structure request body."""
    body: dict[str, Any] = {}
    add_session_or_snapshot(
        body,
        sessionDate=sessionDate,
        snapshotTime=snapshotTime,
    )
    add_filter(
        body,
        ticker=validate_non_empty_string("ticker", ticker),
        expirationDates=expirationDates,
        expirationDateRange=expirationDateRange,
        strikePrices=strikePrices,
        strikePriceRange=strikePriceRange,
        moneyTypes=moneyTypes,
        deltaRange=deltaRange,
    )
    return body


def normalize_term_structure(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Flatten expiration/strike/contract term-structure cells into rows."""
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
                for contract_type, cell in contracts.items():
                    if contract_type not in CONTRACT_TYPES or not isinstance(cell, Mapping):
                        raise TypeError("contract cells must be CALL/PUT objects")
                    money_type = cell["moneyType"]
                    if not isinstance(money_type, str):
                        raise TypeError("moneyType must be a string")
                    rows.append(
                        {
                            "expirationDate": expiration,
                            "strikePrice": _as_float(strike),
                            "contractType": contract_type,
                            "delta": _as_float(cell["delta"]),
                            "iv": _as_float(cell["iv"]),
                            "moneyType": money_type,
                            "stockPrice": stock_price,
                        }
                    )
    except (KeyError, TypeError, ValueError) as exc:
        raise QuantDataClientError(
            f"Unexpected term structure response: {exc}"
        ) from exc
    return sorted(
        rows,
        key=lambda row: (
            row["expirationDate"],
            row["strikePrice"],
            row["contractType"],
        ),
    )
