# @autofiller/sdk

Official TypeScript/JavaScript SDK for Autofiller Community Edition.

## Installation

```bash
npm install @autofiller/sdk
```

## Quick Start

```typescript
import { AutofillerClient } from '@autofiller/sdk';

const client = new AutofillerClient({
  apiKey: process.env.AUTOFILLER_API_KEY!
});

// Extract data from a document
const result = await client.extract({
  file: './invoice.pdf',
  domainPack: 'invoice-standard'
});

console.log(result.data);
// {
//   vendor_name: "Acme Corp",
//   invoice_number: "INV-2024-001",
//   total_amount: 1500.00,
//   ...
// }
```

## Features

- **Synchronous extraction** - For small documents (<10 pages)
- **Async extraction** - For large documents with polling or webhooks
- **Domain pack routing** - Auto-detect document type or specify explicitly
- **TypeScript-first** - Full type definitions included
- **Error handling** - Typed errors for different failure modes

## Usage

### Configuration

```typescript
const client = new AutofillerClient({
  apiKey: 'your-api-key',           // Required
  baseUrl: 'https://custom.api.com', // Optional, for self-hosted
  timeout: 60000,                    // Optional, request timeout (ms)
  maxRetries: 3                      // Optional, retry count
});
```

### Synchronous Extraction

Best for small documents that process quickly:

```typescript
const result = await client.extract({
  file: './document.pdf',
  domainPack: 'invoice-standard',
  includeConfidence: true,
  includeBoundingBoxes: false,
  language: 'en'
});

console.log(result.data);           // Extracted fields
console.log(result.confidence);     // Field confidence scores
console.log(result.metadata.pages); // Page count
```

### Async Extraction

For large documents or when you want webhook notifications:

```typescript
// Start async job
const job = await client.extractAsync({
  file: './large-document.pdf',
  domainPack: 'tax-w2',
  webhookUrl: 'https://your-server.com/webhooks/autofiller'
});

console.log(job.jobId); // Use this to poll for status

// Poll for completion
const result = await client.waitForJob(job.jobId, {
  pollInterval: 2000,  // Check every 2 seconds
  maxWait: 300000      // Give up after 5 minutes
});
```

### Manual Polling

```typescript
const job = await client.extractAsync({ file: './doc.pdf' });

// Poll manually
while (true) {
  const status = await client.getJob(job.jobId);
  
  if (status.status === 'completed') {
    console.log(status.result?.data);
    break;
  }
  
  if (status.status === 'failed') {
    console.error(status.error?.message);
    break;
  }
  
  console.log(`Progress: ${status.progress}%`);
  await new Promise(r => setTimeout(r, 2000));
}
```

### List Domain Packs

```typescript
const packs = await client.listDomainPacks();

for (const pack of packs) {
  console.log(`${pack.name} v${pack.version}: ${pack.description}`);
}

// Get details for a specific pack
const invoicePack = await client.getDomainPack('invoice-standard');
console.log(invoicePack.schema); // JSON Schema for extracted fields
```

### Health Check

```typescript
const health = await client.health();
console.log(health.status);  // 'healthy' | 'degraded' | 'unhealthy'
console.log(health.version); // API version
```

## Error Handling

```typescript
import { 
  AutofillerClient,
  AuthenticationError,
  ValidationError,
  RateLimitError,
  AutofillerError 
} from '@autofiller/sdk';

try {
  const result = await client.extract({ file: './doc.pdf' });
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error('Invalid API key');
  } else if (error instanceof ValidationError) {
    console.error('Invalid request:', error.message);
  } else if (error instanceof RateLimitError) {
    console.error('Rate limited, retry later');
  } else if (error instanceof AutofillerError) {
    console.error(`Error [${error.code}]: ${error.message}`);
  }
}
```

## TypeScript Support

The SDK includes full type definitions. For domain-specific typing:

```typescript
import { AutofillerClient, ExtractionData } from '@autofiller/sdk';

// Typed extraction result
const result = await client.extract<ExtractionData.Invoice>({
  file: './invoice.pdf',
  domainPack: 'invoice-standard'
});

// result.data is typed as ExtractionData.Invoice
console.log(result.data.total_amount);
console.log(result.data.vendor_name);
```

## Browser Usage

The SDK works in browsers with a bundler (webpack, vite, etc.):

```typescript
// Use Blob/File instead of file path
const file = document.querySelector('input[type="file"]').files[0];

const result = await client.extract({
  file: file,
  filename: file.name,
  domainPack: 'invoice-standard'
});
```

## License

MIT
