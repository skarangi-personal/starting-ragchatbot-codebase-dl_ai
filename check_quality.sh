#!/bin/bash

# Code Quality Check Script
# Runs black, ruff, and isort in check-only mode
# Exit code 1 if any issues found, 0 if all passes

set -e

echo "🔍 Running code quality checks..."
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

failed=0

# Check black
echo "Checking code formatting with black..."
if uv run black --check backend/ main.py 2>&1; then
    echo -e "${GREEN}✓ black check passed${NC}"
else
    echo -e "${RED}✗ black found formatting issues${NC}"
    failed=1
fi
echo ""

# Check ruff
echo "Checking code with ruff..."
if uv run ruff check backend/ main.py 2>&1; then
    echo -e "${GREEN}✓ ruff check passed${NC}"
else
    echo -e "${RED}✗ ruff found issues${NC}"
    failed=1
fi
echo ""

# Check isort
echo "Checking import sorting with isort..."
if uv run isort --check-only backend/ main.py 2>&1; then
    echo -e "${GREEN}✓ isort check passed${NC}"
else
    echo -e "${RED}✗ isort found import issues${NC}"
    failed=1
fi
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✅ All quality checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some quality checks failed${NC}"
    echo ""
    echo "To fix issues automatically, run: ./format_code.sh"
    exit 1
fi
