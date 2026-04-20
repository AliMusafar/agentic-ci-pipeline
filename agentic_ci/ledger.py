from typing import List
from schemas.finding import Finding

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def normalize_and_dedupe(findings: List[Finding]) -> List[Finding]:
    """Keep highest-confidence finding per fingerprint."""
    seen: dict[str, Finding] = {}
    for f in findings:
        fp = f.fingerprint
        if fp not in seen or f.confidence > seen[fp].confidence:
            seen[fp] = f
    return list(seen.values())


def sort_findings(findings: List[Finding]) -> List[Finding]:
    return sorted(
        findings,
        key=lambda f: (SEVERITY_ORDER.get(f.severity, 4), -f.confidence),
    )
