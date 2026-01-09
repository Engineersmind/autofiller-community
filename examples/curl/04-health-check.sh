#!/bin/bash
# Autofiller API - Health Check
# 
# Simple health check to verify API connectivity.
#
# Usage:
#   ./04-health-check.sh

set -e

API_BASE_URL="${AUTOFILLER_API_URL:-https://api.autofiller.dev/v1}"

echo "Checking API health..."
echo ""

RESPONSE=$(curl -s -X GET "$API_BASE_URL/health")

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
