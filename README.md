# Autofiller Community Edition

**Open-source document intelligence for structured data extraction**

[![CI](https://github.com/your-org/autofiller-community/workflows/CI/badge.svg)](https://github.com/your-org/autofiller-community/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Autofiller Community Edition is an open-source document extraction platform that turns unstructured documents (PDFs, images, scans) into structured JSON using domain-specific extraction packs. Built for developers who need reliable, high-quality data extraction without vendor lock-in.

## 🎯 What's Included

This repository contains:

- **OpenAPI Specification** – Complete API contract for document processing
- **SDKs** – Official TypeScript and Python client libraries
- **Domain Packs** – Pluggable extraction schemas + evaluation datasets
- **Eval Runner** – Local and CI-based quality measurement
- **Examples** – Working code samples for common use cases
- **Documentation** – Comprehensive guides and references

### What's NOT Included (Hosted Service)

The following components remain proprietary and are provided as a hosted service:

- Core extraction pipeline (ML models, training infrastructure)
- Production orchestration and scaling
- Credit/token management system

This **open-core** model ensures you can contribute to and benefit from shared extraction logic while we maintain the infrastructure.

## 🚀 Quickstart

### 1. Install the SDK

**TypeScript/Node.js:**
```bash
npm install @autofiller/sdk
```

**Python:**
```bash
pip install autofiller-sdk
```

### 2. Extract Data from a Document

**TypeScript:**
```typescript
import { AutofillerClient } from '@autofiller/sdk';

const client = new AutofillerClient({
  apiKey: process.env.AUTOFILLER_API_KEY
});

// Upload and extract
const result = await client.extract({
  file: './invoice.pdf',
  domainPack: 'invoice-standard'
});

console.log(result.data);
```

**Python:**
```python
from autofiller import AutofillerClient

client = AutofillerClient(api_key=os.environ['AUTOFILLER_API_KEY'])

# Upload and extract
result = client.extract(
    file='./invoice.pdf',
    domain_pack='invoice-standard'
)

print(result.data)
```

**cURL:**
```bash
# Upload document
curl -X POST https://api.autofiller.dev/v1/extract \\
  -H "Authorization: Bearer $AUTOFILLER_API_KEY" \\
  -F "file=@invoice.pdf" \\
  -F "domain_pack=invoice-standard"
```

## 📦 Domain Packs

Domain packs are the heart of Autofiller Community. Each pack defines:

- **Schema** – What fields to extract (JSON Schema)
- **Routing** – Document type detection rules
- **Eval Cases** – Test fixtures + expected outputs
- **Metrics** – Quality thresholds for acceptance

**Available Packs:**

| Pack | Description | Status |
|------|-------------|--------|
| `starter` | Example pack template | ✅ Stable |
| `invoice-standard` | General invoices | 🚧 Coming Soon |
| `tax-w2` | IRS Form W-2 | 🚧 Coming Soon |

### Contributing a Domain Pack

1. Copy `/domain-packs/starter` as a template
2. Define your schema in `schema.json`
3. Add test fixtures (synthetic or redacted only)
4. Add expected outputs
5. Run smoke eval: `python -m evals.runner.smoke_eval`
6. Submit PR with passing tests

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 🧪 Evaluation & Quality

Every domain pack must pass automated quality checks:

**Smoke Eval (PR CI):**
- Schema validation
- 1-3 quick test cases
- Fast feedback (<2 min)

**Full Eval (Nightly):**
- Complete test suite
- Accuracy metrics vs. thresholds
- Leaderboard updates

Run evals locally:

```bash
# Install eval runner
pip install -r evals/runner/requirements.txt

# Validate all packs
python -m evals.runner.validate_packs

# Run smoke eval
python -m evals.runner.smoke_eval

# Run full eval (requires API key)
python -m evals.runner.full_eval --pack tax-w2
```

## 🏗️ Repository Structure

```
autofiller-community/
├── openapi/               # API specification
│   ├── openapi.yaml
│   └── openapi.json
├── sdks/                  # Client libraries
│   ├── typescript/
│   └── python/
├── domain-packs/          # Extraction packs (community contributions!)
│   ├── pack.schema.json   # Pack manifest schema
│   └── starter/           # Template pack
├── evals/                 # Evaluation framework
│   └── runner/            # Python eval harness
├── examples/              # Usage examples
│   ├── curl/
│   ├── typescript/
│   └── python/
├── docs/                  # Documentation
│   └── getting-started.md
└── .github/
    ├── workflows/         # CI/CD
    └── ISSUE_TEMPLATE/    # Issue templates
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Good First Issues** – Check issues labeled [`good first issue`](https://github.com/your-org/autofiller-community/labels/good%20first%20issue)
2. **Domain Packs** – Most valuable contribution! See [domain-packs/README.md](domain-packs/README.md)
3. **SDK Improvements** – Enhancements to TypeScript/Python clients
4. **Docs & Examples** – Tutorials, guides, sample code

Read our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

## 📖 Documentation

- [Getting Started Guide](docs/getting-started.md)
- [Domain Pack Specification](domain-packs/README.md)
- [API Reference](openapi/openapi.yaml)
- [Eval Runner Guide](evals/runner/README.md)

## 💬 Community & Support

- **GitHub Issues** – Bug reports and feature requests
- **GitHub Discussions** – Questions and community chat
- **Discord** – Real-time community (coming soon)

See [SUPPORT.md](SUPPORT.md) for help.

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

Inspired by the community-first approach of:
- [Airbyte](https://github.com/airbytehq/airbyte) – Modular connector architecture
- [Supabase](https://github.com/supabase/supabase) – Open-core done right

---

**Ready to extract better data?** Star this repo, contribute a domain pack, or [get your API key](https://autofiller.dev) to start building.
