# Operator Runbook

**Version:** v1  
**Scope:** Agentic CI Pipeline — Milestone 1 (local mode)

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| Git | any recent version |
| Anthropic API key | required |

---

## Installation

**1. Clone the pipeline**
```bash
git clone https://github.com/AliMusafar/agentic-ci-pipeline.git
cd agentic-ci-pipeline
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Create `.env` file**
```
LLM_API_KEY=your-anthropic-api-key
LLM_MODEL=claude-sonnet-4-6
```

---

## Running a review

**Basic run — reviews last commit**
```bash
python ci_pipeline.py --repo ./your-repo
```

**Compare branch against main**
```bash
python ci_pipeline.py --repo ./your-repo --base main --head HEAD
```

**Compare two specific commits**
```bash
python ci_pipeline.py --repo ./your-repo --base abc1234 --head def5678
```

---

## Reading the output

After a run, open the artifacts folder printed at the end:

```
artifacts/run_<timestamp>/
  report.md        ← start here — human readable
  findings.json    ← machine readable, versioned schema
  manifest.json    ← run metadata and artifact hashes
  run-events.json  ← full stage-by-stage execution log
```

**Severity levels:**
- `critical` — must fix before PR
- `high` — strong recommendation to fix
- `medium` — worth fixing, lower urgency
- `low` — minor issues, clean up when convenient

**Auto-fixable field:**
- `true` — safe to fix automatically in a future milestone
- `false` — requires human judgment, do not auto-fix

---

## Debugging a failed run

**1. Check run-events.json**
Open `artifacts/<run-id>/run-events.json`. Find the stage with `"status": "failure"` and read the `metadata.reason` field.

**2. Check the terminal output**
The pipeline prints each stage transition. The last line before the error shows which stage failed.

**3. Common failure points**

| Stage | Common cause |
|-------|-------------|
| preflight | git clone failed — check repo path exists and has git init |
| deterministic_checks | command in repo-profile.yaml doesn't apply to this repo |
| impact_mapping | git diff failed — check base/head refs exist |
| review | Anthropic API error — check LLM_API_KEY in .env |
| publish | disk write error — check artifacts/ directory is writable |

---

## Configuring for a new repo

Edit `.agentic-ci/repo-profile.yaml`:

```yaml
schema_version: repo_profile/v1
repo_name: your-repo-name
base_branch: main

commands:
  preflight: []
  deterministic_checks: []   # add lint/typecheck commands here
  final_checks: []

paths:
  editable:
    - "**/*.py"
    - "**/*.ts"
  protected:
    - ".env"
    - "secrets/**"
```

---

## Artifacts are gitignored

The `artifacts/` directory is in `.gitignore`. Run outputs never get committed. To share a report, copy the `report.md` file manually.

---

## Cleaning up old runs

```bash
rm -rf artifacts/
```
