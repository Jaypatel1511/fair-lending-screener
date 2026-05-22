"""
fair-lending-screener: Statistical disparate impact analysis for HMDA data.

The methodology federal examiners use, open-sourced for community advocates
and investigative journalists.

Scope: Mortgage lending (HMDA-reportable) only.
Does NOT analyze Section 1071 small business lending data.
Does NOT include credit score (not in public HMDA).
Does NOT constitute a finding of discrimination — only a finding of
statistically significant adjusted disparity warranting further review.

v0.1.0: Adjusted denial disparity analysis (logistic regression with controls).
v0.1.1: Bug fixes — disclaimer, controls_used, min_sample_size, provenance year,
         business_or_commercial_purpose filter, bundled docs.
v0.2.0+: BISG proxy, pricing disparity, redlining geographic tests, peer benchmarking.
"""

import os

__version__ = "0.1.1"
__author__ = "Jay Patel"
__license__ = "MIT"

from .data import (
    load_from_api,
    load_from_file,
    load_sample,
    prepare_for_analysis,
    check_data_source,
)
from .disparity import (
    adjusted_denial_disparity,
    DisparityResult,
)
from .report import generate_disparity_report
from .exceptions import (
    FairLendingScreenerError,
    InsufficientDataError,
    ModelConvergenceError,
    InvalidProtectedClassError,
    MissingControlsError,
    DataSourceError,
    InsufficientGroupSizeError,
)


def get_methodology_path() -> str:
    """Return the filesystem path to the bundled methodology documentation."""
    return os.path.join(os.path.dirname(__file__), "_methodology_doc.md")


def get_limitations_path() -> str:
    """Return the filesystem path to the bundled HMDA data limitations documentation."""
    return os.path.join(os.path.dirname(__file__), "_limitations_doc.md")


__all__ = [
    "__version__",
    # Data loading
    "load_from_api",
    "load_from_file",
    "load_sample",
    "prepare_for_analysis",
    "check_data_source",
    # Core analysis
    "adjusted_denial_disparity",
    "DisparityResult",
    # Report generation
    "generate_disparity_report",
    # Bundled docs
    "get_methodology_path",
    "get_limitations_path",
    # Exceptions
    "FairLendingScreenerError",
    "InsufficientDataError",
    "ModelConvergenceError",
    "InvalidProtectedClassError",
    "MissingControlsError",
    "DataSourceError",
    "InsufficientGroupSizeError",
]
