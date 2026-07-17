"""
fair-lending-screener: Statistical lending-disparity screening for public HMDA data.

A public-data screening tool for community advocates and investigative journalists,
using FFIEC-standard controls. Informed by the FFIEC fair-lending risk-factor
framework — not the methodology examiners use (see the methodology doc).

Scope: Mortgage lending (HMDA-reportable) only.
Does NOT analyze Section 1071 small business lending data.
Does NOT include credit score (not in public HMDA).
Does NOT constitute a finding of discrimination — only a finding of
statistically significant adjusted disparity warranting further review.

v0.1.0: Adjusted denial disparity analysis (logistic regression with controls).
v0.2.0: Input validation, type-coercion fixes, release-process rebuild.
v0.2.1: Remove cloud-IP-breaking CFPB health-check gate; identifying headers + honest 403 message.
v0.2.2: Accuracy corrections — regulatory-provenance claim, disparate-impact label, version strings.
v0.3.0+: BISG proxy, redlining geographic tests, peer benchmarking.
        (Pricing/rate-spread disparity evaluated and deferred — public HMDA lacks the
         credit-risk control needed for a defensible adjusted estimate.)
"""

__version__ = "0.2.2"
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
    InvalidDataYearError,
    MethodologyDocNotFoundError,
)
from ._docs import get_methodology_path, get_limitations_path

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
    # Documentation paths
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
    "InvalidDataYearError",
    "MethodologyDocNotFoundError",
]
