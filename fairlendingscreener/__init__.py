"""
Dual-import shim: allows both `import fair_lending_screener` and `import fairlendingscreener`.

This shim re-exports everything from fair_lending_screener so either import path works.
Applied from the hmda-analyzer 0.2.0 dual-import lesson.
"""
from fair_lending_screener import *  # noqa: F401, F403
from fair_lending_screener import __version__, __author__, __license__  # noqa: F401

__all__ = ["__version__", "__author__", "__license__"]
