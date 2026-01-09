# AI Models

This directory contains the AI model training infrastructure for Autofiller's document understanding and form autofilling capabilities.

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Autofiller AI Pipeline                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐    ┌──────────────────┐    ┌───────────────────┐   │
│  │ PDF Input   │───▶│ Document         │───▶│ Field Extraction  │   │
│  │             │    │ Understanding    │    │ Model             │   │
│  └─────────────┘    └──────────────────┘    └───────────────────┘   │
│                              │                        │              │
│                              ▼                        ▼              │
│                     ┌──────────────────┐    ┌───────────────────┐   │
│                     │ Structure        │    │ Extracted         │   │
│                     │ Analysis         │    │ Fields + Values   │   │
│                     └──────────────────┘    └───────────────────┘   │
│                              │                        │              │
│                              ▼                        ▼              │
│                     ┌──────────────────┐    ┌───────────────────┐   │
│                     │ Persona Engine   │    │ Capture Logic     │   │
│                     │ (Smart Questions)│    │ (Form Mapping)    │   │
│                     └──────────────────┘    └───────────────────┘   │
│                              │                        │              │
│                              ▼                        ▼              │
│                     ┌────────────────────────────────────────────┐  │
│                     │           Autofilled Form Output           │  │
│                     └────────────────────────────────────────────┘  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Model Components

### 1. Document Understanding (`document-understanding/`)

The foundation model that comprehends PDF structure:

- **Layout Analysis**: Identifies headers, tables, paragraphs, form fields
- **Text Extraction**: OCR with spatial awareness
- **Semantic Segmentation**: Groups related content blocks
- **Document Classification**: Determines document type

### 2. Field Extraction (`field-extraction/`)

Extracts specific field values from understood documents:

- **Named Entity Recognition**: Identifies dates, amounts, names, addresses
- **Table Parsing**: Extracts structured tabular data
- **Key-Value Extraction**: Matches labels to values
- **Confidence Scoring**: Per-field confidence metrics

### 3. Question Generation (`question-generation/`)

Generates persona-appropriate questions for missing/ambiguous data:

- **Gap Detection**: Identifies fields that couldn't be extracted
- **Context-Aware Prompting**: Considers what's already known
- **Persona Adaptation**: Adjusts language per user persona
- **Disambiguation**: Resolves conflicting or unclear values

### 4. Capture Logic (`capture-logic/`)

Maps extracted data to target form fields:

- **Field Mapping**: Source PDF field → Target form field
- **Transformation Rules**: Format conversions, calculations
- **Validation**: Business rule enforcement
- **Conflict Resolution**: Handles multiple sources

## Directory Structure

```
models/
├── document-understanding/
│   ├── config/
│   │   ├── model_config.yaml      # Model architecture config
│   │   └── training_config.yaml   # Training hyperparameters
│   ├── training/
│   │   ├── train.py               # Training script
│   │   ├── dataset.py             # Data loading
│   │   └── augmentations.py       # Data augmentation
│   └── inference/
│       ├── predict.py             # Inference script
│       └── postprocess.py         # Output processing
│
├── field-extraction/
│   ├── config/
│   ├── training/
│   └── inference/
│
├── question-generation/
│   ├── config/
│   ├── prompts/                   # Prompt templates
│   └── inference/
│
└── shared/
    ├── utils/                     # Common utilities
    ├── evaluation/                # Model evaluation
    └── export/                    # Model export (ONNX, TensorRT)
```

## Training a Model

### Prerequisites

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r models/requirements.txt
```

### Train Document Understanding Model

```bash
python -m models.document_understanding.training.train \
  --config models/document-understanding/config/training_config.yaml \
  --data-dir data/training/documents \
  --output-dir outputs/document-understanding
```

### Train Field Extraction Model

```bash
python -m models.field_extraction.training.train \
  --config models/field-extraction/config/training_config.yaml \
  --data-dir data/training/annotations \
  --output-dir outputs/field-extraction
```

## Model Evaluation

```bash
# Evaluate document understanding accuracy
python -m models.shared.evaluation.run_eval \
  --model document-understanding \
  --checkpoint outputs/document-understanding/best.pt \
  --test-data data/test/documents

# Evaluate field extraction accuracy
python -m models.shared.evaluation.run_eval \
  --model field-extraction \
  --checkpoint outputs/field-extraction/best.pt \
  --test-data data/test/annotations
```

## Contributing Models

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on:

- Training data requirements (PII policies)
- Model architecture standards
- Evaluation benchmarks
- Submission process

## Open-Core Boundary

| Community (This Repo) | Hosted Service |
|-----------------------|----------------|
| Model architectures | Pre-trained weights |
| Training scripts | Large-scale training infra |
| Evaluation framework | Production inference |
| Config schemas | GPU cluster management |
