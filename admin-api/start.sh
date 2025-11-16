#!/bin/bash
# Admin API startup script

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Start uvicorn from the admin-api directory
exec "$SCRIPT_DIR/venv/bin/uvicorn" main:app --host 0.0.0.0 --port 8001 --reload
