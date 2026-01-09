# Capture Logic

Capture logic defines how extracted PDF data maps to target form fields and the rules for transforming, validating, and filling form values.

## Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ Extracted Data  │────▶│ Capture Logic    │────▶│ Filled Form         │
│ from PDF        │     │ Rules Engine     │     │ Fields              │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
        │                       │
        │               ┌───────┴───────┐
        │               │               │
        ▼               ▼               ▼
   ┌─────────┐   ┌───────────┐   ┌───────────┐
   │ Source  │   │ Transform │   │ Validate  │
   │ Mapping │   │ Rules     │   │ Rules     │
   └─────────┘   └───────────┘   └───────────┘
```

## Key Concepts

### 1. Field Mapping
Maps extracted PDF fields to target form fields.

```yaml
mappings:
  - source: vendor_name
    target: form.payee_name
    
  - source: invoice_total
    target: form.amount
    transform: format_currency
```

### 2. Transform Rules
Convert values between formats.

```yaml
transforms:
  - name: format_date
    type: date
    input_formats: ["MM/DD/YYYY", "YYYY-MM-DD", "DD-MMM-YYYY"]
    output_format: "YYYY-MM-DD"
    
  - name: format_currency
    type: number
    decimal_places: 2
    remove_symbols: ["$", ","]
```

### 3. Validation Rules
Ensure filled values meet requirements.

```yaml
validations:
  - field: ssn
    pattern: "^\\d{3}-\\d{2}-\\d{4}$"
    error: "SSN must be in format XXX-XX-XXXX"
    
  - field: amount
    type: number
    min: 0
    max: 999999999.99
```

### 4. Computed Fields
Calculate values from other fields.

```yaml
computed:
  - field: total_tax
    formula: "federal_tax + state_tax + local_tax"
    
  - field: net_pay
    formula: "gross_pay - total_deductions"
```

## Directory Structure

```
capture-logic/
├── README.md                    # This file
├── logic.schema.json           # JSON Schema for capture rules
├── transforms/
│   ├── dates.yaml              # Date transformation rules
│   ├── currency.yaml           # Currency transformation rules
│   ├── addresses.yaml          # Address parsing/formatting
│   └── identifiers.yaml        # SSN, EIN, etc.
├── validations/
│   ├── common.yaml             # Common validation patterns
│   └── us-tax.yaml             # US tax form validations
└── patterns/
    ├── invoice-to-ap.yaml      # Invoice → AP form pattern
    ├── w2-to-1040.yaml         # W2 → 1040 pattern
    └── receipt-to-expense.yaml # Receipt → Expense report
```

## Creating Capture Rules

### Example: Invoice to Payment Form

```yaml
# capture-logic/patterns/invoice-to-payment.yaml
id: invoice-to-payment
name: Invoice to Payment Form
description: Maps extracted invoice data to payment processing form

source_pack: invoice-standard
target_form: payment-request

mappings:
  # Direct mappings
  - source: vendor_name
    target: payee_name
    required: true
    
  - source: vendor_address
    target: payee_address
    transform: format_address
    
  # Transformed mappings  
  - source: invoice_total
    target: payment_amount
    transform: format_currency
    validation: positive_amount
    
  - source: invoice_date
    target: invoice_date
    transform: format_date_iso
    
  - source: due_date
    target: payment_due_date
    transform: format_date_iso
    fallback:
      compute: "invoice_date + 30 days"

computed:
  - field: payment_reference
    formula: "concat(vendor_id, '-', invoice_number)"

validations:
  - field: payment_amount
    rules:
      - type: required
      - type: positive
      - type: max
        value: 100000
        error: "Amounts over $100,000 require manual approval"

defaults:
  - field: payment_method
    value: "ACH"
    
  - field: currency
    value: "USD"
    when:
      condition: "currency is null"
```

## Validation

Validate capture logic files:

```bash
python -m evals.runner.validate_packs --capture-logic
```

## Integration with Domain Packs

Domain packs can include capture logic:

```yaml
# domain-packs/invoice-standard/pack.yaml
capture_logic:
  - pattern: invoice-to-payment
    target_forms:
      - payment-request
      - ap-voucher
```

## API Usage

```python
from autofiller import CaptureEngine

engine = CaptureEngine()

# Load capture rules
engine.load_pattern("invoice-to-payment")

# Apply to extracted data
extracted_data = {
    "vendor_name": "Acme Corp",
    "invoice_total": "$1,234.56",
    "invoice_date": "01/15/2024"
}

# Get filled form data
form_data = engine.apply(extracted_data)
# {
#     "payee_name": "Acme Corp",
#     "payment_amount": 1234.56,
#     "invoice_date": "2024-01-15",
#     "payment_method": "ACH",
#     "currency": "USD"
# }
```
