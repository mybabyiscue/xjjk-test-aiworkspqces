"""Load and validate explicit review policy values."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Pattern


def read_policy(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing review policy: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Review policy root must be an object: {path}")
    return value


def require_section(policy: dict[str, object], name: str) -> dict[str, object]:
    value = policy.get(name)
    if not isinstance(value, dict):
        raise TypeError(f"Review policy section must be an object: {name}")
    return value


def require_string(section: dict[str, object], name: str) -> str:
    value = section.get(name)
    if not isinstance(value, str) or not value:
        raise TypeError(f"Review policy value must be a non-empty string: {name}")
    return value


def require_string_list(section: dict[str, object], name: str) -> list[str]:
    value = section.get(name)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise TypeError(f"Review policy value must be a non-empty string list: {name}")
    return list(value)


def require_string_map(section: dict[str, object], name: str) -> dict[str, str]:
    value = section.get(name)
    if not isinstance(value, dict) or not value:
        raise TypeError(f"Review policy value must be a non-empty string map: {name}")
    result: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key or not isinstance(item, str) or not item:
            raise TypeError(f"Review policy map entries must use non-empty strings: {name}")
        result[key] = item
    return result


def require_positive_int(section: dict[str, object], name: str) -> int:
    value = section.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise TypeError(f"Review policy value must be a positive integer: {name}")
    return value


def require_non_negative_int(section: dict[str, object], name: str) -> int:
    value = section.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise TypeError(f"Review policy value must be a non-negative integer: {name}")
    return value


def require_ratio(section: dict[str, object], name: str) -> float:
    value = section.get(name)
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 < float(value) <= 1:
        raise TypeError(f"Review policy value must be a ratio in (0, 1]: {name}")
    return float(value)


def require_pattern(section: dict[str, object], name: str) -> Pattern[str]:
    return re.compile(require_string(section, name))


def require_rule_list(section: dict[str, object], name: str) -> list[dict[str, str]]:
    value = section.get(name)
    if not isinstance(value, list) or not value:
        raise TypeError(f"Review policy value must be a non-empty rule list: {name}")
    result: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise TypeError(f"Review policy rule must be an object: {name}[{index}]")
        normalized: dict[str, str] = {}
        for field in ("priority", "title", "pattern"):
            field_value = item.get(field)
            if not isinstance(field_value, str) or not field_value:
                raise TypeError(f"Review policy rule field must be a non-empty string: {name}[{index}].{field}")
            normalized[field] = field_value
        re.compile(normalized["pattern"])
        result.append(normalized)
    return result
