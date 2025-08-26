#!/bin/bash

echo "=== Starting Arb Backend ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Python path: $PYTHONPATH"

# Test imports first
echo "Testing imports..."
python test_imports.py
if [ $? -ne 0 ]; then
    echo "❌ Import test failed!"
    exit 1
fi

# Test Playwright
echo "Testing Playwright..."
python verify_playwright.py
if [ $? -ne 0 ]; then
    echo "❌ Playwright test failed!"
    exit 1
fi

echo "✅ All tests passed! Starting application..."
exec python server.py
