# Fixture 02 — eval() Injection + debug=True

**Category:** security  
**Expected severity:** critical (eval), high (debug=True)  
**Auto-fixable:** eval → no (requires design decision); debug → yes

## What's wrong
1. `eval(expression)` executes user-supplied input as Python code — Remote Code Execution.
2. `app.run(debug=True)` enables Flask debug mode in what looks like production code.

## Expected findings
- Critical: RCE via eval() with user input — `autofixable: false`
- High: debug=True in production — `autofixable: true`

## What must NOT happen
The pipeline must not attempt to fix the eval() call automatically.
It requires a product decision (redesign the endpoint logic).
