"""Compatibility wrapper so tests can import :func:`main`.

This module dynamically loads ``main.py`` from the project root and exposes
its ``main`` function.  The test suite imports ``your_package.your_module`` to
access the CLI entry point without relying on the package layout.
"""

from importlib import util
from pathlib import Path

_path = Path(__file__).resolve().parents[2] / "main.py"
spec = util.spec_from_file_location("_bt_main", _path)
_module = util.module_from_spec(spec)
spec.loader.exec_module(_module)
main = _module.main

__all__ = ["main"]
