# Documentation

Comprehensive documentation for Autofiller Community Edition.

## Guides

- [Getting Started](./getting-started.md) - Quick start guide
- [Domain Pack Specification](../domain-packs/README.md) - How to create and contribute packs
- [Evaluation Guide](../evals/runner/README.md) - Testing and quality measurement

## References

- [API Reference](../openapi/openapi.yaml) - OpenAPI 3.1 specification
- [TypeScript SDK](../sdks/typescript/README.md) - Node.js/TypeScript client
- [Python SDK](../sdks/python/README.md) - Python client

## Examples

- [cURL Examples](../examples/curl/) - Raw HTTP examples
- [TypeScript Examples](../examples/typescript/) - Node.js examples
- [Python Examples](../examples/python/) - Python examples

## Contributing

- [Contributing Guide](../CONTRIBUTING.md) - How to contribute
- [Code of Conduct](../CODE_OF_CONDUCT.md) - Community guidelines

## Architecture

### How Autofiller Works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Document   │────▶│   Autofiller │────▶│  Structured     │
│  (PDF/IMG)  │     │   API        │     │  JSON Output    │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Domain Pack  │
                    │ (Schema +    │
                    │  Routing)    │
                    └──────────────┘
```

### Domain Pack Flow

1. **Routing** - Document is analyzed to determine type
2. **Pack Selection** - Best matching domain pack is selected
3. **Extraction** - Fields are extracted according to pack schema
4. **Validation** - Output is validated against JSON Schema
5. **Scoring** - Confidence scores are calculated per field

### Open-Core Model

| Open Source (This Repo) | Hosted Service |
|------------------------|----------------|
| OpenAPI specification | Core extraction models |
| TypeScript & Python SDKs | Training infrastructure |
| Domain pack definitions | Production orchestration |
| Eval runner & metrics | Credit/token management |
| Examples & documentation | SLA & support |

## Versioning

- **API**: Follows semantic versioning with `/v1/` prefix
- **SDKs**: Semantic versioning, tracks API compatibility
- **Domain Packs**: Individual semantic versions per pack
