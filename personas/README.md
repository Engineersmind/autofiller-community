# Personas (Document Filler Profiles)

Personas represent **types of users who fill PDFs**. Each persona captures the filling logic, patterns, and domain knowledge that a specific role uses when completing documents. The AI learns from each persona and can be reused for similar document filling tasks.

## Concept

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PERSONA = USER TYPE + FILLING LOGIC                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌──────────────────────────────────────────────┐   │
│  │ HR Professional │    │ Filling Logic:                               │   │
│  │                 │───▶│ • Knows employee data sources (HRIS, payroll)│   │
│  │ Fills: W-4, I-9,│    │ • Understands tax withholding rules          │   │
│  │ benefits forms  │    │ • Maps employee info → form fields           │   │
│  └─────────────────┘    │ • Validates SSN, dates, addresses            │   │
│                         └──────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────┐    ┌──────────────────────────────────────────────┐   │
│  │ Loan Officer    │    │ Filling Logic:                               │   │
│  │                 │───▶│ • Extracts from paystubs, tax returns        │   │
│  │ Fills: 1003,    │    │ • Calculates DTI, LTV ratios                 │   │
│  │ mortgage apps   │    │ • Cross-references multiple documents        │   │
│  └─────────────────┘    │ • Knows compliance requirements              │   │
│                         └──────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────┐    ┌──────────────────────────────────────────────┐   │
│  │ Tax Preparer    │    │ Filling Logic:                               │   │
│  │                 │───▶│ • Reads W-2s, 1099s, K-1s                    │   │
│  │ Fills: 1040,    │    │ • Applies tax rules and deductions           │   │
│  │ schedules, etc  │    │ • Calculates AGI, taxable income             │   │
│  └─────────────────┘    │ • Knows form field dependencies              │   │
│                         └──────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## How AI Learns from Personas

1. **Training Data**: Each persona provides labeled examples of how they fill documents
2. **Pattern Learning**: AI learns the persona's decision logic and field mappings
3. **Reusability**: Trained persona logic applies to similar documents
4. **Specialization**: Each persona becomes an expert AI agent for their document types

```
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│ Training Data   │────▶│ AI Model Training   │────▶│ Trained Persona     │
│ (Persona fills  │     │ (Learn patterns,    │     │ Agent               │
│ sample docs)    │     │ logic, mappings)    │     │                     │
└─────────────────┘     └─────────────────────┘     └─────────────────────┘
                                                              │
                        ┌─────────────────────────────────────┘
                        ▼
              ┌─────────────────────┐
              │ Reuse for new PDFs  │
              │ of same type        │
              └─────────────────────┘
```

## Directory Structure

```
personas/
├── README.md                    # This file
├── persona.schema.json          # JSON Schema for persona definitions
│
├── hr-professional/             # Example: HR persona
│   ├── persona.yaml             # Persona definition & role
│   ├── document-types.yaml      # Documents this persona fills
│   ├── filling-logic/           # Learned filling patterns
│   │   ├── w4-logic.yaml        # W-4 filling logic
│   │   ├── i9-logic.yaml        # I-9 filling logic
│   │   └── benefits-logic.yaml  
│   └── training/
│       ├── examples/            # Training examples (filled docs)
│       └── annotations/         # Field annotations
│
├── loan-officer/
│   ├── persona.yaml
│   ├── document-types.yaml
│   ├── filling-logic/
│   └── training/
│
├── tax-preparer/
│   └── ...
│
└── insurance-agent/
    └── ...
```

## Creating a Persona

### Step 1: Define the Persona Profile

```yaml
# personas/hr-professional/persona.yaml
id: hr-professional
name: HR Professional
description: Human Resources staff who process employee paperwork

# What role does this persona play?
role:
  title: HR Specialist / HR Generalist
  department: Human Resources
  responsibilities:
    - Employee onboarding paperwork
    - Benefits enrollment
    - Tax withholding forms
    - Employment verification

# What documents does this persona fill?
document_expertise:
  primary:
    - W-4 (Employee's Withholding Certificate)
    - I-9 (Employment Eligibility Verification)
    - State W-4 variants
    - Benefits enrollment forms
    - Direct deposit authorization
  secondary:
    - Employment contracts
    - NDA agreements
    - Emergency contact forms

# What data sources does this persona use?
data_sources:
  - type: hris
    name: HRIS/HCM System
    fields: [employee_name, ssn, address, hire_date, department]
  - type: payroll
    name: Payroll System
    fields: [pay_rate, pay_frequency, bank_info]
  - type: document
    name: Employee-provided documents
    fields: [id_documents, address_proof, prior_w2]

# Domain knowledge this persona has
knowledge:
  regulations:
    - IRS withholding rules
    - I-9 timing requirements (3 business days)
    - State tax requirements
  calculations:
    - Federal withholding estimation
    - State tax withholding
  validations:
    - SSN format and verification
    - I-9 document acceptability list
    - Address standardization (USPS)
```

### Step 2: Define Document Types

```yaml
# personas/hr-professional/document-types.yaml
documents:
  - id: irs-w4
    name: IRS Form W-4
    version: "2024"
    purpose: Employee federal tax withholding
    frequency: high
    complexity: medium
    
  - id: uscis-i9
    name: USCIS Form I-9
    version: "10/21/2019"
    purpose: Employment eligibility verification
    frequency: high
    complexity: high
    special_requirements:
      - Must be completed within 3 days of hire
      - Section 2 requires physical document inspection
      
  - id: direct-deposit
    name: Direct Deposit Authorization
    purpose: Set up payroll direct deposit
    frequency: high
    complexity: low
```

