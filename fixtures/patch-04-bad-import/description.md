# Fixture 04 — Module Boundary Violation

**Category:** boundary  
**Expected severity:** high  
**Auto-fixable:** yes (change to public API imports)

## What's wrong
Code imports from `auth._internal.*` — the `_internal` namespace signals
these are private implementation details not meant for direct use.
The correct approach is to import from `auth`'s public API.

## Expected findings
- High: importing from private `_internal` module — `autofixable: true`
- Boundary violation should reference the two bad import lines specifically
