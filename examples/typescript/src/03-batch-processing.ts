/**
 * Batch Processing Example
 *
 * Demonstrates processing multiple documents efficiently.
 *
 * Run:
 *   npx tsx src/03-batch-processing.ts
 */

import { AutofillerClient, ExtractResult } from "@autofiller/sdk";
import * as fs from "fs";
import * as path from "path";

interface BatchResult {
  file: string;
  success: boolean;
  result?: ExtractResult;
  error?: string;
}

async function processBatch(
  client: AutofillerClient,
  files: string[],
  concurrency: number = 3
): Promise<BatchResult[]> {
  const results: BatchResult[] = [];
  const queue = [...files];

  async function processOne(): Promise<void> {
    while (queue.length > 0) {
      const file = queue.shift()!;
      console.log(`Processing: ${file}`);

      try {
        const result = await client.extract({
          file,
          domainPack: "invoice-standard",
        });

        results.push({ file, success: true, result });
        console.log(`  ✓ ${file} - ${Object.keys(result.data).length} fields extracted`);
      } catch (error) {
        const message = error instanceof Error ? error.message : "Unknown error";
        results.push({ file, success: false, error: message });
        console.log(`  ✗ ${file} - ${message}`);
      }
    }
  }

  // Process with concurrency limit
  const workers = Array(Math.min(concurrency, files.length))
    .fill(null)
    .map(() => processOne());

  await Promise.all(workers);
  return results;
}

async function main() {
  const client = new AutofillerClient({
    apiKey: process.env.AUTOFILLER_API_KEY!,
  });

  console.log("=== Batch Document Processing ===\n");

  // Get all PDFs from a directory
  const inputDir = "./invoices";
  const files = fs
    .readdirSync(inputDir)
    .filter((f) => f.endsWith(".pdf"))
    .map((f) => path.join(inputDir, f));

  console.log(`Found ${files.length} documents to process\n`);

  const startTime = Date.now();
  const results = await processBatch(client, files, 3);
  const elapsed = Date.now() - startTime;

  // Summary
  const successful = results.filter((r) => r.success).length;
  const failed = results.filter((r) => !r.success).length;

  console.log("\n=== Summary ===");
  console.log(`Total: ${results.length}`);
  console.log(`Successful: ${successful}`);
  console.log(`Failed: ${failed}`);
  console.log(`Time: ${(elapsed / 1000).toFixed(1)}s`);
  console.log(`Avg: ${(elapsed / results.length / 1000).toFixed(2)}s per document`);

  // Write results to file
  const outputPath = "./batch-results.json";
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
  console.log(`\nResults saved to ${outputPath}`);
}

main().catch(console.error);
