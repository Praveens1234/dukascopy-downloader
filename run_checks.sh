#!/bin/bash
set -e

echo "Running Flake8..."
flake8 .

echo "Running Mypy..."
mypy .

echo "Running Tests..."
pytest --cov=core --cov-report=term-missing
