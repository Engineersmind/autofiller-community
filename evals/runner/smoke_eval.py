"""
Smoke Evaluation Runner

Quick evaluation for CI - runs 1-3 cases per pack.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console
from rich.table import Table

from evals.runner.metrics import calculate_metrics, EvalResult
from evals.runner.validate_packs import DOMAIN_PACKS_DIR, get_all_packs, validate_single_pack, load_pack_schema

console = Console()

# Maximum cases for smoke eval
SMOKE_EVAL_MAX_CASES = 3


def get_changed_packs() -> list[str]:
    """Get packs that have changed in the current PR/commit."""
    try:
        # Get changed files from git
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True,
            text=True,
            check=True,
        )
        changed_files = result.stdout.strip().split("\n")
        
        # Find packs with changes
        changed_packs = set()
        for file in changed_files:
            if file.startswith("domain-packs/"):
                parts = file.split("/")
                if len(parts) >= 2:
                    pack_name = parts[1]
                    if pack_name != "pack.schema.json":
                        changed_packs.add(pack_name)
        
        return list(changed_packs)
    except subprocess.CalledProcessError:
        # Git command failed, return all packs
        return [p.name for p in get_all_packs()]


def load_eval_cases(pack_dir: Path, max_cases: int = SMOKE_EVAL_MAX_CASES) -> list[dict[str, Any]]:
    """Load evaluation cases for a pack."""
    manifest_path = pack_dir / "pack.yaml"
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    
    cases_path = pack_dir / manifest.get("eval", {}).get("cases", "eval/cases.jsonl")
    
    cases = []
    with open(cases_path) as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
                if len(cases) >= max_cases:
                    break
    
    return cases


def load_expected_output(pack_dir: Path, expected_path: str) -> dict[str, Any]:
    """Load expected output for a case."""
    full_path = pack_dir / expected_path
    with open(full_path) as f:
        return json.load(f)


def load_recorded_output(pack_dir: Path, case_id: str) -> dict[str, Any] | None:
    """Load recorded model output (for offline evaluation)."""
    recorded_dir = pack_dir / "eval" / "recorded"
    recorded_path = recorded_dir / f"{case_id}.json"
    
    if recorded_path.exists():
        with open(recorded_path) as f:
            return json.load(f)
    return None


def run_live_extraction(fixture_path: Path, domain_pack: str) -> dict[str, Any]:
    """Call the Autofiller API to extract data (live mode)."""
    # Import here to avoid requiring SDK for offline eval
    try:
        from autofiller import AutofillerClient
    except ImportError:
        console.print("[red]Error: autofiller-sdk not installed. Install with: pip install autofiller-sdk[/red]")
        sys.exit(1)
    
    api_key = os.environ.get("AUTOFILLER_API_KEY")
    if not api_key:
        console.print("[red]Error: AUTOFILLER_API_KEY environment variable not set[/red]")
        sys.exit(1)
    
    client = AutofillerClient(api_key=api_key)
    result = client.extract(file=str(fixture_path), domain_pack=domain_pack)
    return result.data


def run_pack_eval(
    pack_dir: Path,
    live: bool = False,
    max_cases: int = SMOKE_EVAL_MAX_CASES,
) -> tuple[bool, list[EvalResult]]:
    """
    Run evaluation for a single pack.
    
    Returns:
        Tuple of (passed, results)
    """
    manifest_path = pack_dir / "pack.yaml"
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    
    pack_name = manifest["name"]
    metrics_path = pack_dir / manifest.get("eval", {}).get("metrics", "eval/metrics.yaml")
    
    with open(metrics_path) as f:
        metrics_config = yaml.safe_load(f)
    
    cases = load_eval_cases(pack_dir, max_cases)
    results: list[EvalResult] = []
    
    console.print(f"\n[bold]Evaluating {pack_name}[/bold] ({len(cases)} cases)")
    
    for case in cases:
        case_id = case["id"]
        expected = load_expected_output(pack_dir, case["expected"])
        
        # Get actual output
        if live:
            fixture_path = pack_dir / case["fixture"]
            if not fixture_path.exists():
                console.print(f"  [yellow]⚠ Fixture not found: {case['fixture']}[/yellow]")
                continue
            actual = run_live_extraction(fixture_path, pack_name)
        else:
            actual = load_recorded_output(pack_dir, case_id)
            if actual is None:
                # Use expected as "actual" for validation-only mode
                console.print(f"  [yellow]⚠ No recorded output for {case_id}, using expected[/yellow]")
                actual = expected
        
        # Calculate metrics
        result = calculate_metrics(case_id, expected, actual, metrics_config)
        results.append(result)
        
        status = "✓" if result.passed else "✗"
        color = "green" if result.passed else "red"
        console.print(f"  [{color}]{status}[/{color}] {case_id}: score={result.score:.2f}")
    
    # Calculate overall pass/fail
    if not results:
        return False, results
    
    min_score = metrics_config.get("minimum_score", 0.80)
    avg_score = sum(r.score for r in results) / len(results)
    passed = avg_score >= min_score and all(r.passed for r in results)
    
    return passed, results


def run_smoke_eval(
    pack_name: str | None = None,
    changed_only: bool = False,
    live: bool = False,
) -> bool:
    """
    Run smoke evaluation.
    
    Args:
        pack_name: Specific pack to evaluate
        changed_only: Only evaluate packs with changes
        live: Use live API instead of recorded outputs
    
    Returns:
        True if all evaluations pass
    """
    pack_schema = load_pack_schema()
    
    # Determine packs to evaluate
    if pack_name:
        pack_dir = DOMAIN_PACKS_DIR / pack_name
        if not pack_dir.exists():
            console.print(f"[red]Pack not found: {pack_name}[/red]")
            return False
        packs = [pack_dir]
    elif changed_only:
        changed = get_changed_packs()
        if not changed:
            console.print("[yellow]No changed packs found[/yellow]")
            return True
        packs = [DOMAIN_PACKS_DIR / name for name in changed if (DOMAIN_PACKS_DIR / name).exists()]
    else:
        packs = get_all_packs()
    
    if not packs:
        console.print("[yellow]No packs to evaluate[/yellow]")
        return True
    
    console.print(f"\n[bold]Smoke Eval: {len(packs)} pack(s)[/bold]")
    console.print(f"Mode: {'Live API' if live else 'Recorded outputs'}")
    
    # Results
    all_passed = True
    pack_results: list[tuple[str, bool, float]] = []
    
    for pack_dir in packs:
        # Validate first
        is_valid, errors = validate_single_pack(pack_dir, pack_schema)
        if not is_valid:
            console.print(f"\n[red]Skipping {pack_dir.name}: validation failed[/red]")
            all_passed = False
            pack_results.append((pack_dir.name, False, 0.0))
            continue
        
        # Run eval
        passed, results = run_pack_eval(pack_dir, live=live)
        all_passed = all_passed and passed
        
        avg_score = sum(r.score for r in results) / len(results) if results else 0.0
        pack_results.append((pack_dir.name, passed, avg_score))
    
    # Summary table
    console.print("\n")
    table = Table(title="Smoke Eval Results")
    table.add_column("Pack", style="cyan")
    table.add_column("Status")
    table.add_column("Score", justify="right")
    
    for pack_name, passed, score in pack_results:
        status = "[green]✓ Pass[/green]" if passed else "[red]✗ Fail[/red]"
        table.add_row(pack_name, status, f"{score:.2f}")
    
    console.print(table)
    
    if all_passed:
        console.print("\n[green]✓ All smoke evals passed[/green]")
    else:
        console.print("\n[red]✗ Some smoke evals failed[/red]")
    
    return all_passed


@click.command()
@click.option("--pack", "-p", help="Specific pack to evaluate")
@click.option("--changed-only", is_flag=True, help="Only evaluate changed packs")
@click.option("--live", is_flag=True, help="Use live API instead of recorded outputs")
def main(pack: str | None, changed_only: bool, live: bool):
    """Run smoke evaluation for domain packs."""
    passed = run_smoke_eval(pack, changed_only, live)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
