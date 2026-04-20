# Troubleshooting Guide

**Version:** v1  
**Scope:** Agentic CI Pipeline — Milestone 1 (local mode)

---

## API Key errors

**Error:**
```
ERROR: Set LLM_API_KEY in your .env file before running.
```
**Fix:** Create a `.env` file in the `agentic-ci-pipeline/` root:
```
LLM_API_KEY=your-anthropic-api-key
LLM_MODEL=claude-sonnet-4-6
```

---

**Error:**
```
anthropic.AuthenticationError: invalid x-api-key
```
**Fix:** Your API key is wrong or expired. Go to [console.anthropic.com](https://console.anthropic.com), generate a new key, and update `.env`.

---

**Error:**
```
anthropic.RateLimitError
```
**Fix:** You've hit the Anthropic API rate limit. Wait a minute and try again. If it happens repeatedly, check your usage tier at console.anthropic.com.

---

## Git errors

**Error:**
```
[failed] 'NoneType' object has no attribute 'strip'
```
**Cause:** `git diff` failed — usually because the base ref doesn't exist.  
**Fix:** Check your `--base` ref exists in the target repo:
```bash
cd your-repo
git log --oneline
```
If the repo only has one commit, use:
```bash
python ci_pipeline.py --repo ./your-repo --base HEAD --head HEAD
```

---

**Error:**
```
fatal: not a git repository
```
**Fix:** The path you passed to `--repo` is not a git repo. Make sure it has been initialised:
```bash
cd your-repo
git init
git add .
git commit -m "initial"
```

---

**Error:**
```
fatal: destination path already exists
```
**Cause:** A previous clone to the temp directory wasn't cleaned up.  
**Fix:** This is auto-handled by the pipeline's `finally` block. If it persists, manually delete temp folders matching `agentic-ci-*` in your system temp directory.

---

## Diff / impact mapping issues

**Symptom:** Pipeline says `Changed files (1): ['README.md']` and falls back to full repo review.  
**Cause:** The last commit only touched non-code files (README, docs, etc.).  
**This is normal behaviour** — the pipeline automatically falls back to reviewing all tracked files. No action needed.

---

**Symptom:** `Review packs selected: []` — no packs run, 0 findings.  
**Cause:** The repo has no files matching the pack patterns (`.py`, `.ts`, `.tsx`, `.js`, `.java`).  
**Fix:** Add the relevant file extension to the review packs in `.agentic-ci/review-packs/*.yaml`:
```yaml
scope_selector:
  include_paths:
    - "**/*.go"   # add your language here
```

---

## Windows encoding errors

**Error:**
```
UnicodeDecodeError: 'charmap' codec can't decode byte ...
```
**Cause:** Git output contains non-ASCII characters and Windows is using the wrong encoding.  
**Fix:** This is already handled in the pipeline by forcing `utf-8` on all subprocess calls. If you still see this, make sure you have the latest version:
```bash
git pull origin main
```

---

## Reviewer returns 0 findings unexpectedly

**Possible causes:**
1. The files passed to the reviewer are too large and were truncated — check if the repo has very large files
2. The LLM genuinely found no issues in that pack category
3. The diff is empty — the reviewer received no meaningful content

**Debug:** Check `artifacts/<run-id>/run-events.json` for the review stage metadata showing how many raw findings came back per pack.

---

## Report or findings.json not written

**Error:**
```
[failed] ... permission denied
```
**Fix:** Make sure the `artifacts/` directory is writable:
```bash
mkdir -p artifacts
```
On Windows, check that no other process (like Explorer or an antivirus) is locking the directory.

---

## Pipeline crashes mid-run

The pipeline writes `run-events.json` after every stage transition. Even if it crashes, you can inspect what happened:

```bash
cat artifacts/<run-id>/run-events.json
```

Look for the last event — its `stage_id` and `status` show exactly where it stopped.
