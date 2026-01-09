# cURL Examples

Raw HTTP examples using cURL for the Autofiller API.

## Prerequisites

1. Set your API key:
   ```bash
   export AUTOFILLER_API_KEY="your-api-key"
   ```

2. Make scripts executable:
   ```bash
   chmod +x *.sh
   ```

## Examples

### Health Check (no auth required)

```bash
./04-health-check.sh
```

### Synchronous Extraction

```bash
./01-extract-sync.sh path/to/invoice.pdf
```

### Async Extraction with Polling

```bash
./02-extract-async.sh path/to/large-document.pdf
```

### List Domain Packs

```bash
./03-list-domain-packs.sh
```

## Quick Reference

### Extract (sync)

```bash
curl -X POST https://api.autofiller.dev/v1/extract \
  -H "Authorization: Bearer $AUTOFILLER_API_KEY" \
  -F "file=@document.pdf" \
  -F "domain_pack=invoice-standard"
```

### Extract (async)

```bash
# Start job
curl -X POST https://api.autofiller.dev/v1/extract/async \
  -H "Authorization: Bearer $AUTOFILLER_API_KEY" \
  -F "file=@document.pdf"

# Poll status
curl -X GET https://api.autofiller.dev/v1/jobs/{job_id} \
  -H "Authorization: Bearer $AUTOFILLER_API_KEY"
```

### List domain packs

```bash
curl -X GET https://api.autofiller.dev/v1/domain-packs \
  -H "Authorization: Bearer $AUTOFILLER_API_KEY"
```
