"""Core placeholder replacement engine."""

import re
from typing import Dict, List

from .constants import TEMPLATE_GTM_ID


def replace_placeholders(content: str, data: Dict[str, str]) -> str:
    """Replace all {{KEY}} placeholders in content with values from data dict.

    Keys starting with _ are internal metadata and are skipped.
    """
    def replacer(match):
        key = match.group(1).strip()
        return data.get(key, match.group(0))

    return re.sub(r'\{\{([^}]+)\}\}', replacer, content)


def replace_gtm(content: str, data: Dict[str, str]) -> str:
    """Replace the hardcoded GTM container ID with the one from Excel data.

    If no GTM_CONTAINER_ID is in data, removes GTM code entirely.
    """
    gtm_id = data.get("GTM_CONTAINER_ID", "")

    if gtm_id:
        # Replace the hardcoded GTM ID
        content = content.replace(TEMPLATE_GTM_ID, gtm_id)
    else:
        # Remove GTM head script block
        content = re.sub(
            r'\s*<!-- Google Tag Manager -->\s*<script>.*?</script>\s*',
            '\n',
            content,
            flags=re.DOTALL,
        )
        # Remove GTM noscript block
        content = re.sub(
            r'\s*<!-- Google Tag Manager \(noscript\) -->\s*<noscript>.*?</noscript>\s*',
            '\n',
            content,
            flags=re.DOTALL,
        )

    return content


def replace_service_x(content: str, service_num: int, data: Dict[str, str]) -> str:
    """Replace SERVICE_X placeholders with SERVICE_N values.

    For service template pages, the template uses SERVICE_X as a generic
    placeholder. This replaces those with the actual service number's data.
    """
    # Replace SERVICE_X_ with SERVICE_N_ in placeholder keys
    # First handle the {{SERVICE_X_*}} placeholders by substituting N
    def replacer(match):
        key = match.group(1).strip()
        if key.startswith("SERVICE_X_"):
            actual_key = key.replace("SERVICE_X_", f"SERVICE_{service_num}_")
            return data.get(actual_key, match.group(0))
        return match.group(0)

    result = re.sub(r'\{\{(SERVICE_X_[^}]+)\}\}', replacer, content)

    # Also replace IMAGE_SXL with IMAGE_S{N}L
    image_key = f"IMAGE_S{service_num}L"
    result = result.replace("{{IMAGE_SXL}}", data.get(image_key, ""))

    return result


def replace_city_x(content: str, city_num: int, data: Dict[str, str]) -> str:
    """Replace CITY_X placeholders with CITY_N values."""
    def replacer(match):
        key = match.group(1).strip()
        if key.startswith("CITY_X_"):
            actual_key = key.replace("CITY_X_", f"CITY_{city_num}_")
            return data.get(actual_key, match.group(0))
        return match.group(0)

    return re.sub(r'\{\{(CITY_X_[^}]+)\}\}', replacer, content)


def find_unreplaced(content: str) -> List[str]:
    """Find any remaining {{PLACEHOLDER}} tokens in content."""
    return re.findall(r'\{\{([^}]+)\}\}', content)


def process_file(content: str, data: Dict[str, str]) -> str:
    """Full processing pipeline for a template file.

    Applies placeholder replacement and GTM replacement.
    """
    content = replace_placeholders(content, data)
    content = replace_gtm(content, data)
    return content
