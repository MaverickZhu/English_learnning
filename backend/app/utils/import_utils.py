import csv
import json
from pathlib import Path
from typing import Any


def parse_json(content: str) -> list[dict]:
    data = json.loads(content)
    if isinstance(data, dict) and "items" in data:
        return data["items"]
    if isinstance(data, list):
        return data
    raise ValueError("JSON must be a list or contain 'items'")


def _parse_list(value: str | None) -> list[str] | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_level(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def parse_csv(content: str) -> list[dict]:
    reader = csv.DictReader(content.splitlines())
    items: list[dict] = []
    for row in reader:
        cleaned = {key: value for key, value in row.items() if value is not None and value != ""}
        if "answer" in cleaned:
            cleaned["answer"] = cleaned["answer"].strip()
        if "prompt" in cleaned:
            cleaned["prompt"] = cleaned["prompt"].strip()
        tags = _parse_list(row.get("tags"))
        options = _parse_list(row.get("options"))
        level = _parse_level(row.get("level"))
        if tags is not None:
            cleaned["tags"] = tags
        if options is not None:
            cleaned["options"] = options
        if level is not None:
            cleaned["level"] = level
        items.append(cleaned)
    return items


def apply_mapping(items: list[dict], mapping: dict[str, str] | None) -> list[dict]:
    if not mapping:
        return items
    mapped_items: list[dict] = []
    for item in items:
        mapped: dict[str, Any] = {}
        for target, source in mapping.items():
            if source in item:
                mapped[target] = item[source]
        for key, value in item.items():
            if key not in mapping.values():
                mapped.setdefault(key, value)
        mapped_items.append(mapped)
    return mapped_items


def parse_file(filename: str, content: str) -> list[dict]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".json":
        return parse_json(content)
    if suffix == ".csv":
        return parse_csv(content)
    raise ValueError("Unsupported file type")
