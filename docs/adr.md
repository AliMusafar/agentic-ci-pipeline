# Architectural Decision Record

**Version:** v1  
**Scope:** Agentic CI Pipeline — Milestone 1 major decisions

---

## ADR-01: Plain Python orchestration instead of an agent framework

**Decision:** Use plain sequential Python to orchestrate the pipeline stages instead of OpenHands SDK, LangGraph, or another agent framework.

**Why:**
Milestone 1 is read-only. The pipeline has a fixed, linear execution path:
clone → checks → diff → review → dedupe → publish. There is no branching
logic, no tool use, no multi-turn conversation, and no state that needs to
persist between agent calls. An agent framework adds complexity without
adding value at this stage.

The spec (§9.4) also states that Trigger.dev is the intended orchestration
platform for M2+. Building on a different framework in M1 would create
throwaway work.

**Tradeoff:** A framework like LangGraph would make it easier to add
conditional branching and retries later. Plain Python requires more manual
wiring in M2 when the fix/verify loop is added.

**When to revisit:** When the fix-verify-rollback loop (M2) is implemented,
evaluate whether Trigger.dev or LangGraph is needed for retry logic and
durable execution.

---

## ADR-02: Anthropic SDK directly instead of OpenHands for reviewers

**Decision:** Call the Anthropic API directly for reviewer agents instead of
using the OpenHands SDK with TerminalTool.

**Why:**
The reviewer's job is to read code and return structured JSON findings. It
does not need to execute commands, edit files, or interact with a shell.
Giving it TerminalTool (as the previous implementation did) was both
unnecessary and a security risk — TerminalTool allows arbitrary shell
commands, making the reviewer not truly read-only.

A direct Anthropic API call is simpler, faster, cheaper, and genuinely
read-only. The reviewer receives the diff and file contents as text in the
prompt and returns findings as JSON.

**Tradeoff:** OpenHands would make it easier to add tool-using agents later
(fix workers, verifiers). The direct API approach means fix workers in M2
will need a different execution model.

**When to revisit:** When fix workers are implemented in M2, evaluate
OpenHands remote workspace as the execution environment for agents that
need to edit files and run verification commands.

---

## ADR-03: Git clone to temp directory for isolation

**Decision:** Clone the target repo into a `tempfile.mkdtemp()` directory
for all pipeline work, rather than working in the developer's checked-out
directory.

**Why:**
The spec (§4.4, §14.1) is explicit: the system must never write to the
developer's working tree. Cloning to a temp directory enforces this at the
infrastructure level rather than relying on agent behaviour. Even if a bug
causes a write, it lands in the temp clone, not the developer's files.

The temp directory is deleted in a `finally` block regardless of success
or failure, so it never accumulates state between runs.

**Tradeoff:** Cloning adds a few seconds to each run for large repos.
A shallow clone (`--depth 1`) could be used to speed this up, but would
limit the available git history for diff computation.

**When to revisit:** If run time becomes a concern on large repos, switch
to `git clone --depth N` with a configurable depth in the repo profile.

---

## ADR-04: JSON files on disk instead of SQLite for findings storage

**Decision:** Write findings to `findings.json` per run rather than
inserting into a SQLite database.

**Why:**
Milestone 1 produces one report per run. There is no requirement for
cross-run querying, longitudinal metrics, or concurrent access in M1.
JSON files are human-readable, require no database setup, and are trivially
inspectable with any text editor.

Nick's feedback confirmed this: "SQLite is fine for local" — meaning SQLite
is acceptable but not required for M1. JSON satisfies the durability and
versioned schema requirements at lower complexity.

**Tradeoff:** JSON files cannot be queried across runs. Finding trends,
duplicate rates over time, and accepted/rejected ratios cannot be computed
without loading multiple files manually.

**When to revisit:** In M2, when the integrator needs to accept/reject
findings and the verifier needs to record per-batch results, a SQLite
database (or Postgres for cloud) becomes the right choice.

---

## ADR-05: Repo profile lives in the pipeline repo, not the target repo

**Decision:** The `.agentic-ci/` config lives in the pipeline repository,
not in each target repo being reviewed.

**Why:**
In M1, the pipeline is a standalone tool pointed at external repos. Requiring
each target repo to contain a `.agentic-ci/` config would add setup friction
for every repo being reviewed. A single generic profile in the pipeline repo
works for all target repos without any changes to those repos.

**Tradeoff:** The profile cannot be repo-specific without manual updates.
A TypeScript repo and a Python repo use the same profile, which is less
optimal than per-repo configuration.

**When to revisit:** In M3 (repo profile expansion), add logic to check
for a `.agentic-ci/repo-profile.yaml` inside the target repo first, falling
back to the pipeline's default profile if not found.
