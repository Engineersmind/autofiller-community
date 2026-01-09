"""
Domain Pack Validation

Validates pack structure, manifest, and schema files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click
import yaml
from jsonschema import Draft7Validator, ValidationError as JsonSchemaError
from rich.console import Console
from rich.table import Table

console = Console()

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
DOMAIN_PACKS_DIR = REPO_ROOT / "domain-packs"
PACK_SCHEMA_PATH = DOMAIN_PACKS_DIR / "pack.schema.json"


def load_pack_schema() -> dict[str, Any]:
    """Load the pack manifest schema."""
    if not PACK_SCHEMA_PATH.exists():
        console.print(f"[red]Error: Pack schema not found at {PACK_SCHEMA_PATH}[/red]")
        sys.exit(1)
    
    with open(PACK_SCHEMA_PATH) as f:
        return json.load(f)


def get_all_packs() -> list[Path]:
    """Get all domain pack directories."""
    packs = []
    for path in DOMAIN_PACKS_DIR.iterdir():
        if path.is_dir() and (path / "pack.yaml").exists():
            packs.append(path)
    return sorted(packs)


def validate_pack_manifest(pack_dir: Path, schema: dict[str, Any]) -> list[str]:
    """Validate pack.yaml against the pack schema."""
    errors = []
    manifest_path = pack_dir / "pack.yaml"
    
    if not manifest_path.exists():
        return [f"Missing pack.yaml in {pack_dir.name}"]
    
    try:
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"Invalid YAML in pack.yaml: {e}"]
    
    # Validate against schema
    validator = Draft7Validator(schema)
    for error in validator.iter_errors(manifest):
        path = ".".join(str(p) for p in error.path) or "(root)"
        errors.append(f"{path}: {error.message}")
    
    return errors


def validate_pack_schema(pack_dir: Path) -> list[str]:
    """Validate the pack's JSON Schema file."""
    errors = []
    
    # Load manifest to get schema path
    manifest_path = pack_dir / "pack.yaml"
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    
    schema_path = pack_dir / manifest.get("schema", "schema.json")
    
    if not schema_path.exists():
        return [f"Missing schema file: {schema_path.name}"]
    
    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON in {schema_path.name}: {e}"]
    
    # Validate it's a valid JSON Schema
    try:
        Draft7Validator.check_schema(schema)
    except JsonSchemaError as e:
        errors.append(f"Invalid JSON Schema: {e.message}")
    
    return errors


def validate_eval_structure(pack_dir: Path) -> list[str]:
    """Validate eval directory structure and files."""
    errors = []
    
    # Load manifest
    manifest_path = pack_dir / "pack.yaml"
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    
    eval_config = manifest.get("eval", {})
    
    # Check cases file
    cases_path = pack_dir / eval_config.get("cases", "eval/cases.jsonl")
    if not cases_path.exists():
        errors.append(f"Missing eval cases file: {cases_path.name}")
    else:
        # Validate JSONL format
        try:
            with open(cases_path) as f:
                line_num = 0
                for line in f:
                    line_num += 1
                    if line.strip():
                        try:
                            case = json.loads(line)
                            if "id" not in case:
                                errors.append(f"Case at line {line_num} missing 'id' field")
                            if "fixture" not in case:
                                errors.append(f"Case at line {line_num} missing 'fixture' field")
                            if "expected" not in case:
                                errors.append(f"Case at line {line_num} missing 'expected' field")
                        except json.JSONDecodeError as e:
                            errors.append(f"Invalid JSON at line {line_num}: {e}")
        except Exception as e:
            errors.append(f"Error reading cases file: {e}")
    
    # Check expected directory
    expected_dir = pack_dir / eval_config.get("expected_dir", "eval/expected")
    if not expected_dir.exists():
        errors.append(f"Missing expected outputs directory: {expected_dir.name}")
    
    # Check metrics file
    metrics_path = pack_dir / eval_config.get("metrics", "eval/metrics.yaml")
    if not metrics_path.exists():
        errors.append(f"Missing metrics config: {metrics_path.name}")
    else:
        try:
            with open(metrics_path) as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML in metrics file: {e}")
    
    return errors


def validate_single_pack(pack_dir: Path, pack_schema: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate a single domain pack.
    
    Returns:
        Tuple of (is_valid, errors)
    """
    all_errors = []
    
    # Validate manifest
    manifest_errors = validate_pack_manifest(pack_dir, pack_schema)
    all_errors.extend(manifest_errors)
    
    # Only continue if manifest is valid
    if not manifest_errors:
        # Validate schema
        schema_errors = validate_pack_schema(pack_dir)
        all_errors.extend(schema_errors)
        
        # Validate eval structure
        eval_errors = validate_eval_structure(pack_dir)
        all_errors.extend(eval_errors)
    
    return len(all_errors) == 0, all_errors


def validate_packs(pack_name: str | None = None) -> bool:
    """
    Validate domain packs.
    
    Args:
        pack_name: Specific pack to validate, or None for all packs.
    
    Returns:
        True if all packs are valid.
    """
    pack_schema = load_pack_schema()
    
    if pack_name:
        pack_dir = DOMAIN_PACKS_DIR / pack_name
        if not pack_dir.exists():
            console.print(f"[red]Pack not found: {pack_name}[/red]")
            return False
        packs = [pack_dir]
    else:
        packs = get_all_packs()
    
    if not packs:
        console.print("[yellow]No domain packs found[/yellow]")
        return True
    
    console.print(f"\n[bold]Validating {len(packs)} domain pack(s)...[/bold]\n")
    
    # Results table
    table = Table(title="Validation Results")
    table.add_column("Pack", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Errors", style="red")
    
    all_valid = True
    
    for pack_dir in packs:
        is_valid, errors = validate_single_pack(pack_dir, pack_schema)
        
        if is_valid:
            table.add_row(pack_dir.name, "✓ Valid", "")
        else:
            all_valid = False
            error_summary = f"{len(errors)} error(s)"
            table.add_row(pack_dir.name, "✗ Invalid", error_summary)
            
            # Print detailed errors
            console.print(f"\n[red]Errors in {pack_dir.name}:[/red]")
            for error in errors:
                console.print(f"  • {error}")
    
    console.print(table)
    
    if all_valid:
        console.print("\n[green]✓ All packs valid[/green]")
    else:
        console.print("\n[red]✗ Validation failed[/red]")
    
    return all_valid


@click.command()
@click.option("--pack", "-p", help="Specific pack to validate")
def main(pack: str | None):
    """Validate domain pack structure and configuration."""
    is_valid = validate_packs(pack)
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
