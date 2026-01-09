"""
Async Extraction Example

Demonstrates async extraction with polling for large documents.

Run:
    python 02_async_extraction.py
"""

import os
import time
from autofiller import AutofillerClient


def main():
    client = AutofillerClient(api_key=os.environ["AUTOFILLER_API_KEY"])

    print("=== Async Document Extraction ===\n")

    # Start async extraction
    print("Starting async extraction...")
    job = client.extract_async(
        file="./large-document.pdf",
        domain_pack="tax-w2",
    )

    job_id = job["job_id"]
    print(f"Job ID: {job_id}")
    print(f"Estimated time: {job.get('estimated_time_seconds', 'unknown')} seconds")
    print("\nPolling for completion...")

    # Option 1: Use built-in polling
    result = client.wait_for_job(job_id, poll_interval=2.0, max_wait=300.0)

    print("\n=== Extraction Complete ===")
    print(f"Status: {result.status}")
    print("Data:")
    for key, value in result.data.items():
        print(f"  {key}: {value}")


def manual_polling():
    """Alternative: Manual polling example"""
    client = AutofillerClient(api_key=os.environ["AUTOFILLER_API_KEY"])

    job = client.extract_async(file="./document.pdf")
    job_id = job["job_id"]

    while True:
        status = client.get_job(job_id)
        progress = status.progress or 0
        print(f"Status: {status.status} ({progress:.0f}%)")

        if status.status == "completed" and status.result:
            print("Done!")
            print(status.result.data)
            break

        if status.status == "failed":
            print(f"Failed: {status.error}")
            break

        time.sleep(2)


if __name__ == "__main__":
    main()
