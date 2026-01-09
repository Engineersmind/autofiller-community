# SDKs

Official client libraries for the Autofiller Community Edition API.

## Available SDKs

| SDK | Status | Installation |
|-----|--------|--------------|
| [TypeScript/JavaScript](./typescript/) | ✅ Stable | `npm install @autofiller/sdk` |
| [Python](./python/) | ✅ Stable | `pip install autofiller-sdk` |

## Quick Comparison

### TypeScript

```typescript
import { AutofillerClient } from '@autofiller/sdk';

const client = new AutofillerClient({ apiKey: process.env.AUTOFILLER_API_KEY });

const result = await client.extract({
  file: './invoice.pdf',
  domainPack: 'invoice-standard'
});

console.log(result.data);
```

### Python

```python
from autofiller import AutofillerClient

client = AutofillerClient(api_key=os.environ['AUTOFILLER_API_KEY'])

result = client.extract(
    file='./invoice.pdf',
    domain_pack='invoice-standard'
)

print(result.data)
```

## Feature Matrix

| Feature | TypeScript | Python |
|---------|------------|--------|
| Sync extraction | ✅ | ✅ |
| Async extraction | ✅ | ✅ |
| Job polling | ✅ | ✅ |
| Webhooks | ✅ | ✅ |
| Type definitions | ✅ | ✅ (Pydantic) |
| Async client | ✅ (native) | ✅ (AsyncAutofillerClient) |
| Retry logic | ✅ | ✅ |
| Streaming | 🚧 Planned | 🚧 Planned |

## Contributing

We welcome SDK improvements! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### Adding a New SDK

If you'd like to contribute an SDK for another language:

1. Follow the API contract in `/openapi/openapi.yaml`
2. Implement all endpoints (health, extract, extract/async, jobs, domain-packs)
3. Include proper error handling
4. Add comprehensive tests
5. Write clear documentation with examples
6. Submit a PR with the `sdk` label
