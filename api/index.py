"""
Vercel serverless entry point for the MasterShield AI cockpit.

Vercel's Python runtime discovers `app` in this module. WebSockets are not
supported on serverless, so the live stream degrades to HTTP polling; the
attack injection studio, graph topology, benchmark and ISO 20022 views all
work normally.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from web_app.api import app  # noqa: E402

__all__ = ["app"]
