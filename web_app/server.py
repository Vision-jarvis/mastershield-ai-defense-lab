"""
MasterShield AI - Web Prototype Server Runner
Mastercard Innovation Challenge @ GFF 2026
"""

import os
import sys
import argparse
from pathlib import Path

# Ensure root directory is on Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from web_app.api import app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MasterShield AI Defense Lab Web Prototype")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)),
                        help="Port to serve the Cyber Defense Cockpit on (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    args = parser.parse_args()

    print(f"[*] Starting MasterShield AI Defense Lab Web UI on http://localhost:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, reload=False)
