# List all recipes
default:
    @just --list

# Setup development environment
setup:
    uv pip install '.[dev]'
    pre-commit install

# Run all tests
test:
    pytest

# Run feature pipeline
feature-pipeline:
    #!/usr/bin/env bash
    cd src/01-module/scripts && \
    ./run-feature-and-prediction-pipelines.sh

# Run fraud feature pipeline
fraud-pipeline:
    #!/usr/bin/env bash
    cd src/02-module/scripts && \
    ./run-fraud-feature-pipelines.sh

# Run fraud batch inference
fraud-inference:
    #!/usr/bin/env bash
    cd src/03-module/scripts && \
    ./run-fraud-batch-inference.sh

# Run Streamlit app
streamlit:
    #!/usr/bin/env bash
    cd src/04-module && \
    ./run-fraud-streamlit.sh

# Run code quality checks
lint:
    ruff check .
    ruff format --check .

# Fix code style issues
fix:
    ruff check --fix .
    ruff format .

# Check documentation coverage
docs:
    interrogate -v .

# Clean python cache files
clean:
    find . -type d -name "__pycache__" -exec rm -r {} +
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type f -name "*.pyd" -delete
    find . -type d -name "*.egg-info" -exec rm -r {} +
    find . -type d -name "*.egg" -exec rm -r {} +
    find . -type d -name ".pytest_cache" -exec rm -r {} +
    find . -type d -name ".ruff_cache" -exec rm -r {} +

# Run all checks (lint and test)
check: lint test

# Build project
build:
    uv pip install build
    python -m build
