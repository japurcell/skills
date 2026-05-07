#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:?must be set}"
echo "Syncing against ${API_BASE_URL}"
