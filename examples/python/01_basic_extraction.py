"""
Basic Document Extraction Example

Demonstrates synchronous extraction from a single document.

Run:
    python 01_basic_extraction.py
"""

import os
from autofiller import AutofillerClient


def main():
    # Initialize client
    client = AutofillerClient(api_key=os.environ["AUTOFILLER_API_KEY"])

    print("=== Basic Document Extraction ===\n")

    # Check API health first
    health = client.health()
    print(f"API Status: {health.status} (v{health.version})\n")

    # Extract data from a document
    result = client.extract(
        file="./sample-invoice.pdf",
        domain_pack="invoice-standard",
        include_confidence=True,
    )

    print(f"Extraction ID: {result.id}")
    print(f"Status: {result.status}")
    print(f"Domain Pack: {result.domain_pack}")
    print(f"Pages: {result.metadata.pages}")
    print(f"Processing Time: {result.metadata.processing_time_ms}ms")

    print("\n=== Extracted Data ===")
    for key, value in result.data.items():
        print(f"  {key}: {value}")

    if result.confidence:
        print("\n=== Confidence Scores ===")
        for field, score in result.confidence.items():
            print(f"  {field}: {score * 100:.1f}%")

    if result.warnings:
        print("\n=== Warnings ===")
        for warning in result.warnings:
            print(f"  - {warning}")


if __name__ == "__main__":
    main()
