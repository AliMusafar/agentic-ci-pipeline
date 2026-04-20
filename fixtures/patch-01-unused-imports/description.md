# Fixture 01 — Unused Imports

**Category:** quality  
**Expected severity:** low  
**Auto-fixable:** yes

## What's wrong
Three imports (`requests`, `sys`, `hashlib`) are imported but never used.

## Expected finding
The reviewer should flag all three unused imports with severity `low`
and `autofixable: true`.

## What must NOT happen
The pipeline must not auto-fix this in Milestone 1 (read-only run).
The fix would be to remove the three unused import lines.
