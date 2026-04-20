# Fixtures

Five replayable patch sets for testing the Agentic CI pipeline.
Each fixture is a small Python file with deliberate bugs.

| Fixture | Category | Severity | Auto-fixable |
|---------|----------|----------|--------------|
| patch-01-unused-imports | quality | low | yes |
| patch-02-eval-injection | security | critical + high | no (eval) / yes (debug) |
| patch-03-missing-validation | quality | high | yes |
| patch-04-bad-import | boundary | high | yes |
| patch-05-auth-no-autofix | security | critical | NO — human review required |

## How to run a fixture

Each fixture directory contains a `buggy.py` file. To run the pipeline
against a fixture, create a small git repo from it:

```bash
# One-time setup per fixture
cd fixtures/patch-02-eval-injection
git init
git add .
git commit -m "initial clean state"
cp buggy.py app.py
git add .
git commit -m "introduce bugs"
cd ../..

# Run the pipeline against it
python ci_pipeline.py --repo fixtures/patch-02-eval-injection
```

## Acceptance criteria

- patch-01: reviewer finds 3 unused import findings, all low severity
- patch-02: reviewer finds eval() as critical, debug=True as high
- patch-03: reviewer finds missing validation as high
- patch-04: reviewer finds boundary violation as high
- patch-05: reviewer finds auth issues as critical, ALL autofixable=false
