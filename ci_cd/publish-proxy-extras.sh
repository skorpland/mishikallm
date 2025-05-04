#!/bin/bash

# Exit on error
set -e

echo "🚀 Building and publishing mishikallm-proxy-extras"

# Navigate to mishikallm-proxy-extras directory
cd "$(dirname "$0")/../mishikallm-proxy-extras"

# Build the package
echo "📦 Building package..."
poetry build

# Publish to PyPI
echo "🌎 Publishing to PyPI..."
poetry publish

echo "✅ Done! Package published successfully"