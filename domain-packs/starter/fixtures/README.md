# Starter Pack Fixtures

This directory contains test documents for the starter pack evaluation.

## Important: PII Policy

⚠️ **All fixtures must contain synthetic (fake) data only.**

- Do NOT commit real personal information
- Do NOT commit actual business documents
- Use generated/fake names, addresses, amounts
- Redact any real information if adapting real documents

## Fixture Requirements

Each fixture should:

1. Be a valid PDF, PNG, or JPG file
2. Be readable (good scan quality)
3. Match an eval case in `eval/cases.jsonl`
4. Have corresponding expected output in `eval/expected/`

## Creating Synthetic Fixtures

Options for creating test documents:

1. **Design tools**: Create in Figma, Canva, or similar
2. **Document generators**: Use faker libraries + PDF generation
3. **Anonymize real docs**: Heavily redact and replace all text
4. **Template filling**: Use Word/Docs templates with fake data

## File Naming

Use the pattern: `{pack}_{case_number}.{ext}`

Examples:
- `sample_001.pdf`
- `sample_002.pdf`
- `sample_003.png`
