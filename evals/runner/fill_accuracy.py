#!/usr/bin/env python3
"""
Fill Accuracy Evaluation

Evaluates the end-to-end form filling accuracy,
including PDF extraction, question generation, and capture logic.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class FillMetrics:
    """Container for fill accuracy metrics."""
    
    # Overall accuracy
    overall_accuracy: float = 0.0
    
    # Field-level metrics
    fields_correct: int = 0
    fields_total: int = 0
    fields_accuracy: float = 0.0
    
    # By source type
    extracted_accuracy: float = 0.0   # Fields from PDF extraction
    answered_accuracy: float = 0.0    # Fields from user answers
    computed_accuracy: float = 0.0    # Calculated fields
    default_accuracy: float = 0.0     # Default values
    
    # Error breakdown
    extraction_errors: int = 0
    transformation_errors: int = 0
    validation_errors: int = 0
    mapping_errors: int = 0
    
    # Per-field details
    per_field: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.per_field is None:
            self.per_field = {}


@dataclass
class FillTestCase:
    """Test case for fill accuracy evaluation."""
    id: str
    document_path: str
    user_answers: Dict[str, Any]
    expected_form: Dict[str, Any]
    domain_pack: str
    target_form: str


def load_fill_test_cases(test_dir: Path) -> List[FillTestCase]:
    """Load fill accuracy test cases."""
    cases = []
    
    test_file = test_dir / 'fill_cases.jsonl'
    if not test_file.exists():
        logger.warning(f"No fill test cases found at {test_file}")
        return cases
    
    with open(test_file, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            cases.append(FillTestCase(
                id=data['id'],
                document_path=data.get('document'),
                user_answers=data.get('answers', {}),
                expected_form=data.get('expected_form', {}),
                domain_pack=data.get('domain_pack', 'starter'),
                target_form=data.get('target_form', 'generic')
            ))
    
    return cases


def compare_form_values(
    filled: Dict[str, Any],
    expected: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare filled form values against expected.
    
    Returns detailed comparison results.
    """
    results = {
        'correct': [],
        'incorrect': [],
        'missing': [],
        'extra': []
    }
    
    all_fields = set(filled.keys()) | set(expected.keys())
    
    for field in all_fields:
        filled_val = filled.get(field)
        expected_val = expected.get(field)
        
        if expected_val is None:
            results['extra'].append({
                'field': field,
                'filled': filled_val
            })
        elif filled_val is None:
            results['missing'].append({
                'field': field,
                'expected': expected_val
            })
        elif normalize_value(filled_val) == normalize_value(expected_val):
            results['correct'].append({
                'field': field,
                'value': filled_val
            })
        else:
            results['incorrect'].append({
                'field': field,
                'filled': filled_val,
                'expected': expected_val
            })
    
    return results


def normalize_value(value: Any) -> Any:
    """Normalize value for comparison."""
    if value is None:
        return None
    
    if isinstance(value, str):
        # Normalize whitespace and case
        return ' '.join(value.lower().split())
    
    if isinstance(value, float):
        # Round to 2 decimal places
        return round(value, 2)
    
    return value


