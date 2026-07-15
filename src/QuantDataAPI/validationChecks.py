from typing import Sequence, Any


def validate_non_empty_string(name: str, value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} must be a non-empty string.")
    return normalized


def validate_enum(name: str, value: str, allowed: set[str]) -> str:
    normalized = value.upper()
    if normalized not in allowed:
        values = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of: {values}.")
    return normalized


def validate_enum_sequence(
    name: str,
    values: Sequence[str] | None,
    allowed: set[str],
) -> list[str] | None:
    if values is None:
        return None
    return [validate_enum(name, value, allowed) for value in values]


def validate_required(name: str, value: Any) -> Any:
    if value is None:
        raise ValueError(f"{name} is required.")
    return value


def validate_positive(name: str, value: int | float | None) -> int | float | None:
    if value is not None and value <= 0:
        raise ValueError(f"{name} must be positive.")
    return value


def validate_period_days(name: str, value: int) -> int:
    value = int(value)
    if not 1 <= value <= 365:
        raise ValueError(f"{name} must be between 1 and 365.")
    return value
