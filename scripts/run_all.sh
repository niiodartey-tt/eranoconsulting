#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/backend"
echo "Activate Python venv and install requirements if not done."
echo "To start backend (dev):"
echo "  source .venv/bin/activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
echo
echo "Frontend apps (open separate terminals):"
echo "  cd frontend/main-site && npm install && npm run dev -- -p 3000"
echo "  cd frontend/client-portal && npm install && npm run dev -- -p 3001"
echo "  cd frontend/admin-portal && npm install && npm run dev -- -p 3002"
