from pydantic import BaseModel, Field
from typing import List, Optional
import uuid


class FindingScope(BaseModel):
    files: List[str] = []
    symbols: List[str] = []


class FindingEvidence(BaseModel):
    kind: str
    path: str
    line: Optional[int] = None


class Finding(BaseModel):
    schema_version: str = "finding/v1"
    id: str = Field(default_factory=lambda: f"finding_{uuid.uuid4().hex[:8]}")
    fingerprint: str
    source: str
    category: str  # security, boundary, quality, test_gap, docs_drift
    severity: str  # critical, high, medium, low
    confidence: float
    scope: FindingScope = Field(default_factory=FindingScope)
    title: str
    summary: str
    evidence: List[FindingEvidence] = []
    proposed_action: str
    autofixable: bool
    risk_notes: List[str] = []
    verification_hints: List[str] = []
