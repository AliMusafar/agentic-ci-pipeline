# Fixture 03 — Missing Input Validation

**Category:** quality / security  
**Expected severity:** high  
**Auto-fixable:** yes (add null checks and 404 guard)

## What's wrong
1. `create_user` accesses `data["username"]` etc. without checking if the key exists.
   A missing field causes an unhandled `KeyError` and a 500 error.
2. `get_user` accesses `users[user_id]` without checking existence — same issue.

## Expected findings
- High: missing input validation in create_user — `autofixable: true`
- High: missing 404 guard in get_user — `autofixable: true`
