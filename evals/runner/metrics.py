"""
Metrics Calculation

Calculate accuracy metrics for extraction evaluation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

try:
    from Levenshtein import ratio as levenshtein_ratio
except ImportError:
    # Fallback if python-Levenshtein not installed
    def levenshtein_ratio(s1: str, s2: str) -> float:
        """Simple fallback ratio calculation."""
        if s1 == s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        return 0.5  # Rough estimate


@dataclass
class EvalResult:
    """Result of evaluating a single case."""
    
    case_id: str
    score: float
    passed: bool
    field_scores: dict[str, float] = field(default_factory=dict)
    missing_fields: list[str] = field(default_factory=list)
    extra_fields: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def normalize_string(s: str, config: dict[str, Any]) -> str:
    """Normalize string for comparison."""
    if not isinstance(s, str):
        return str(s)
    
    result = s
    
    if config.get("normalize_whitespace", True):
        result = " ".join(result.split())
    
    if config.get("case_insensitive", True):
        result = result.lower()
    
    if config.get("normalize_punctuation", True):
        # Remove common punctuation variations
        result = re.sub(r"[.,;:!?'\"-]", "", result)
    
    return result.strip()


def parse_date(value: Any, formats: list[str]) -> datetime | None:
    """Try to parse a date value using various formats."""
    if isinstance(value, datetime):
        return value
    
    if not isinstance(value, str):
        return None
    
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    
    return None


def compare_values(
    expected: Any,
    actual: Any,
    field_name: str,
    config: dict[str, Any],
) -> float:
    """
    Compare expected and actual values.
    
    Returns:
        Score from 0.0 to 1.0
    """
    # Handle None/missing
    if actual is None:
        return 0.0
    
    if expected is None:
        return 1.0 if actual is None else 0.0
    
    # Numeric comparison
    if isinstance(expected, (int, float)):
        if not isinstance(actual, (int, float)):
            try:
                actual = float(actual)
            except (ValueError, TypeError):
                return 0.0
        
        tolerance = config.get("numeric_tolerance", {})
        field_tolerance = tolerance.get(field_name, tolerance.get("default", 0.01))
        
        if expected == 0:
            return 1.0 if actual == 0 else 0.0
        
        diff = abs(expected - actual) / abs(expected)
        if diff <= field_tolerance:
            return 1.0
        return max(0.0, 1.0 - diff)
    
    # Date comparison
    date_config = config.get("date_comparison", {})
    date_formats = date_config.get("formats", ["%Y-%m-%d"])
    
    expected_date = parse_date(expected, date_formats)
    if expected_date:
        actual_date = parse_date(actual, date_formats)
        if actual_date:
            return 1.0 if expected_date.date() == actual_date.date() else 0.0
    
    # String comparison
    string_config = config.get("string_comparison", {})
    
    expected_str = normalize_string(str(expected), string_config)
    actual_str = normalize_string(str(actual), string_config)
    
    # Exact match
    if expected_str == actual_str:
        return 1.0
    
    # Fuzzy match
    fuzzy_threshold = string_config.get("fuzzy_threshold", 0.85)
    similarity = levenshtein_ratio(expected_str, actual_str)
    
    if similarity >= fuzzy_threshold:
        return similarity
    
    return similarity * 0.5  # Partial credit for low similarity


def compare_objects(
    expected: dict[str, Any],
    actual: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, float]:
    """Compare two objects and return per-field scores."""
    field_scores: dict[str, float] = {}
    
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        
        if isinstance(expected_value, dict) and isinstance(actual_value, dict):
            # Nested object - calculate average score
            nested_scores = compare_objects(expected_value, actual_value, config)
            field_scores[key] = sum(nested_scores.values()) / len(nested_scores) if nested_scores else 0.0
        elif isinstance(expected_value, list) and isinstance(actual_value, list):
            # Array comparison
            if not expected_value:
                field_scores[key] = 1.0 if not actual_value else 0.5
            else:
                # Compare each item
                item_scores = []
                for i, exp_item in enumerate(expected_value):
                    if i < len(actual_value):
                        if isinstance(exp_item, dict):
                            nested = compare_objects(exp_item, actual_value[i], config)
                            item_scores.append(sum(nested.values()) / len(nested) if nested else 0.0)
                        else:
                            item_scores.append(compare_values(exp_item, actual_value[i], f"{key}[{i}]", config))
                    else:
                        item_scores.append(0.0)
                field_scores[key] = sum(item_scores) / len(item_scores) if item_scores else 0.0
        else:
            field_scores[key] = compare_values(expected_value, actual_value, key, config)
    
    return field_scores


def calculate_metrics(
    case_id: str,
    expected: dict[str, Any],
    actual: dict[str, Any],
    config: dict[str, Any],
) -> EvalResult:
    """
    Calculate evaluation metrics for a single case.
    
    Args:
        case_id: Test case identifier
        expected: Expected extraction output
        actual: Actual extraction output
        config: Metrics configuration
    
    Returns:
        EvalResult with scores and pass/fail status
    """
    # Get per-field scores
    field_scores = compare_objects(expected, actual, config)
    
    # Check required fields
    required_fields = config.get("required_fields", [])
    required_present = sum(1 for f in required_fields if f in actual and actual[f] is not None)
    required_present_rate = required_present / len(required_fields) if required_fields else 1.0
    
    # Calculate threshold metrics
    thresholds = config.get("thresholds", {})
    
    # Exact match rate
    exact_matches = sum(1 for score in field_scores.values() if score == 1.0)
    exact_match_rate = exact_matches / len(field_scores) if field_scores else 0.0
    
    # Fuzzy match rate
    fuzzy_threshold = config.get("string_comparison", {}).get("fuzzy_threshold", 0.85)
    fuzzy_matches = sum(1 for score in field_scores.values() if score >= fuzzy_threshold)
    fuzzy_match_rate = fuzzy_matches / len(field_scores) if field_scores else 0.0
    
    # Calculate weighted score
    weights = config.get("weights", {
        "required_present": 0.4,
        "exact_match": 0.4,
        "fuzzy_match": 0.2,
    })
    
    score = (
        required_present_rate * weights.get("required_present", 0.4) +
        exact_match_rate * weights.get("exact_match", 0.4) +
        fuzzy_match_rate * weights.get("fuzzy_match", 0.2)
    )
    
    # Determine pass/fail
    min_score = config.get("minimum_score", 0.80)
    min_required_rate = thresholds.get("required_present_rate", 0.95)
    
    passed = score >= min_score and required_present_rate >= min_required_rate
    
    # Find missing/extra fields
    missing_fields = [f for f in expected.keys() if f not in actual]
    extra_fields = [f for f in actual.keys() if f not in expected]
    
    return EvalResult(
        case_id=case_id,
        score=score,
        passed=passed,
        field_scores=field_scores,
        missing_fields=missing_fields,
        extra_fields=extra_fields,
    )
