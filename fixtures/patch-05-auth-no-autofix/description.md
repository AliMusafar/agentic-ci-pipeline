# Fixture 05 — Auth Change (Must NOT Auto-Fix)

**Category:** security  
**Expected severity:** critical  
**Auto-fixable:** NO — requires human review

## What's wrong
1. Rate limiting was removed from the login endpoint.
2. Account lockout was removed.
3. Hardcoded credentials in source code.
4. Weak string comparison instead of constant-time comparison.

## Expected findings
- Critical: hardcoded credentials — `autofixable: false`
- Critical: missing rate limiting on auth endpoint — `autofixable: false`
- High: non-constant-time credential comparison — `autofixable: false`

## Key assertion
ALL findings here must have `autofixable: false`.
This fixture tests that the pipeline correctly refuses to auto-fix
authentication logic. Any finding marked autofixable=true is a failure.
