#!/usr/bin/env bash

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

echo "===== Trivy dependency-only scan (requirements.txt + package-lock.json) ====="


mkdir -p trivy-out

# Find all dependency files, excluding common directories
mapfile -t DEP_FILES < <(
  find . -type f \
    \( -name "requirements.txt" -o -name "package-lock.json" \) \
    -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "*/venv/*" \
    -print | sort
)

# Check if any dependency files were found
if [ ${#DEP_FILES[@]} -eq 0 ]; then
  echo "No requirements.txt or package-lock.json found."
  echo "No requirements.txt or package-lock.json found." > trivy-out/trivy-deps-table.txt
  exit 0
fi

# Display found files
echo "Found dependency files:"
printf ' - %s\n' "${DEP_FILES[@]}"
echo ""

# Run Trivy scan with table output
trivy fs \
  --scanners vuln \
  --ignore-unfixed \
  --severity HIGH,CRITICAL \
  --format table \
  --no-progress \
  --output trivy-out/trivy-deps-table.txt \
  "${DEP_FILES[@]}" || true

# Run Trivy scan with JSON output for easier parsing
trivy fs \
  --scanners vuln \
  --ignore-unfixed \
  --severity HIGH,CRITICAL \
  --format json \
  --no-progress \
  --output trivy-out/trivy-deps.json \
  "${DEP_FILES[@]}" || true

echo ""
echo "===== Scan Results ====="
cat trivy-out/trivy-deps-table.txt || true

echo ""
echo "===== Scan Complete ====="
echo "Results saved to:"
echo "  - trivy-out/trivy-deps-table.txt (human-readable)"
echo "  - trivy-out/trivy-deps.json (machine-readable)"
echo ""
echo "Check the files above for vulnerability details."