def evaluate_fill_accuracy(
    pipeline,  # Full autofill pipeline
    test_cases: List[FillTestCase],
    output_dir: Path = None
) -> FillMetrics:
    """
    Evaluate end-to-end fill accuracy.
    
    Args:
        pipeline: Autofill pipeline with extract(), ask_questions(), fill() methods
        test_cases: List of test cases
        output_dir: Directory to save results
        
    Returns:
        FillMetrics with results
    """
    total_correct = 0
    total_fields = 0
    
    by_source = {
        'extracted': {'correct': 0, 'total': 0},
        'answered': {'correct': 0, 'total': 0},
        'computed': {'correct': 0, 'total': 0},
        'default': {'correct': 0, 'total': 0}
    }
    
    errors = {
        'extraction': 0,
        'transformation': 0,
        'validation': 0,
        'mapping': 0
    }
    
    per_field_results = {}
    detailed_results = []
    
    for case in test_cases:
        logger.info(f"Evaluating fill case: {case.id}")
        
        try:
            # Step 1: Extract from document
            extracted = pipeline.extract(
                document=case.document_path,
                domain_pack=case.domain_pack
            )
            
            # Step 2: Simulate user answers
            # In real scenario, questions would be generated for missing fields
            combined_data = {**extracted.data, **case.user_answers}
            
            # Step 3: Fill form using capture logic
            filled_form = pipeline.fill(
                data=combined_data,
                target_form=case.target_form
            )
            
            # Compare results
            comparison = compare_form_values(filled_form, case.expected_form)
            
            # Update metrics
            num_correct = len(comparison['correct'])
            num_total = len(case.expected_form)
            
            total_correct += num_correct
            total_fields += num_total
            
            # Track by source (if available in metadata)
            for item in comparison['correct']:
                source = item.get('source', 'extracted')
                by_source.get(source, by_source['extracted'])['correct'] += 1
                by_source.get(source, by_source['extracted'])['total'] += 1
                
            for item in comparison['incorrect'] + comparison['missing']:
                source = item.get('source', 'extracted')
                by_source.get(source, by_source['extracted'])['total'] += 1
            
            # Track per-field accuracy
            for item in comparison['correct']:
                field = item['field']
                if field not in per_field_results:
                    per_field_results[field] = {'correct': 0, 'total': 0}
                per_field_results[field]['correct'] += 1
                per_field_results[field]['total'] += 1
                
            for item in comparison['incorrect'] + comparison['missing']:
                field = item['field']
                if field not in per_field_results:
                    per_field_results[field] = {'correct': 0, 'total': 0}
                per_field_results[field]['total'] += 1
            
            detailed_results.append({
                'case_id': case.id,
                'comparison': comparison,
                'accuracy': num_correct / num_total if num_total > 0 else 0
            })
            
        except Exception as e:
            logger.error(f"Fill evaluation failed for {case.id}: {e}")
            errors['extraction'] += 1
    
    # Calculate final metrics
    metrics = FillMetrics(
        overall_accuracy=total_correct / total_fields if total_fields > 0 else 0,
        fields_correct=total_correct,
        fields_total=total_fields,
        fields_accuracy=total_correct / total_fields if total_fields > 0 else 0,
        extracted_accuracy=by_source['extracted']['correct'] / by_source['extracted']['total'] if by_source['extracted']['total'] > 0 else 0,
        answered_accuracy=by_source['answered']['correct'] / by_source['answered']['total'] if by_source['answered']['total'] > 0 else 0,
        computed_accuracy=by_source['computed']['correct'] / by_source['computed']['total'] if by_source['computed']['total'] > 0 else 0,
        default_accuracy=by_source['default']['correct'] / by_source['default']['total'] if by_source['default']['total'] > 0 else 0,
        extraction_errors=errors['extraction'],
        transformation_errors=errors['transformation'],
        validation_errors=errors['validation'],
        mapping_errors=errors['mapping'],
        per_field={
            field: {'accuracy': data['correct'] / data['total']}
            for field, data in per_field_results.items()
        }
    )
    
    # Save results
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / 'fill_metrics.json', 'w') as f:
            json.dump(asdict(metrics), f, indent=2)
            
        with open(output_dir / 'fill_details.json', 'w') as f:
            json.dump(detailed_results, f, indent=2)
    
    return metrics


def print_fill_report(metrics: FillMetrics) -> None:
    """Print formatted fill accuracy report."""
    print("\n" + "=" * 50)
    print("FILL ACCURACY REPORT")
    print("=" * 50)
    
    print(f"\nOverall Accuracy: {metrics.overall_accuracy:.1%}")
    print(f"Fields Correct: {metrics.fields_correct}/{metrics.fields_total}")
    
    print("\n--- By Source ---")
    print(f"Extracted: {metrics.extracted_accuracy:.1%}")
    print(f"User Answers: {metrics.answered_accuracy:.1%}")
    print(f"Computed: {metrics.computed_accuracy:.1%}")
    print(f"Defaults: {metrics.default_accuracy:.1%}")
    
    if any([metrics.extraction_errors, metrics.transformation_errors,
            metrics.validation_errors, metrics.mapping_errors]):
        print("\n--- Errors ---")
        print(f"Extraction: {metrics.extraction_errors}")
        print(f"Transformation: {metrics.transformation_errors}")
        print(f"Validation: {metrics.validation_errors}")
        print(f"Mapping: {metrics.mapping_errors}")
    
    if metrics.per_field:
        print("\n--- Per-Field Accuracy ---")
        sorted_fields = sorted(
            metrics.per_field.items(),
            key=lambda x: x[1]['accuracy'],
            reverse=True
        )
        for field, data in sorted_fields[:10]:
            print(f"  {field}: {data['accuracy']:.1%}")


def main():
    parser = argparse.ArgumentParser(description='Evaluate fill accuracy')
    parser.add_argument('--test-dir', type=str, required=True,
                        help='Directory with fill test cases')
    parser.add_argument('--output-dir', type=str, default='eval-results/fill')
    parser.add_argument('--api-url', type=str, default='http://localhost:8080',
                        help='Autofiller API URL')
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    # Load test cases
    test_cases = load_fill_test_cases(Path(args.test_dir))
    logger.info(f"Loaded {len(test_cases)} fill test cases")
    
    if not test_cases:
        print("No fill test cases found. Create fill_cases.jsonl in test directory.")
        return
    
    # Note: Full evaluation requires running pipeline
    print("Note: Full fill evaluation requires running autofill pipeline")
    print("See documentation for API setup instructions")


if __name__ == '__main__':
    main()
