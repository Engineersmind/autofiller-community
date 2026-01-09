/**
 * Async Extraction Example
 *
 * Demonstrates async extraction with polling for large documents.
 *
 * Run:
 *   npx tsx src/02-async-extraction.ts
 */

import { AutofillerClient } from "@autofiller/sdk";

async function main() {
  const client = new AutofillerClient({
    apiKey: process.env.AUTOFILLER_API_KEY!,
  });

  console.log("=== Async Document Extraction ===\n");

  // Start async extraction
  console.log("Starting async extraction...");
  const job = await client.extractAsync({
    file: "./large-document.pdf",
    domainPack: "tax-w2",
  });

  console.log(`Job ID: ${job.jobId}`);
  console.log(`Estimated time: ${job.estimatedTimeSeconds ?? "unknown"} seconds`);
  console.log("\nPolling for completion...");

  // Option 1: Use built-in polling
  const result = await client.waitForJob(job.jobId, 2000, 300000);

  console.log("\n=== Extraction Complete ===");
  console.log("Status:", result.status);
  console.log("Data:", JSON.stringify(result.data, null, 2));
}

// Alternative: Manual polling
async function manualPolling() {
  const client = new AutofillerClient({
    apiKey: process.env.AUTOFILLER_API_KEY!,
  });

  const job = await client.extractAsync({ file: "./document.pdf" });

  while (true) {
    const status = await client.getJob(job.jobId);
    console.log(`Status: ${status.status} (${status.progress ?? 0}%)`);

    if (status.status === "completed" && status.result) {
      console.log("Done!", status.result.data);
      break;
    }

    if (status.status === "failed") {
      console.error("Failed:", status.error?.message);
      break;
    }

    await new Promise((r) => setTimeout(r, 2000));
  }
}

main().catch(console.error);
