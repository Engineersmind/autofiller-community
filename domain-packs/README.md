# Domain Packs

Domain packs are the heart of Autofiller Community Edition. Each pack defines how to extract structured data from a specific document type.

## What is a Domain Pack?

A domain pack is a modular unit containing:

| Component | File | Purpose |
|-----------|------|---------|
| **Manifest** | `pack.yaml` | Metadata, routing rules, constraints |
| **Schema** | `schema.json` | JSON Schema defining extracted fields |
| **Eval Cases** | `eval/cases.jsonl` | Test fixtures for quality measurement |
| **Expected Outputs** | `eval/expected/` | Ground truth for test cases |
| **Metrics** | `eval/metrics.yaml` | Quality thresholds for acceptance |

## Available Packs

| Pack | Description | Status |
|------|-------------|--------|
| [`starter`](./starter/) | Example template pack | ✅ Stable |
| `invoice-standard` | General invoices | 🚧 Coming Soon |
| `tax-w2` | IRS Form W-2 | 🚧 Coming Soon |
| `tax-1099` | IRS Form 1099 | 🚧 Coming Soon |
| `receipt-retail` | Retail receipts | 🚧 Coming Soon |

## Contributing a Domain Pack

### 1. Create Pack Structure

```bash
# Copy the starter template
cp -r starter my-pack-name
cd my-pack-name
```

### 2. Define Your Schema

Edit `schema.json` with the fields you want to extract:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "vendor_name": {
      "type": "string",
      "description": "Company or vendor name"
    },
    "total_amount": {
      "type": "number",
      "description": "Total amount due"
    }
  },
  "required": ["vendor_name", "total_amount"]
}
```

### 3. Configure Routing

Edit `pack.yaml` with keywords/anchors that identify your document type:

```yaml
routing:
  keywords:
    - "Invoice"
    - "Bill To"
  anchors:
    - "Total Due"
    - "Amount Owing"
```

### 4. Add Test Fixtures

⚠️ **Important**: Only use synthetic or redacted data. Never commit real PII.

Add test documents to `fixtures/`:
- Use fake/generated data
- Redact any real information
- Include edge cases (multi-page, poor scan quality, etc.)

### 5. Add Expected Outputs

For each fixture, create expected output in `eval/expected/`:

```json
{
  "vendor_name": "Acme Corporation",
  "total_amount": 1234.56
}
```

### 6. Configure Metrics

Edit `eval/metrics.yaml` with quality thresholds:

```yaml
thresholds:
  required_present_rate: 0.95  # 95% of required fields extracted
  exact_match_rate: 0.80       # 80% exact string matches
```

### 7. Validate & Test

```bash
# Validate pack structure
python -m evals.runner.validate_packs --pack my-pack-name

# Run smoke eval
python -m evals.runner.smoke_eval --pack my-pack-name
```

### 8. Submit PR

- Ensure all CI checks pass
- Include description of document type
- Note any special considerations

## Pack Specification

See [pack.schema.json](./pack.schema.json) for the full manifest schema.

### pack.yaml Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Unique pack identifier (kebab-case) |
| `version` | string | ✅ | Semantic version |
| `description` | string | ✅ | Human-readable description |
| `owners` | array | ✅ | GitHub usernames of maintainers |
| `schema` | string | ✅ | Path to JSON Schema file |
| `routing.keywords` | array | | Keywords for document detection |
| `routing.anchors` | array | | Text anchors for confidence |
| `eval.cases` | string | ✅ | Path to eval cases file |
| `eval.expected_dir` | string | ✅ | Directory with expected outputs |
| `eval.metrics` | string | ✅ | Path to metrics config |
| `constraints.pii_policy` | string | ✅ | `synthetic-or-redacted-only` |
| `constraints.max_pages` | number | | Maximum supported pages |

## Quality Standards

All domain packs must meet these requirements:

1. **PII Policy**: Only synthetic or properly redacted test data
2. **Minimum Cases**: At least 5 eval cases
3. **Pass Thresholds**: Meet configured metric thresholds
4. **Schema Validity**: Valid JSON Schema draft-07
5. **Documentation**: Clear description in pack.yaml

## CI Integration

Every PR touching domain packs runs:

1. **Validation** - Schema and manifest checks
2. **Smoke Eval** - Quick test on 1-3 cases
3. **Full Eval** (nightly) - Complete test suite

See [GitHub Workflows](../.github/workflows/) for details.
