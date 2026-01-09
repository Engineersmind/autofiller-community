# autofiller-sdk

Official Python SDK for Autofiller Community Edition.

## Installation

```bash
pip install autofiller-sdk
```

## Quick Start

```python
from autofiller import AutofillerClient

client = AutofillerClient(api_key="your-api-key")

# Extract data from a document
result = client.extract(
    file="./invoice.pdf",
    domain_pack="invoice-standard"
)

print(result.data)
# {
#     "vendor_name": "Acme Corp",
#     "invoice_number": "INV-2024-001",
#     "total_amount": 1500.00,
#     ...
# }
```

## Features

- **Synchronous and async clients** - Choose based on your application
- **Type hints throughout** - Full IDE autocompletion
- **Pydantic models** - Validated response types
- **Automatic retries** - Built-in retry logic for transient failures

## Usage

### Configuration

```python
client = AutofillerClient(
    api_key="your-api-key",
    base_url="https://custom.api.com",  # Optional, for self-hosted
    timeout=60.0,                        # Optional, request timeout (seconds)
    max_retries=3                        # Optional, retry count
)
```

### Synchronous Extraction

```python
from autofiller import AutofillerClient

client = AutofillerClient(api_key="your-api-key")

# Basic extraction
result = client.extract(file="./document.pdf")

# With options
result = client.extract(
    file="./document.pdf",
    domain_pack="invoice-standard",
    include_confidence=True,
    include_bounding_boxes=True,
    language="en"
)

print(result.data)           # Extracted fields
print(result.confidence)     # Field confidence scores
print(result.metadata.pages) # Page count
```

### Async Extraction

For large documents or when you want webhook notifications:

```python
# Start async job
job = client.extract_async(
    file="./large-document.pdf",
    domain_pack="tax-w2",
    webhook_url="https://your-server.com/webhooks/autofiller"
)

print(job["job_id"])

# Wait for completion (polls automatically)
result = client.wait_for_job(
    job["job_id"],
    poll_interval=2.0,  # Check every 2 seconds
    max_wait=300.0      # Give up after 5 minutes
)
```

### Manual Polling

```python
job = client.extract_async(file="./doc.pdf")

import time
while True:
    status = client.get_job(job["job_id"])
    
    if status.status == "completed":
        print(status.result.data)
        break
    
    if status.status == "failed":
        print(status.error)
        break
    
    print(f"Progress: {status.progress}%")
    time.sleep(2)
```

### Async Client (asyncio)

```python
import asyncio
from autofiller import AsyncAutofillerClient

async def main():
    async with AsyncAutofillerClient(api_key="your-api-key") as client:
        result = await client.extract(file="./invoice.pdf")
        print(result.data)

asyncio.run(main())
```

### List Domain Packs

```python
packs = client.list_domain_packs()

for pack in packs:
    print(f"{pack.name} v{pack.version}: {pack.description}")

# Get details for a specific pack
invoice_pack = client.get_domain_pack("invoice-standard")
print(invoice_pack.schema_)  # JSON Schema for extracted fields
```

### Health Check

```python
health = client.health()
print(health.status)   # 'healthy' | 'degraded' | 'unhealthy'
print(health.version)  # API version
```

## Error Handling

```python
from autofiller import (
    AutofillerClient,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    AutofillerError,
)

client = AutofillerClient(api_key="your-api-key")

try:
    result = client.extract(file="./doc.pdf")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except RateLimitError:
    print("Rate limited, retry later")
except AutofillerError as e:
    print(f"Error [{e.code}]: {e.message}")
```

## File Input Types

The SDK accepts multiple file input types:

```python
# File path (string or Path)
result = client.extract(file="./invoice.pdf")
result = client.extract(file=Path("./invoice.pdf"))

# Bytes
with open("./invoice.pdf", "rb") as f:
    data = f.read()
result = client.extract(file=data, filename="invoice.pdf")

# File-like object
with open("./invoice.pdf", "rb") as f:
    result = client.extract(file=f)
```

## Context Manager

Use the client as a context manager to ensure proper cleanup:

```python
with AutofillerClient(api_key="your-api-key") as client:
    result = client.extract(file="./doc.pdf")
# Client is automatically closed
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src

# Linting
ruff check src
```

## License

MIT