### Step 3: Define Filling Logic

```yaml
# personas/hr-professional/filling-logic/w4-logic.yaml
id: w4-filling-logic
document: irs-w4
persona: hr-professional

# Field mappings: data source → form field
field_mappings:
  - source: hris.employee_name
    target: step1a_name
    transform: format_legal_name
    
  - source: hris.ssn
    target: step1b_ssn
    transform: format_ssn
    validation: validate_ssn
    
  - source: hris.address
    target: step1c_address
    transform: format_address_single_line

# Decision logic for complex fields
decision_logic:
  # Step 2: Multiple Jobs Worksheet
  - field: step2_checkbox
    rule: |
      IF employee.spouse_works == true OR employee.has_multiple_jobs == true
      THEN check_box = true
      ELSE check_box = false
    requires_input: true
    question: "Does the employee or their spouse have multiple jobs?"
    
  # Step 3: Claim Dependents
  - field: step3_dependents_amount
    rule: |
      children_under_17 = COUNT(dependents WHERE age < 17)
      other_dependents = COUNT(dependents WHERE age >= 17 AND qualifies)
      total = (children_under_17 * 2000) + (other_dependents * 500)
      RETURN total
    requires_input: true
    questions:
      - "How many children under 17 does the employee claim?"
      - "How many other qualifying dependents?"

# Validation rules
validations:
  - field: step1b_ssn
    rule: "MATCHES pattern XXX-XX-XXXX AND is_valid_ssn()"
    error: "Invalid SSN format"
    
  - field: step1c_address
    rule: "NOT empty AND is_us_address()"
    error: "Valid US address required"

# Post-fill checks
post_fill_checks:
  - check: "If step2 checked, verify worksheet completed"
  - check: "If step3 > 0, verify dependent information collected"
```

### Step 4: Provide Training Examples

```jsonl
# personas/hr-professional/training/examples/w4-examples.jsonl
{"id": "w4-001", "scenario": "Single employee, no dependents", "input": {"employee_name": "John Smith", "ssn": "123-45-6789", "address": "123 Main St, Anytown, CA 90210", "filing_status": "single", "multiple_jobs": false, "dependents_under_17": 0, "other_dependents": 0}, "filled_form": {"step1a": "John Smith", "step1b": "123-45-6789", "step1c": "123 Main St, Anytown, CA 90210", "step1c_status": "single", "step2": null, "step3": "0"}}
{"id": "w4-002", "scenario": "Married, spouse works, 2 kids", "input": {"employee_name": "Jane Doe", "ssn": "987-65-4321", "address": "456 Oak Ave, Springfield, IL 62701", "filing_status": "married_filing_jointly", "multiple_jobs": true, "dependents_under_17": 2, "other_dependents": 0}, "filled_form": {"step1a": "Jane Doe", "step1b": "987-65-4321", "step1c": "456 Oak Ave, Springfield, IL 62701", "step1c_status": "married_filing_jointly", "step2": "checked", "step3": "4000"}}
{"id": "w4-003", "scenario": "Head of household, 1 child, 1 elderly parent", "input": {"employee_name": "Maria Garcia", "ssn": "456-78-9012", "address": "789 Elm Blvd, Austin, TX 78701", "filing_status": "head_of_household", "multiple_jobs": false, "dependents_under_17": 1, "other_dependents": 1}, "filled_form": {"step1a": "Maria Garcia", "step1b": "456-78-9012", "step1c": "789 Elm Blvd, Austin, TX 78701", "step1c_status": "head_of_household", "step2": null, "step3": "2500"}}
```

## Training a Persona AI Agent

```bash
# Train AI model on persona's filling logic
python -m models.persona_training.train \
  --persona hr-professional \
  --documents w4,i9,direct-deposit \
  --output models/trained/hr-professional

# Evaluate persona accuracy
python -m evals.runner.persona_eval \
  --persona hr-professional \
  --test-data personas/hr-professional/training/test
```

## Using a Trained Persona

```python
from autofiller import PersonaAgent

# Load trained HR Professional persona
agent = PersonaAgent.load("hr-professional")

# Fill a W-4 using the persona's learned logic
result = agent.fill(
    document_type="irs-w4",
    input_data={
        "employee_name": "New Hire",
        "ssn": "111-22-3333",
        "address": "100 Corporate Dr, Business City, NY 10001",
    },
    source_documents=["offer_letter.pdf"]  # Optional: extract more data
)

# Result
print(result.filled_fields)       # Fields that were auto-filled
print(result.confidence_scores)   # Confidence per field
print(result.needs_input)         # Fields requiring user input
print(result.questions)           # Questions to ask user
```

## Persona Inheritance

Personas can extend other personas to add specialization:

```yaml
# personas/senior-hr-manager/persona.yaml
id: senior-hr-manager
extends: hr-professional

# Additional expertise
additional_expertise:
  - Executive compensation forms
  - Stock option paperwork
  - International employee forms (tax treaties)
  
# Override or extend base logic
overrides:
  - document: irs-w4
    additional_logic: executive-w4-logic.yaml  # Handle deferred comp
```

## Integration with Domain Packs

Domain packs specify which personas are trained to fill them:

```yaml
# domain-packs/irs-w4/pack.yaml
name: irs-w4
version: "2024"

applicable_personas:
  - id: hr-professional
    role: primary
    accuracy_target: 0.98
    
  - id: payroll-specialist  
    role: secondary
    
  - id: individual
    role: self-service
    requires_guidance: true
```
