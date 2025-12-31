#!/bin/bash

# Code Formatting Script
# Automatically formats code using black, ruff, and isort

set -e

echo "🎨 Formatting code..."
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Format with isort (import sorting)
echo -e "${BLUE}→${NC} Running isort (import sorting)..."
uv run isort backend/ main.py

# Format with black (code formatting)
echo -e "${BLUE}→${NC} Running black (code formatting)..."
uv run black backend/ main.py

# Fix with ruff (linting and auto-fixes)
echo -e "${BLUE}→${NC} Running ruff (linting and fixes)..."
uv run ruff check --fix backend/ main.py

echo ""
echo -e "${GREEN}✅ Code formatting complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review the changes: git diff"
echo "  2. Run checks: ./check_quality.sh"
echo "  3. Commit changes: git add . && git commit -m 'Format code'"
