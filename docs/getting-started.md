# Getting Started with Autofiller Community Edition

Welcome! This guide will help you get up and running with Autofiller in minutes.

## What is Autofiller?

Autofiller is a document extraction platform that converts unstructured documents (PDFs, images, scans) into structured JSON data. It uses domain-specific "packs" to understand different document types like invoices, tax forms, receipts, and more.

## Prerequisites

- An API key (get one at [autofiller.dev](https://autofiller.dev))
- Node.js 18+ (for TypeScript SDK) or Python 3.9+ (for Python SDK)

## Installation

### TypeScript/Node.js

```bash
npm install @autofiller/sdk
```

### Python

```bash
pip install autofiller-sdk
```

## Quick Start

### 1. Set Your API Key

```bash
export AUTOFILLER_API_KEY="your-api-key"
```

### 2. Extract Data from a Document

**TypeScript:**

```typescript
import { AutofillerClient } from '@autofiller/sdk';

const client = new AutofillerClient({
  apiKey: process.env.AUTOFILLER_API_KEY!
});

async function extractInvoice() {
  const result = await client.extract({
    file: './invoice.pdf',
    domainPack: 'invoice-standard'
  });

  console.log('Vendor:', result.data.vendor_name);
  console.log('Amount:', result.data.total_amount);
  console.log('Confidence:', result.confidence);
}

extractInvoice();
```

**Python:**

```python
import os
from autofiller import AutofillerClient

client = AutofillerClient(api_key=os.environ['AUTOFILLER_API_KEY'])

result = client.extract(
    file='./invoice.pdf',
    domain_pack='invoice-standard'
)

print('Vendor:', result.data.get('vendor_name'))
print('Amount:', result.data.get('total_amount'))
print('Confidence:', result.confidence)
```

## Understanding the Response

The extraction result includes:

| Field | Description |
|-------|-------------|
| `id` | Unique extraction ID |
| `status` | `completed` or `partial` |
| `domainPack` | Pack used for extraction |
| `data` | Extracted structured fields |
| `confidence` | Per-field confidence scores (0-1) |
| `metadata` | Pages, processing time, model version |
| `warnings` | Any non-fatal issues |

Example response:

```json
{
  "id": "ext_abc123",
  "status": "completed",
  "domainPack": "invoice-standard",
  "data": {
    "vendor_name": "Acme Corporation",
    "invoice_number": "INV-2024-001",
    "invoice_date": "2024-01-15",
    "total_amount": 1234.56,
    "currency": "USD"
  },
  "confidence": {
    "vendor_name": 0.95,
    "invoice_number": 0.98,
    "invoice_date": 0.92,
    "total_amount": 0.99,
    "currency": 0.97
  },
  "metadata": {
    "pages": 1,
    "processingTimeMs": 1250,
    "modelVersion": "2024.1"
  }
}
```

## Choosing a Domain Pack

Domain packs are specialized extractors for different document types:

| Pack | Description | Use For |
|------|-------------|---------|
| `invoice-standard` | General invoices | Most invoices |
| `tax-w2` | IRS Form W-2 | US wage statements |
| `tax-1099` | IRS Form 1099 | US tax forms |
| `receipt-retail` | Retail receipts | Store receipts |

### Auto-Routing

If you don't specify a pack, Autofiller will automatically detect the document type:

```typescript
// Let Autofiller choose the best pack
const result = await client.extract({
  file: './document.pdf'
  // domainPack omitted - auto-routing enabled
});

console.log('Detected pack:', result.domainPack);
```

### List Available Packs

```typescript
const packs = await client.listDomainPacks();

for (const pack of packs) {
  console.log(`${pack.name}: ${pack.description}`);
}
```

## Handling Large Documents

For documents over 10 pages, use async extraction:

```typescript
// Start async job
const job = await client.extractAsync({
  file: './large-document.pdf'
});

console.log('Job started:', job.jobId);

// Wait for completion (polls automatically)
const result = await client.waitForJob(job.jobId);
console.log('Done:', result.data);
```

Or set up a webhook to be notified when complete:

```typescript
const job = await client.extractAsync({
  file: './large-document.pdf',
  webhookUrl: 'https://your-server.com/webhooks/autofiller'
});
```

## Error Handling

```typescript
import { 
  AutofillerClient, 
  AuthenticationError, 
  ValidationError,
  RateLimitError 
} from '@autofiller/sdk';

try {
  const result = await client.extract({ file: './doc.pdf' });
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error('Check your API key');
  } else if (error instanceof ValidationError) {
    console.error('Invalid request:', error.message);
  } else if (error instanceof RateLimitError) {
    console.error('Too many requests, slow down');
  }
}
```

## Next Steps

- 📖 [API Reference](../openapi/openapi.yaml) - Full API documentation
- 📦 [Domain Packs](../domain-packs/README.md) - Available packs and how to contribute
- 💻 [Examples](../examples/) - More code examples
- 🧪 [Eval Runner](../evals/runner/README.md) - Test pack quality locally

## Getting Help

- **Questions**: [GitHub Discussions](https://github.com/your-org/autofiller-community/discussions)
- **Bugs**: [GitHub Issues](https://github.com/your-org/autofiller-community/issues)
- **Security**: [Security Policy](../SECURITY.md)
