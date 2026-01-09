#!/bin/bash
# Autofiller API - Async Extraction Example
# 
# This script demonstrates asynchronous document extraction with polling.
# Use for large documents (>10 pages) or when processing takes longer.
#
# Prerequisites:
#   - Set AUTOFILLER_API_KEY environment variable
#   - Have a sample document
#
# Usage:
#   ./02-extract-async.sh path/to/large-document.pdf

set -e

# Configuration
API_BASE_URL="${AUTOFILLER_API_URL:-https://api.autofiller.dev/v1}"
API_KEY="${AUTOFILLER_API_KEY:?Error: AUTOFILLER_API_KEY environment variable is not set}"
POLL_INTERVAL=2  # seconds

# Get document path from argument
DOCUMENT="${1:-sample.pdf}"

if [ ! -f "$DOCUMENT" ]; then
    echo "Error: Document not found: $DOCUMENT"
    echo "Usage: $0 path/to/document.pdf"
    exit 1
fi

echo "=== Autofiller Async Extraction ==="
echo "Document: $DOCUMENT"
echo "API: $API_BASE_URL"
echo ""

# Step 1: Start async extraction job
echo "Starting async extraction..."
JOB_RESPONSE=$(curl -s -X POST "$API_BASE_URL/extract/async" \
    -H "Authorization: Bearer $API_KEY" \
    -F "file=@$DOCUMENT")

JOB_ID=$(echo "$JOB_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])" 2>/dev/null)

if [ -z "$JOB_ID" ]; then
    echo "Error: Failed to start job"
    echo "$JOB_RESPONSE"
    exit 1
fi

echo "Job started: $JOB_ID"
echo ""

# Step 2: Poll for completion
echo "Polling for completion..."
while true; do
    STATUS_RESPONSE=$(curl -s -X GET "$API_BASE_URL/jobs/$JOB_ID" \
        -H "Authorization: Bearer $API_KEY")
    
    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
    PROGRESS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('progress', 0))" 2>/dev/null)
    
    echo "Status: $STATUS (${PROGRESS}%)"
    
    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "=== Extraction Result ==="
        echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo ""
        echo "=== Job Failed ==="
        echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"
        exit 1
    fi
    
    sleep $POLL_INTERVAL
done
