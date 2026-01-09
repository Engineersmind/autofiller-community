"""
Batch Processing Example

Demonstrates processing multiple documents efficiently with concurrency.

Run:
    python 03_batch_processing.py
"""

import os
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from autofiller import AutofillerClient, ExtractResult, AutofillerError


@dataclass
class BatchResult:
    file: str
    success: bool
    result: ExtractResult | None = None
    error: str | None = None


def process_single(client: AutofillerClient, file_path: str) -> BatchResult:
    """Process a single document."""
    try:
        result = client.extract(
            file=file_path,
            domain_pack="invoice-standard",
        )
        return BatchResult(file=file_path, success=True, result=result)
    except AutofillerError as e:
        return BatchResult(file=file_path, success=False, error=str(e))
    except Exception as e:
        return BatchResult(file=file_path, success=False, error=str(e))


def process_batch(
    files: list[str],
    concurrency: int = 3,
) -> list[BatchResult]:
    """Process multiple documents with concurrency."""
    client = AutofillerClient(api_key=os.environ["AUTOFILLER_API_KEY"])
    results: list[BatchResult] = []

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(process_single, client, f): f for f in files
        }

        # Collect results as they complete
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            result = future.result()
            results.append(result)

            if result.success:
                field_count = len(result.result.data) if result.result else 0
                print(f"  ✓ {file_path} - {field_count} fields extracted")
            else:
                print(f"  ✗ {file_path} - {result.error}")

    return results


def main():
    print("=== Batch Document Processing ===\n")

    # Get all PDFs from a directory
    input_dir = Path("./invoices")
    files = list(input_dir.glob("*.pdf"))

    print(f"Found {len(files)} documents to process\n")

    start_time = time.time()
    results = process_batch([str(f) for f in files], concurrency=3)
    elapsed = time.time() - start_time

    # Summary
    successful = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)

    print("\n=== Summary ===")
    print(f"Total: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Time: {elapsed:.1f}s")
    print(f"Avg: {elapsed / len(results):.2f}s per document")

    # Write results to file
    output_path = Path("./batch-results.json")
    output_data = [
        {
            "file": r.file,
            "success": r.success,
            "data": r.result.data if r.result else None,
            "error": r.error,
        }
        for r in results
    ]
    output_path.write_text(json.dumps(output_data, indent=2))
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
