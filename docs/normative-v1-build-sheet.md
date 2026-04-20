# Normative v1 Build Sheet

**Version:** v1  
**Scope:** Agentic CI — local mode (Milestone 1)

This document records the concrete technology decisions for the first
implementation. It exists to prevent guesswork and make tradeoffs explicit.

---

## What is built in M1

A locally-executable, read-only pre-PR quality pipeline that:

1. Clones the target repo into an isolated temp directory
2. Runs configured deterministic checks
3. Maps the diff to relevant review packs
4. Runs LLM-based read-only reviewer agents
5. Normalizes and deduplicates findings
6. Writes versioned artifact files to `artifacts/<run-id>/`

No code is written to the target repo. No fix branch is created. M1 is
strictly read-only.

---

## Technology decisions

| Component | Decision | Reason |
|-----------|----------|--------|
| LLM reviewer | Anthropic SDK (direct API call) | No agent tools needed for read-only review; simpler and more reliable than OpenHands for M1 |
| Orchestration | Plain Python (sequential) | Trigger.dev is the M2+ target; local sequential flow is sufficient and debuggable for M1 |
| Findings store | JSON files on disk (`findings.json`) | Durable, versioned, human-readable; SQLite is the M2 target when cross-run queries are needed |
| Artifact storage | Local `artifacts/<run-id>/` directory | GCS is the production target; local files are sufficient for M1 |
| Repo isolation | `git clone --local` to `tempfile.mkdtemp()` | Guarantees no writes to developer's working tree |
| Schema validation | Pydantic v2 | Enforces versioned contracts at runtime with clear error messages |
| Config format | YAML (repo profile + review packs) | Human-editable, version-controllable, matches spec §16 |
| Run state | JSON run-events file | SQLite or Postgres is the M2+ target; JSON is sufficient for local single-run tracking |

---

## What is explicitly deferred to M2+

| Item | Target milestone |
|------|-----------------|
| Integrator agent (accept/reject findings) | M2 |
| Fix workers and auto-fix | M2 |
| Per-batch verification and rollback | M2 |
| Sibling `agentic-ci/<run-id>` fix branch | M2 |
| SQLite findings ledger | M2 |
| Trigger.dev orchestration | M2+ |
| GCS artifact storage | M3+ |
| Cloud SQL Postgres workflow ledger | M3+ |
| Secret scrubbing from LLM prompts | M2 |
| Outbound network sandbox | M2 |
| External reviewer adapters (CodeRabbit, cubic) | M5 |

---

## Key implementation rules (M1)

- The reviewer must never receive file-writing tools.
- Repo content is passed to reviewers as labeled evidence, never as policy text.
- All writes go to `artifacts/<run-id>/` — never to the target repo path.
- Every machine-readable output includes `schema_version`.
- The clone is deleted in a `finally` block regardless of success or failure.
- `artifacts/` is gitignored to prevent accidental commit of run outputs.

---

## Local execution model

```
Developer machine
  |
  +--> python ci_pipeline.py --repo ./my-repo
         |
         +--> git clone --local ./my-repo /tmp/agentic-ci-<run_id>/
         +--> run deterministic checks in clone
         +--> compute diff, select review packs
         +--> call Anthropic API for each reviewer
         +--> write artifacts/<run-id>/
         +--> delete /tmp/agentic-ci-<run_id>/
```

No remote services required in M1 beyond the Anthropic API.

---

## Assumptions that drive these decisions

1. The developer runs this on their own machine before pushing a PR.
2. The Anthropic API is the only external service called.
3. The target repo is a local git repository accessible by path.
4. Python 3.12+ is available in the execution environment.
