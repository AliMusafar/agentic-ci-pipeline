from pydantic import BaseModel
from typing import List, Optional


class FixBatch(BaseModel):
    schema_version: str = "fix_batch/v1"
    id: str
    accepted_findings: List[str]  # list of finding IDs
    target_files: List[str]
    goal: str
    allowed_edit_globs: List[str] = []
    verification_plan: List[str] = []
    result: Optional[str] = None  # passed, failed, rolled_back, pending
