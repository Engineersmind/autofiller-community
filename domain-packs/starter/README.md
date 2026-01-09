# Starter Pack

Example domain pack demonstrating the pack structure and conventions.

## Overview

This is a template pack that you can copy to create your own domain packs.

## Schema

The starter pack extracts these fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | string | ✅ | Unique identifier |
| `document_date` | date | ✅ | Document date |
| `title` | string | ✅ | Document title |
| `description` | string | | Summary |
| `amount` | number | | Monetary amount |
| `currency` | string | | Currency code |
| `sender` | object | | Sender info |
| `recipient` | object | | Recipient info |
| `line_items` | array | | Line items |
| `notes` | string | | Additional notes |

## Usage

```typescript
const result = await client.extract({
  file: './document.pdf',
  domainPack: 'starter'
});
```

## Contributing

To improve this pack:

1. Add more test fixtures
2. Improve the schema
3. Add edge case handling
4. Update metrics thresholds

See [domain-packs/README.md](../README.md) for contribution guidelines.
