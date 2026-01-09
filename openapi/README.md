# OpenAPI Specification

This directory contains the OpenAPI 3.1 specification for the Autofiller Community Edition API.

## Files

- **openapi.yaml** - Full specification in YAML format (human-readable, for editing)
- **openapi.json** - Full specification in JSON format (for tooling/SDKs)

## Endpoints Overview

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (no auth required) |
| POST | `/extract` | Synchronous document extraction |
| POST | `/extract/async` | Start async extraction job |
| GET | `/jobs/{job_id}` | Poll async job status |
| GET | `/documents` | List processed documents |
| GET | `/documents/{id}` | Get document details |
| GET | `/domain-packs` | List available domain packs |
| GET | `/domain-packs/{name}` | Get domain pack schema |

## Using the Spec

### Generate SDK clients

```bash
# TypeScript
npx openapi-typescript openapi.yaml -o ../sdks/typescript/src/types.ts

# Python
openapi-python-client generate --path openapi.yaml --output-path ../sdks/python/
```

### Validate the spec

```bash
npx @redocly/cli lint openapi.yaml
```

### View interactive docs

```bash
npx @redocly/cli preview-docs openapi.yaml
```

## Versioning

The API follows semantic versioning:
- **v1** - Current stable version
- Breaking changes will increment the major version
- New fields/endpoints are added without version bump

## Contributing

When modifying the API spec:
1. Edit `openapi.yaml` (source of truth)
2. Run validation: `npx @redocly/cli lint openapi.yaml`
3. Generate JSON: `npx js-yaml openapi.yaml > openapi.json`
4. Update SDK types if needed
