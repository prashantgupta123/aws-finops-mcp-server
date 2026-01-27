"""Helper functions for AWS FinOps operations."""

import re
from typing import Any


def format_header(accessor: str) -> str:
    """Convert field accessor to formatted header.
    
    Examples:
        instance_id -> Instance ID
        AMIId -> AMI ID
        MaxCPUUtilization -> Max CPU Utilization
    """
    # Replace underscores with spaces
    s = accessor.replace("_", " ")
    
    # Insert space before CamelCase transitions
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)
    
    # Handle acronyms (keep AMI, ID, ASG, etc. uppercase)
    words = s.split()
    formatted_words = []
    
    for w in words:
        # Keep all-uppercase words as-is
        if w.isupper():
            formatted_words.append(w)
        # Handle mixed case with acronyms
        elif re.fullmatch(r"(?:[A-Z]{2,}[A-Z][a-z]*)+", w):
            parts = re.findall(r"(?:[A-Z]{2,}(?=[A-Z][a-z]|$))|[A-Z][a-z]+|[a-z]+", w)
            formatted_words.extend([p if p.isupper() else p.capitalize() for p in parts])
        else:
            formatted_words.append(w.capitalize())
    
    return " ".join(formatted_words)


def fields_to_headers(fields: dict[str, str]) -> list[dict[str, str]]:
    """Convert fields dictionary to headers list.
    
    Args:
        fields: Dictionary mapping field IDs to accessor names
        
    Returns:
        List of header dictionaries with Header and accessor keys
    """
    return [
        {"Header": format_header(accessor), "accessor": accessor}
        for accessor in fields.values()
    ]


def normalize_data(data_list: list[dict[str, Any]], all_tag_keys: set[str]) -> list[dict[str, Any]]:
    """Normalize data by ensuring all items have the same keys.
    
    Args:
        data_list: List of data dictionaries
        all_tag_keys: Set of all possible tag keys
        
    Returns:
        Normalized list with consistent keys
    """
    normalized_data = []
    for item in data_list:
        row = item.copy()
        for tag_key in all_tag_keys:
            row.setdefault(tag_key, "")
        normalized_data.append(row)
    return normalized_data


def remove_percent_sign(value: str | None) -> str:
    """Remove percent sign from string value."""
    return value.replace("%", "").strip() if value else ""


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    if value is None:
        return default
    try:
        if isinstance(value, str):
            value = remove_percent_sign(value)
        return float(value)
    except (ValueError, TypeError):
        return default
