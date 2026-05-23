"""
Public API for accessing bundled methodology documentation.

Files are bundled inside the wheel at install time (fair_lending_screener/_methodology_doc.md
and fair_lending_screener/_limitations_doc.md). get_methodology_path() and
get_limitations_path() return pathlib.Path objects pointing to those files.

MethodologyDocNotFoundError is raised if the file is absent from the installed package
(e.g., after a partial or corrupt install).
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path

from .exceptions import MethodologyDocNotFoundError


def get_methodology_path() -> Path:
    """
    Return the path to the bundled methodology documentation file.

    Returns:
        pathlib.Path to fair_lending_screener/_methodology_doc.md in the installed package.

    Raises:
        MethodologyDocNotFoundError: if the bundled file is absent from this environment.
    """
    ref = importlib.resources.files("fair_lending_screener") / "_methodology_doc.md"
    if not ref.is_file():
        raise MethodologyDocNotFoundError("fair_lending_screener/_methodology_doc.md")
    return Path(str(ref))


def get_limitations_path() -> Path:
    """
    Return the path to the bundled limitations documentation file.

    Returns:
        pathlib.Path to fair_lending_screener/_limitations_doc.md in the installed package.

    Raises:
        MethodologyDocNotFoundError: if the bundled file is absent from this environment.
    """
    ref = importlib.resources.files("fair_lending_screener") / "_limitations_doc.md"
    if not ref.is_file():
        raise MethodologyDocNotFoundError("fair_lending_screener/_limitations_doc.md")
    return Path(str(ref))
