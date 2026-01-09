"""
Full Evaluation Runner

Complete evaluation suite for nightly/manual runs.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console
from rich.table import Table

from evals.runner.metrics import calculate_metrics, EvalResult
from evals.runner.smoke_eval import (
    load_eval_cases,
    load_expected_output,
    load_recorded_output,
    run_live_extraction,
)
from evals.runner.validate_packs import (
    DOMAIN_PACKS_DIR,
    get_all_packs,
    load_pack_schema,
    validate_single_pack,
)

console = Console()


def run_full_pack_eval(
    pack_dir: Path,
    live: bool = True,
    api_url: str | None = None,
) -> tuple[bool, list[EvalResult], dict[str, Any]]:
    """
    Run full evaluation for a single pack.
    
    Returns:
        Tuple of (passed, results, report)
    """
    manifest_path = pack_dir / "pack.yaml"
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    
    pack_name = manifest["name"]
    metrics_path = pack_dir / manifest.get("eval", {}).get("metrics", "eval/metrics.yaml")
    
    with open(metrics_path) as f:
        metrics_config = yaml.safe_load(f)
    
    # Load ALL cases (no limit)
    cases = load_eval_cases(pack_dir, max_cases=1000)
    results: list[EvalResult] = []
    
    console.print(f"\n[bold]Full Eval: {pack_name}[/bold] ({len(cases)} cases)")
    
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
                console.print(f"  [yellow]⚠ No recorded output for {case_id}[/yellow]")
                continue
        
        # Calculate metrics
        result = calculate_metrics(case_id, expected, actual, metrics_config)
        results.append(result)
        
        status = "✓" if result.passed else "✗"
        color = "green" if result.passed else "red"
        console.print(f"  [{color}]{status}[/{color}] {case_id}: score={result.score:.2f}")
    
    # Calculate overall stats
    if not results:
        return False, results, {}
    
    min_score = metrics_config.get("minimum_score", 0.80)
    avg_score = sum(r.score for r in results) / len(results)
    passed_count = sum(1 for r in results if r.passed)
    passed = avg_score >= min_score
    
    # Build report
    report = {
        "pack": pack_name,
        "version": manifest.get("version", "unknown"),
        "timestamp": datetime.utcnow().isoformat(),
        "cases_total": len(results),
        "cases_passed": passed_count,
        "cases_failed": len(results) - passed_count,
        "average_score": avg_score,
        "minimum_score": min_score,
        "passed": passed,
        "results": [
            {
                "case_id": r.case_id,
                "score": r.score,
                "passed": r.passed,
                "field_scores": r.field_scores,
            }
            for r in results
        ],
    }
    
    return passed, results, report


def run_full_eval(
    pack_name: str | None = None,
    live: bool = True,
    api_url: str | None = None,
    output_path: str | None = None,
) -> bool:
    """
    Run full evaluation suite.
    
    Args:
        pack_name: Specific pack to evaluate
        live: Use live API
        api_url: Custom API URL
        output_path: Path to write JSON report
    
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
    else:
        packs = get_all_packs()
    
    if not packs:
        console.print("[yellow]No packs to evaluate[/yellow]")
        return True
    
    console.print(f"\n[bold]Full Eval: {len(packs)} pack(s)[/bold]")
    console.print(f"Mode: {'Live API' if live else 'Recorded outputs'}")
    
    # Run evaluations
    all_passed = True
    all_reports: list[dict[str, Any]] = []
    pack_summaries: list[tuple[str, bool, float, int, int]] = []
    
    for pack_dir in packs:
        # Validate first
        is_valid, errors = validate_single_pack(pack_dir, pack_schema)
        if not is_valid:
            console.print(f"\n[red]Skipping {pack_dir.name}: validation failed[/red]")
            all_passed = False
            continue
        
        # Run full eval
        passed, results, report = run_full_pack_eval(pack_dir, live=live, api_url=api_url)
        all_passed = all_passed and passed
        
        if report:
            all_reports.append(report)
            pack_summaries.append((
                pack_dir.name,
                passed,
                report["average_score"],
                report["cases_passed"],
                report["cases_total"],
            ))
    
    # Summary table
    console.print("\n")
    table = Table(title="Full Eval Results")
    table.add_column("Pack", style="cyan")
    table.add_column("Status")
    table.add_column("Score", justify="right")
    table.add_column("Cases", justify="right")
    
    for pack_name, passed, score, cases_passed, cases_total in pack_summaries:
        status = "[green]✓ Pass[/green]" if passed else "[red]✗ Fail[/red]"
        cases = f"{cases_passed}/{cases_total}"
        table.add_row(pack_name, status, f"{score:.2f}", cases)
    
    console.print(table)
    
    # Write report
    if output_path and all_reports:
        full_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "packs": all_reports,
            "overall_passed": all_passed,
        }
        with open(output_path, "w") as f:
            json.dump(full_report, f, indent=2)
        console.print(f"\n[dim]Report written to {output_path}[/dim]")
    
    if all_passed:
        console.print("\n[green]✓ All full evals passed[/green]")
    else:
        console.print("\n[red]✗ Some full evals failed[/red]")
    
    return all_passed


@click.command()
@click.option("--pack", "-p", help="Specific pack to evaluate")
@click.option("--live/--no-live", default=True, help="Use live API or recorded outputs")
@click.option("--api-url", help="Custom API URL")
@click.option("--output", "-o", help="Output path for JSON report")
def main(pack: str | None, live: bool, api_url: str | None, output: str | None):
    """Run full evaluation for domain packs."""
    passed = run_full_eval(pack, live, api_url, output)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
