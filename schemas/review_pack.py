from pydantic import BaseModel
from typing import List


class ScopeSelector(BaseModel):
    include_paths: List[str] = ["**"]
    exclude_paths: List[str] = []


class ReviewPack(BaseModel):
    schema_version: str = "review_pack/v1"
    id: str
    kind: str  # general, security, boundary, test_gap, docs_drift
    name: str
    scope_selector: ScopeSelector = ScopeSelector()
    policy_text: str
    output_schema: str = "finding/v1"
    verification_hints: List[str] = []
