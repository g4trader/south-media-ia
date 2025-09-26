"""Utilities for parsing numeric values from localized strings."""

import math
import re
from typing import Optional, Union

NumericInput = Union[str, int, float]

_NUMERIC_EXTRACT_PATTERN = re.compile(r"[^0-9,\.\-]+")
_SEPARATOR_PATTERN = re.compile(r"[\.,]")
_DIGIT_PATTERN = re.compile(r"[^0-9]")


def _normalize_input(value: NumericInput) -> Optional[str]:
    """Return a trimmed string representation of *value* or ``None`` if empty."""

    if value is None:
        return None

    if isinstance(value, (int, float)):
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None
        return str(value)

    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None

    # Normalise minus symbol variations
    text = text.replace("−", "-")
    return text


def _extract_sign(value: str) -> tuple[str, str]:
    """Return the sign (``"-"`` or ``""``) and the unsigned remainder of *value*."""

    sign = ""
    if value.startswith("-"):
        sign = "-"
        value = value[1:]

    # Remove any additional minus signs that may appear mid-string
    value = value.replace("-", "")
    return sign, value


def normalise_numeric_string(value: NumericInput) -> Optional[str]:
    """Convert *value* to a numeric string with ``."` as decimal separator.

    Thousands separators and currency symbols are removed. If no digits are
    found the function returns ``None``.
    """

    text = _normalize_input(value)
    if text is None:
        return None

    sign, unsigned = _extract_sign(text)
    unsigned = _NUMERIC_EXTRACT_PATTERN.sub("", unsigned)
    if not unsigned:
        return None

    digits_only = _DIGIT_PATTERN.sub("", unsigned)
    if not digits_only:
        return None

    separators = list(_SEPARATOR_PATTERN.finditer(unsigned))
    if not separators:
        return f"{sign}{digits_only}"

    last_sep = separators[-1]
    decimal_sep = last_sep.group()
    integer_part_raw = unsigned[: last_sep.start()]
    decimal_part_raw = unsigned[last_sep.start() + 1 :]

    integer_digits = _DIGIT_PATTERN.sub("", integer_part_raw)
    decimal_digits = _DIGIT_PATTERN.sub("", decimal_part_raw)

    treat_as_decimal = bool(decimal_digits)

    if treat_as_decimal:
        other_separator = "," if decimal_sep == "." else "."
        if other_separator not in unsigned:
            # Heuristic: strings like 31.000 or 12.345 represent thousands.
            if len(decimal_digits) == 3 and len(digits_only) > 3:
                treat_as_decimal = False

    if treat_as_decimal:
        return f"{sign}{integer_digits}.{decimal_digits}"

    return f"{sign}{digits_only}"


def safe_float(value: NumericInput) -> float:
    """Robust float conversion that handles currency and thousand separators."""

    if value is None:
        return 0.0

    if isinstance(value, (int, float)):
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return 0.0
        return float(value)

    normalised = normalise_numeric_string(value)
    if not normalised:
        return 0.0

    try:
        return float(normalised)
    except (TypeError, ValueError):
        return 0.0


def safe_int(value: NumericInput) -> int:
    """Robust integer conversion that mirrors :func:`safe_float`."""

    if value is None:
        return 0

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return 0
        return int(value)

    normalised = normalise_numeric_string(value)
    if not normalised:
        return 0

    try:
        return int(float(normalised))
    except (TypeError, ValueError):
        return 0
