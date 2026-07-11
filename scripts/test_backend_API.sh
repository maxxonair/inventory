#!/bin/bash

set -e

cd $(dirname "$0")/../backend/src

# Run the test for all backend API endpoints
uv run pytest test_backend_api.py -v