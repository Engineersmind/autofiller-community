# Examples

This directory contains working examples demonstrating how to use the Autofiller API.

## Quick Start

| Example | Description |
|---------|-------------|
| [curl/](./curl/) | Raw HTTP examples using cURL |
| [typescript/](./typescript/) | TypeScript/Node.js examples |
| [python/](./python/) | Python examples |

## Common Workflows

### 1. Basic Document Extraction

Extract structured data from a single document:

- [cURL example](./curl/01-extract-sync.sh)
- [TypeScript example](./typescript/src/01-basic-extraction.ts)
- [Python example](./python/01_basic_extraction.py)

### 2. Async Processing (Large Documents)

Handle large documents with async jobs:

- [cURL example](./curl/02-extract-async.sh)
- [TypeScript example](./typescript/src/02-async-extraction.ts)
- [Python example](./python/02_async_extraction.py)

### 3. Batch Processing

Process multiple documents efficiently:

- [TypeScript example](./typescript/src/03-batch-processing.ts)
- [Python example](./python/03_batch_processing.py)

## Prerequisites

1. Get an API key at https://autofiller.dev
2. Set your API key as an environment variable:

```bash
export AUTOFILLER_API_KEY="your-api-key"
```

## Running Examples

### cURL

```bash
cd curl
chmod +x *.sh
./01-extract-sync.sh
```

### TypeScript

```bash
cd typescript
npm install
npx tsx src/01-basic-extraction.ts
```

### Python

```bash
cd python
pip install autofiller-sdk
python 01_basic_extraction.py
```
