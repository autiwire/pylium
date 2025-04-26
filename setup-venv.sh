#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip and install build tools
pip install --upgrade pip
pip install --upgrade setuptools wheel

# Install the package in development mode with all dependencies
pip install -e .[dev]

# Generate requirements.txt from requirements.in
pip-compile requirements.in

echo "Virtual environment setup complete! Use 'source .venv/bin/activate' to activate it." 