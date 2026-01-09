#!/bin/bash
# Autofiller API - Sync Extraction Example
# 
# This script demonstrates basic synchronous document extraction.
# Use for small documents (<10 pages) that process quickly.
#
# Prerequisites:
#   - Set AUTOFILLER_API_KEY environment variable
#   - Have a sample document (PDF, PNG, JPG, or TIFF)
#
# Usage:
#   ./01-extract-sync.sh path/to/document.pdf

set -e

# Configuration
API_BASE_URL="${AUTOFILLER_API_URL:-https://api.autofiller.dev/v1}"
API_KEY="${AUTOFILLER_API_KEY:?Error: AUTOFILLER_API_KEY environment variable is not set}"

# Get document path from argument or use default
DOCUMENT="${1:-sample.pdf}"

if [ ! -f "$DOCUMENT" ]; then
    echo "Error: Document not found: $DOCUMENT"
    echo "Usage: $0 path/to/document.pdf"
    exit 1
fi

echo "=== Autofiller Sync Extraction ==="
echo "Document: $DOCUMENT"
echo "API: $API_BASE_URL"
echo ""

# Extract data from document
echo "Extracting data..."
RESPONSE=$(curl -s -X POST "$API_BASE_URL/extract" \
    -H "Authorization: Bearer $API_KEY" \
    -F "file=@$DOCUMENT" \
    -F "domain_pack=invoice-standard" \
    -F 'options={"include_confidence": true}')

# Pretty print response
echo ""
echo "=== Extraction Result ==="
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
