/**
 * Basic Document Extraction Example
 *
 * Demonstrates synchronous extraction from a single document.
 *
 * Run:
 *   npx tsx src/01-basic-extraction.ts
 */

import { AutofillerClient } from "@autofiller/sdk";

async function main() {
  // Initialize client
  const client = new AutofillerClient({
    apiKey: process.env.AUTOFILLER_API_KEY!,
  });

  console.log("=== Basic Document Extraction ===\n");

  // Check API health first
  const health = await client.health();
  console.log(`API Status: ${health.status} (v${health.version})\n`);

  // Extract data from a document
  const result = await client.extract({
    file: "./sample-invoice.pdf",
    domainPack: "invoice-standard",
    includeConfidence: true,
  });

  console.log("Extraction ID:", result.id);
  console.log("Status:", result.status);
  console.log("Domain Pack:", result.domainPack);
  console.log("Pages:", result.metadata.pages);
  console.log("Processing Time:", result.metadata.processingTimeMs, "ms");
  console.log("\n=== Extracted Data ===");
  console.log(JSON.stringify(result.data, null, 2));

  if (result.confidence) {
    console.log("\n=== Confidence Scores ===");
    for (const [field, score] of Object.entries(result.confidence)) {
      console.log(`  ${field}: ${(score * 100).toFixed(1)}%`);
    }
  }

  if (result.warnings?.length) {
    console.log("\n=== Warnings ===");
    result.warnings.forEach((w) => console.log(`  - ${w}`));
  }
}

main().catch(console.error);
