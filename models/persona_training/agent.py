#!/usr/bin/env python3
"""
Persona Agent

A trained AI agent that fills documents using learned persona logic.

Usage:
    from models.persona_training.agent import PersonaAgent
    
    agent = PersonaAgent.load("hr-professional")
    result = agent.fill("w4", input_data)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import yaml

logger = logging.getLogger(__name__)


@dataclass
class FillResult:
    """Result of filling a document."""
    filled_fields: Dict[str, Any]
    confidence_scores: Dict[str, float]
    needs_input: List[str]
    questions: List[Dict[str, Any]]
    warnings: List[str]
    validation_errors: List[str]


class PersonaAgent:
    """
    AI agent trained to fill documents like a specific persona.
    
    The agent uses:
    1. Learned field mappings
    2. Decision logic for complex fields
    3. Validation rules
    4. Question generation for missing data
    """
    
    def __init__(
        self,
        persona_id: str,
        persona_config: Dict[str, Any],
        filling_logic: Dict[str, Dict[str, Any]],
        model_path: Optional[Path] = None
    ):
        self.persona_id = persona_id
        self.config = persona_config
        self.filling_logic = filling_logic
        self.model_path = model_path
        
    @classmethod
    def load(cls, persona_id: str, models_dir: str = "models/trained") -> "PersonaAgent":
        """
        Load a trained persona agent.
        
        Args:
            persona_id: ID of the persona (e.g., "hr-professional")
            models_dir: Directory containing trained models
            
        Returns:
            PersonaAgent instance
        """
        models_path = Path(models_dir)
        persona_path = models_path / persona_id
        
        if not persona_path.exists():
            raise ValueError(f"Trained persona not found: {persona_id}")
        
        # Load persona config
        config_file = persona_path / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {"id": persona_id}
        
        # Load filling logic for each document
        filling_logic = {}
        for doc_dir in persona_path.iterdir():
            if doc_dir.is_dir():
                logic_file = doc_dir / "training_data.json"
                if logic_file.exists():
                    with open(logic_file, 'r') as f:
                        data = json.load(f)
                        filling_logic[doc_dir.name] = data
        
        return cls(
            persona_id=persona_id,
            persona_config=config,
            filling_logic=filling_logic,
            model_path=persona_path
        )
    
    def fill(
        self,
        document_type: str,
        input_data: Dict[str, Any],
        source_documents: Optional[List[str]] = None
    ) -> FillResult:
        """
        Fill a document using the persona's learned logic.
        
        Args:
            document_type: Type of document to fill (e.g., "w4")
            input_data: Input data from various sources
            source_documents: Optional list of source document paths
            
        Returns:
            FillResult with filled fields, confidence, and questions
        """
        if document_type not in self.filling_logic:
            raise ValueError(f"Persona not trained for document: {document_type}")
        
        logic = self.filling_logic[document_type]
        
        # Initialize result containers
        filled_fields = {}
        confidence_scores = {}
        needs_input = []
        questions = []
        warnings = []
        validation_errors = []
        
        # Get field mappings and decision logic from training data
        examples = logic.get('examples', [])
        if not examples:
            return FillResult(
                filled_fields={},
                confidence_scores={},
                needs_input=[],
                questions=[],
                warnings=["No training data available"],
                validation_errors=[]
            )
        
        context = examples[0].get('input', {}).get('context', {})
        field_mappings = context.get('field_mappings', [])
        decision_logic = context.get('decision_logic', [])
        
        # Process field mappings
        for mapping in field_mappings:
            source = mapping.get('source', '')
            target = mapping.get('target', '')
            
            # Extract value from input data
            value = self._get_nested_value(input_data, source)
            
            if value is not None:
                # Apply transform if specified
                transform = mapping.get('transform')
                if transform:
                    value = self._apply_transform(value, transform)
                
                filled_fields[target] = value
                confidence_scores[target] = 0.95  # High confidence for direct mappings
            else:
                needs_input.append(target)
        
        # Process decision logic
        for decision in decision_logic:
            field = decision.get('field', '')
            requires_input = decision.get('requires_input', [])
            
            # Check if we have all required inputs
            has_all_inputs = True
            for req in requires_input:
                req_field = req.get('field', '')
                if req_field not in input_data:
                    has_all_inputs = False
                    
                    # Generate question
                    questions.append({
                        "field": req_field,
                        "question": req.get('question', f"Please provide {req_field}"),
                        "type": req.get('type', 'text'),
                        "options": req.get('options'),
                        "help": req.get('help')
                    })
            
            if has_all_inputs:
                # TODO: Execute decision logic
                # For now, this is a placeholder
                result = self._execute_logic(decision, input_data)
                if result is not None:
                    filled_fields[field] = result
                    confidence_scores[field] = 0.85
            else:
                needs_input.append(field)
        
        # Run validations
        # TODO: Implement validation execution
        
        return FillResult(
            filled_fields=filled_fields,
            confidence_scores=confidence_scores,
            needs_input=needs_input,
            questions=questions,
            warnings=warnings,
            validation_errors=validation_errors
        )
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _apply_transform(self, value: Any, transform: str) -> Any:
        """Apply a transformation to a value."""
        transforms = {
            'uppercase': lambda v: str(v).upper(),
            'lowercase': lambda v: str(v).lower(),
            'format_ssn': lambda v: self._format_ssn(v),
            'format_address_line1': lambda v: v.get('street', str(v)) if isinstance(v, dict) else str(v),
            'format_city_state_zip': lambda v: self._format_city_state_zip(v) if isinstance(v, dict) else str(v),
        }
        
        if transform in transforms:
            return transforms[transform](value)
        
        return value
    
    def _format_ssn(self, value: Any) -> str:
        """Format SSN as XXX-XX-XXXX."""
        ssn = str(value).replace('-', '').replace(' ', '')
        if len(ssn) == 9:
            return f"{ssn[:3]}-{ssn[3:5]}-{ssn[5:]}"
        return str(value)
    
    def _format_city_state_zip(self, address: Dict[str, Any]) -> str:
        """Format city, state, zip."""
        city = address.get('city', '')
        state = address.get('state', '')
        zip_code = address.get('zip', '')
        return f"{city}, {state} {zip_code}"
    
    def _execute_logic(self, decision: Dict[str, Any], input_data: Dict[str, Any]) -> Any:
        """
        Execute decision logic.
        
        This is a simplified implementation. In production, this would:
        1. Parse and execute the logic expression
        2. Use the trained model for complex decisions
        3. Apply business rules
        """
        field = decision.get('field', '')
        logic = decision.get('logic', '')
        
        # Simple pattern matching for common cases
        if 'dependents' in field.lower():
            children = input_data.get('dependents_under_17', 0)
            other = input_data.get('other_dependents', 0)
            return str((children * 2000) + (other * 500))
        
        if 'multiple_jobs' in field.lower():
            has_multiple = input_data.get('has_multiple_jobs', False)
            spouse_works = input_data.get('spouse_works', False)
            if has_multiple or spouse_works:
                return "checked"
            return None
        
        return None
    
    def get_supported_documents(self) -> List[str]:
        """Get list of documents this persona can fill."""
        return list(self.filling_logic.keys())
    
    def get_required_fields(self, document_type: str) -> List[Dict[str, Any]]:
        """Get required input fields for a document type."""
        if document_type not in self.filling_logic:
            return []
        
        logic = self.filling_logic[document_type]
        examples = logic.get('examples', [])
        
        if not examples:
            return []
        
        # Get context from first example
        context = examples[0].get('input', {}).get('context', {})
        
        required = []
        
        # Add fields from mappings
        for mapping in context.get('field_mappings', []):
            required.append({
                "field": mapping.get('source', ''),
                "target": mapping.get('target', ''),
                "required": True
            })
        
        # Add fields from decision logic
        for decision in context.get('decision_logic', []):
            for req in decision.get('requires_input', []):
                required.append({
                    "field": req.get('field', ''),
                    "question": req.get('question', ''),
                    "type": req.get('type', 'text'),
                    "required": True
                })
        
        return required
