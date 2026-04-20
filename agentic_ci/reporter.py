import json
import hashlib
from pathlib import Path
from typing import List
from datetime import datetime
from schemas.finding import Finding
from schemas.artifact_manifest import ArtifactManifest, ArtifactEntry


def write_findings(artifacts_dir: Path, findings: List[Finding]) -> Path:
    path = artifacts_dir / "findings.json"
    path.write_text(json.dumps([f.model_dump() for f in findings], indent=2), encoding="utf-8")
    return path


def write_report(
    artifacts_dir: Path,
    findings: List[Finding],
    run_id: str,
    repo: str,
    base_ref: str,
    head_ref: str,
) -> Path:
    path = artifacts_dir / "report.md"

    by_severity = {s: [f for f in findings if f.severity == s]
                   for s in ("critical", "high", "medium", "low")}
    autofixable = [f for f in findings if f.autofixable]

    lines = [
        "# Agentic CI Report",
        "",
        f"**Run ID:** `{run_id}`  ",
        f"**Repo:** {repo}  ",
        f"**Base:** `{base_ref}` -> **Head:** `{head_ref}`  ",
        f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Severity | Count |",
        "|----------|-------|",
        *[f"| {s.capitalize()} | {len(by_severity[s])} |"
          for s in ("critical", "high", "medium", "low")],
        f"| **Total** | **{len(findings)}** |",
        "",
        f"Auto-fixable: {len(autofixable)} of {len(findings)}",
        "",
        "---",
        "",
        "## Findings",
        "",
    ]

    for f in findings:
        lines += [
            f"### [{f.severity.upper()}] {f.title}",
            "",
            f"**Category:** {f.category}  ",
            f"**Confidence:** {f.confidence:.0%}  ",
            f"**Files:** {', '.join(f.scope.files)}  ",
            f"**Source:** {f.source}  ",
            f"**Auto-fixable:** {'Yes' if f.autofixable else 'No — requires human review'}  ",
            "",
            f"{f.summary}",
            "",
            f"**Proposed action:** {f.proposed_action}",
            "",
        ]
        if f.risk_notes:
            lines.append(f"**Risk notes:** {'; '.join(f.risk_notes)}")
            lines.append("")
        lines.append("---")
        lines.append("")

    if not findings:
        lines.append("No findings. The code looks clean.")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_manifest(artifacts_dir: Path, manifest: ArtifactManifest) -> Path:
    path = artifacts_dir / "manifest.json"
    path.write_text(json.dumps(manifest.model_dump(), indent=2), encoding="utf-8")
    return path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
