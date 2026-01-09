---
name: New Domain Pack
about: Propose or submit a new domain pack
title: '[Domain Pack] '
labels: ['domain-pack', 'triage']
assignees: ''
---

## Domain Pack Overview

**Pack Name**: (e.g., `invoice-international`, `tax-1099`)

**Document Type**: What type of documents does this pack extract data from?

**Description**: Brief description of what this pack does.

## Target Fields

List the key fields this pack will extract:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `example_field` | string | Yes | Description |
| `another_field` | number | No | Description |

## Document Examples

What documents are covered by this pack?

- [ ] Example document type 1
- [ ] Example document type 2

## Implementation Status

- [ ] I am proposing this pack for someone else to implement
- [ ] I am working on implementing this pack
- [ ] I have a working implementation ready for review

## Test Fixtures

How will you provide test fixtures?

- [ ] I will create synthetic/fake test documents
- [ ] I will redact real documents
- [ ] I need help generating test fixtures

## Checklist

For pack submissions:

- [ ] `pack.yaml` is valid and complete
- [ ] `schema.json` is valid JSON Schema
- [ ] At least 5 eval cases provided
- [ ] All fixtures contain synthetic/redacted data only
- [ ] Smoke eval passes locally
- [ ] README documents the pack

## Additional Context

Add any other context about the domain pack here.
