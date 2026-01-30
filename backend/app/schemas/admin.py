from typing import Literal

from pydantic import BaseModel

BulkMode = Literal["upsert", "insert_only", "update_only"]


class BulkError(BaseModel):
    index: int
    field: str
    message: str


class BulkErrorSummary(BaseModel):
    field: str
    message: str
    count: int


class BulkResult(BaseModel):
    created: int
    updated: int
    skipped: int
    errors: list[BulkError] = []
    error_summary: list[BulkErrorSummary] = []


class BulkActionResult(BaseModel):
    updated: int
    skipped: int
    errors: list[BulkError] = []
    error_summary: list[BulkErrorSummary] = []


class BulkDeleteResult(BaseModel):
    deleted: int
    missing: list[int] = []


class BulkWordRequest(BaseModel):
    items: list[dict]
    mode: BulkMode = "upsert"
    atomic: bool = False


class BulkSentenceRequest(BaseModel):
    items: list[dict]
    mode: BulkMode = "upsert"
    atomic: bool = False


class BulkPassageRequest(BaseModel):
    items: list[dict]
    mode: BulkMode = "upsert"
    atomic: bool = False


class BulkExerciseRequest(BaseModel):
    items: list[dict]
    mode: BulkMode = "upsert"
    atomic: bool = False


class TagAssignRequest(BaseModel):
    entity_type: Literal["word", "sentence", "passage", "exercise"]
    entity_id: int
    tags: list[str]
    mode: Literal["replace", "add", "remove"] = "replace"


class BulkDeleteRequest(BaseModel):
    ids: list[int]
    atomic: bool = False


class BulkTagAssignItem(BaseModel):
    entity_id: int
    tags: list[str]
    mode: Literal["replace", "add", "remove"] = "replace"


class BulkTagAssignRequest(BaseModel):
    entity_type: Literal["word", "sentence", "passage", "exercise"]
    items: list[BulkTagAssignItem]
    atomic: bool = False


class BulkValidateRequest(BaseModel):
    entity_type: Literal["word", "sentence", "passage", "exercise"]
    items: list[dict]


class BulkValidateResult(BaseModel):
    valid: bool
    errors: list[BulkError] = []
    error_summary: list[BulkErrorSummary] = []


class ImportExecuteRequest(BaseModel):
    entity_type: Literal["word", "sentence", "passage", "exercise"]
    items: list[dict]
    mode: BulkMode = "upsert"
    atomic: bool = False
