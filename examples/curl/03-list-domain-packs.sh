#!/bin/bash
# Autofiller API - List Domain Packs
# 
# This script lists all available domain packs and their schemas.
#
# Usage:
#   ./03-list-domain-packs.sh

set -e

# Configuration
API_BASE_URL="${AUTOFILLER_API_URL:-https://api.autofiller.dev/v1}"
API_KEY="${AUTOFILLER_API_KEY:?Error: AUTOFILLER_API_KEY environment variable is not set}"

echo "=== Available Domain Packs ==="
echo ""

# List all domain packs
RESPONSE=$(curl -s -X GET "$API_BASE_URL/domain-packs" \
    -H "Authorization: Bearer $API_KEY")

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
