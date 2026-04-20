import os
import json
import re
from typing import List
from anthropic import Anthropic
from schemas.finding import Finding, FindingScope, FindingEvidence
from schemas.review_pack import ReviewPack

SYSTEM_PROMPT = """You are a read-only code reviewer. You receive a git diff, changed file contents, and a review policy.

Your job: output a JSON array of findings. Do NOT suggest writing or modifying files.

Each finding must follow this exact schema:
{
  "fingerprint": "<category>|<file>|<short-slug>",
  "source": "<pack_id>",
  "category": "<security|boundary|quality|test_gap|docs_drift>",
  "severity": "<critical|high|medium|low>",
  "confidence": <0.0-1.0>,
  "scope": {"files": ["<file>"], "symbols": ["<symbol_or_empty>"]},
  "title": "<short title under 60 chars>",
  "summary": "<1-2 sentence description of the problem>",
  "evidence": [{"kind": "code", "path": "<file>", "line": <line_number_or_null>}],
  "proposed_action": "<what a developer should do to fix this>",
  "autofixable": <true|false>,
  "risk_notes": [],
  "verification_hints": []
}

Rules:
- Output ONLY a valid JSON array. No markdown fences, no explanation text.
- If no issues found, output an empty array: []
- autofixable must be false for auth, payment, secrets, migrations, or rate-limiting changes
- confidence should reflect how certain you are (0.9+ = very certain, 0.5 = possible issue)"""


def run_reviewer(pack: ReviewPack, diff: str, file_contents: dict) -> List[Finding]:
    api_key = os.getenv("LLM_API_KEY")
    model_env = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
    model = model_env.replace("anthropic/", "")

    client = Anthropic(api_key=api_key)

    files_block = "\n\n".join(
        f"=== {fname} ===\n{content}" for fname, content in file_contents.items()
    )

    user_message = (
        f"## Review Pack: {pack.name}\n\n"
        f"## Policy\n{pack.policy_text}\n\n"
        f"## Git Diff\n```\n{diff[:5000]}\n```\n\n"
        f"## Changed File Contents\n{files_block}\n\n"
        f"Output findings as a JSON array."
    )

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()
    return _parse_findings(raw, pack.id)


def _parse_findings(raw: str, pack_id: str) -> List[Finding]:
    # Extract JSON array even if there's surrounding text
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        return []

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return []

    findings = []
    for item in data:
        try:
            item["source"] = pack_id
            item["schema_version"] = "finding/v1"
            # Ensure scope is a dict
            if isinstance(item.get("scope"), dict):
                item["scope"] = FindingScope(**item["scope"])
            else:
                item["scope"] = FindingScope()
            # Ensure evidence is a list of dicts
            raw_evidence = item.pop("evidence", [])
            item["evidence"] = [
                FindingEvidence(**e) if isinstance(e, dict) else FindingEvidence(kind="code", path="unknown")
                for e in raw_evidence
            ]
            findings.append(Finding(**item))
        except Exception:
            continue

    return findings
