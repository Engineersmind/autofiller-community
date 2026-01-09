# Eval Runner

Python-based evaluation framework for Autofiller domain packs.

## Overview

The eval runner provides:

- **Pack Validation** - Verify pack structure and schema
- **Smoke Eval** - Quick tests for PR CI (1-3 cases)
- **Full Eval** - Complete test suite (nightly/manual)
- **Metrics Calculation** - Accuracy, field matching, scores

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Validate All Packs

```bash
python -m evals.runner.validate_packs
```

### Validate Specific Pack

```bash
python -m evals.runner.validate_packs --pack starter
```

### Run Smoke Eval

Quick evaluation for CI (runs 1-3 cases per pack):

```bash
# All packs
python -m evals.runner.smoke_eval

# Specific pack
python -m evals.runner.smoke_eval --pack starter

# Only changed packs (for PR CI)
python -m evals.runner.smoke_eval --changed-only
```

### Run Full Eval

Complete evaluation suite (requires API access):

```bash
# All packs
python -m evals.runner.full_eval

# Specific pack
python -m evals.runner.full_eval --pack starter

# With custom API endpoint
python -m evals.runner.full_eval --api-url https://sandbox.autofiller.dev/v1
```

## Modes

### Recorded Mode (Default for Smoke)

Uses pre-recorded model outputs stored in `eval/recorded/`. No API calls needed.

- Deterministic results
- Works offline
- Good for PR CI

### Live Mode

Calls the actual Autofiller API to get extraction results.

- Measures real accuracy
- Requires API key
- Used for nightly/release evals

```bash
# Enable live mode
python -m evals.runner.smoke_eval --live

# Set API key
export AUTOFILLER_API_KEY="your-key"
```

## Output

### Console Report

```
=== Eval Results: starter ===
Cases: 3
Passed: 3
Failed: 0
Score: 0.95

Field Metrics:
  document_id: 100% exact match
  document_date: 100% exact match
  title: 95% fuzzy match
  amount: 100% within tolerance
```

### JSON Report

```bash
python -m evals.runner.full_eval --output results.json
```

### CI Integration

Exit code indicates pass/fail for CI:
- `0` - All packs pass thresholds
- `1` - One or more packs failed

## Adding Tests

1. Add fixture to `domain-packs/{pack}/fixtures/`
2. Add expected output to `domain-packs/{pack}/eval/expected/`
3. Add case to `domain-packs/{pack}/eval/cases.jsonl`
4. (Optional) Add recorded output to `domain-packs/{pack}/eval/recorded/`

## Configuration

See `eval/metrics.yaml` in each pack for threshold configuration.
