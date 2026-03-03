"""Validate Excel data for completeness and correctness."""

import re
from typing import Dict, List, Tuple

from .constants import REQUIRED_FIELDS, RECOMMENDED_FIELDS, MAX_SERVICES, MAX_CITIES
from .excel_reader import get_service_count, get_city_count


def validate_data(data: Dict[str, str]) -> Tuple[List[str], List[str]]:
    """Validate the data dictionary.

    Returns:
        Tuple of (errors, warnings). Errors are fatal, warnings are informational.
    """
    errors = []
    warnings = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")

    # Check recommended fields
    for field in RECOMMENDED_FIELDS:
        if not data.get(field):
            warnings.append(f"Missing recommended field: {field}")

    # Validate hex colors
    for color_field in ["COLOR_PRIMARY", "COLOR_ACCENT", "COLOR_SECONDARY"]:
        val = data.get(color_field, "")
        if val and not _is_valid_hex(val):
            errors.append(f"Invalid hex color for {color_field}: '{val}' (expected #RRGGBB)")

    # Must have at least 1 service
    service_count = get_service_count(data)
    if service_count == 0:
        errors.append("No services defined. At least SERVICE_1_NAME is required.")
    else:
        # Validate each service has required fields
        for n in range(1, service_count + 1):
            if not data.get(f"SERVICE_{n}_SLUG"):
                errors.append(f"SERVICE_{n}_SLUG is required when SERVICE_{n}_NAME is defined")

    # Must have at least 1 city
    city_count = get_city_count(data)
    if city_count == 0:
        errors.append("No cities defined. At least CITY_1_NAME is required.")
    else:
        for n in range(1, city_count + 1):
            if not data.get(f"CITY_{n}_SLUG"):
                errors.append(f"CITY_{n}_SLUG is required when CITY_{n}_NAME is defined")

    # Validate DOMAIN format
    domain = data.get("DOMAIN", "")
    if domain and not domain.startswith("http"):
        warnings.append(f"DOMAIN should start with https:// (got: '{domain}')")

    return errors, warnings


def _is_valid_hex(color: str) -> bool:
    """Check if a string is a valid hex color (#RGB or #RRGGBB)."""
    return bool(re.match(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', color))
