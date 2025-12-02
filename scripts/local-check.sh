#!/bin/bash
set -e

echo "Starting local checks..."

# 1. Linting
echo "🔍 Running Linting..."
echo "   - Ruff..."
python -m ruff check .
echo "   - Black..."
python -m black --check .
echo "   - Isort..."
python -m isort --check-only .

# 2. Security
echo "🛡️  Running Security Checks..."
echo "   - Safety..."
python -m safety check --json > /dev/null 2>&1 || echo "   ! Safety issues found (check ignored for local run, but recommended to fix)"
echo "   - Bandit..."
python -m bandit -r apps/ config/ -f json > /dev/null 2>&1 || echo "   ! Bandit issues found"

# 3. Tests
echo "🧪 Running Tests..."
python -m pytest

echo "✅ All local checks passed! You are ready to push."


echo "Test passed through locally see you soon in globally"