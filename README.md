# Agentic CI Pipeline

A locally-executable, read-only pre-PR quality pipeline. Run it against a
branch before opening a pull request to get a structured code review report
with normalized findings saved to disk.

---

## What it does

1. Clones your repo into an isolated temp directory (never touches your working tree)
2. Runs deterministic checks (syntax, lint — configured per repo)
3. Maps the diff to relevant review packs (security, quality, boundary)
4. Runs read-only LLM reviewer agents in sequence
5. Deduplicates and normalizes findings to a versioned schema
6. Writes artifacts to `artifacts/<run-id>/`

---

## Getting Started

**Step 1 — Clone this pipeline**
```bash
git clone https://github.com/AliMusafar/agentic-ci-pipeline.git
cd agentic-ci-pipeline
```

**Step 2 — Clone the repo you want to review (into the same folder)**
```bash
git clone https://github.com/your-username/your-repo.git
```

Your folder should now look like this:
```
agentic-ci-pipeline/
  your-repo/        ← the repo you want to review
  agentic_ci/
  ci_pipeline.py
  ...
```

**Step 3 — Install dependencies and add your API key**
```bash
pip install -r requirements.txt
```

Create a `.env` file inside `agentic-ci-pipeline/`:
```
LLM_API_KEY=your-anthropic-api-key
LLM_MODEL=claude-sonnet-4-6
```

**Step 4 — Run**
```bash
python ci_pipeline.py --repo ./your-repo
```

That's it. Results are written to `artifacts/` — open `report.md` to read the findings.

> Your repo is never modified. The pipeline clones it into a temp directory,
> reviews it there, then deletes the temp copy when done.

---

## Requirements

- Python 3.12+
- Git available in PATH
- Anthropic API key

---

## Install

```bash
pip install -r requirements.txt
```

Create a `.env` file in this directory:

```
LLM_API_KEY=your-anthropic-api-key
LLM_MODEL=claude-sonnet-4-6
```

---

## Run

```bash
python ci_pipeline.py --repo ./path/to/your/repo
```

Optional flags:

```bash
python ci_pipeline.py --repo ./my-repo --base main --head HEAD
```

| Flag | Default | Description |
|------|---------|-------------|
| `--repo` | `.` | Path to target git repo |
| `--base` | `HEAD~1` | Base ref for diff |
| `--head` | `HEAD` | Head ref for diff |

---

## Output

Every run writes to `artifacts/<run-id>/`:

| File | Description |
|------|-------------|
| `report.md` | Human-readable findings report |
| `findings.json` | All findings in `finding/v1` schema |
| `manifest.json` | Run metadata, artifact hashes, schema versions |
| `run-events.json` | Full run state machine log |

---

## Run against a fixture

```bash
cd fixtures/patch-02-eval-injection
git init && git add . && git commit -m "initial"
cp buggy.py app.py && git add . && git commit -m "introduce bugs"
cd ../..

python ci_pipeline.py --repo fixtures/patch-02-eval-injection
```

See [fixtures/README.md](fixtures/README.md) for all 5 fixture cases.

---

## Project structure

```
.agentic-ci/          config — repo profile and review packs
agentic_ci/           pipeline code
schemas/              versioned Pydantic contracts
fixtures/             5 replayable test cases
docs/                 threat model, build sheet
artifacts/            runtime output (gitignored)
ci_pipeline.py        CLI entry point
```

---

## Docs

- [Runbook](docs/runbook.md) — install, run, configure, debug
- [Troubleshooting Guide](docs/troubleshooting.md) — common errors and fixes
- [ADR](docs/adr.md) — why key architectural decisions were made
- [Threat Model](docs/threat-model.md)
- [Normative v1 Build Sheet](docs/normative-v1-build-sheet.md)
- [Fixtures Guide](fixtures/README.md)

---

## Milestone status

| Milestone | Status |
|-----------|--------|
| M0 — Contracts and fixtures | Complete |
| M1 — Read-only vertical slice | Complete |
| M2 — Bounded auto-fix | Not started |
