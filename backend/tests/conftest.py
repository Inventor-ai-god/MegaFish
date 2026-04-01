"""
pytest configuration for the MegaFish backend test suite.

Adds the backend directory to sys.path so that `app` and `cli` are importable
as top-level packages (matching the pyproject.toml build target).
"""

import sys
import os

# Insert the backend/ directory at the front of sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
