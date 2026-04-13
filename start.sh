#!/bin/bash
set -e

export FLASK_ENV=development
export FLASK_APP=main.py

# Backend
python -m flask run --port 5000 &
FLASK_PID=$!

echo "Backend running on localhost:5000"
echo "Press Ctrl+C to stop"

wait $FLASK_PID
