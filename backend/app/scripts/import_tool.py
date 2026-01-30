import argparse
import csv
import json
from pathlib import Path

from app.schemas.admin import BulkError, BulkErrorSummary, BulkValidateResult
from app.schemas.exercise import ExerciseCreate
from app.schemas.passage import PassageCreate
from app.schemas.sentence import SentenceCreate
from app.schemas.word import WordCreate

SCHEMA_MAP = {
    "word": WordCreate,
    "sentence": SentenceCreate,
    "passage": PassageCreate,
    "exercise": ExerciseCreate,
}


def _parse_list(value: str | None) -> list[str] | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_options(value: str | None) -> list[str] | None:
    return _parse_list(value)


def _parse_level(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def load_items(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "items" in data:
            return data["items"]
        if isinstance(data, list):
            return data
        raise ValueError("JSON must be a list or contain 'items'")
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            items: list[dict] = []
            for row in reader:
                cleaned = {key: value for key, value in row.items() if value is not None and value != ""}
                if "answer" in cleaned:
                    cleaned["answer"] = cleaned["answer"].strip()
                if "prompt" in cleaned:
                    cleaned["prompt"] = cleaned["prompt"].strip()
                tags = _parse_list(row.get("tags"))
                options = _parse_options(row.get("options"))
                level = _parse_level(row.get("level"))
                if tags is not None:
                    cleaned["tags"] = tags
                if options is not None:
                    cleaned["options"] = options
                if level is not None:
                    cleaned["level"] = level
                items.append(cleaned)
            return items
    raise ValueError("Unsupported file type")


def validate_items(entity_type: str, items: list[dict]) -> BulkValidateResult:
    schema = SCHEMA_MAP.get(entity_type)
    if schema is None:
        raise ValueError("Unsupported entity_type")
    errors: list[BulkError] = []
    duplicates = set()
    seen_keys = set()
    for index, item in enumerate(items):
        try:
            schema.model_validate(item)
        except Exception as exc:
            details = []
            if hasattr(exc, "errors"):
                for err in exc.errors():
                    field = ".".join(str(part) for part in err.get("loc", [])) or "item"
                    details.append(f"{field}: {err.get('msg', 'Invalid value')}")
            message = "; ".join(details) if details else str(exc)
            errors.append(BulkError(index=index, field="item", message=message))
            continue
        key = None
        if entity_type in ("word", "sentence"):
            key = item.get("text")
        elif entity_type == "passage":
            key = item.get("title")
        elif entity_type == "exercise":
            key = f"{item.get('exercise_type')}::{item.get('prompt')}"
        if key is not None:
            if key in seen_keys:
                duplicates.add(index)
            else:
                seen_keys.add(key)
    for index in sorted(duplicates):
        errors.append(BulkError(index=index, field="item", message="Duplicate item in payload"))
    buckets: dict[tuple[str, str], int] = {}
    for error in errors:
        key = (error.field, error.message)
        buckets[key] = buckets.get(key, 0) + 1
    summary = [BulkErrorSummary(field=field, message=message, count=count) for (field, message), count in buckets.items()]
    return BulkValidateResult(valid=len(errors) == 0, errors=errors, error_summary=summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate import file for admin bulk APIs.")
    parser.add_argument("--entity", required=True, help="word|sentence|passage|exercise")
    parser.add_argument("--file", required=True, help="Path to JSON or CSV file")
    parser.add_argument("--export-errors", help="Path to export errors as CSV")
    args = parser.parse_args()

    items = load_items(Path(args.file))
    result = validate_items(args.entity, items)
    if args.export_errors and result.errors:
        export_path = Path(args.export_errors)
        with export_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["index", "field", "message"])
            for error in result.errors:
                writer.writerow([error.index, error.field, error.message])
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
