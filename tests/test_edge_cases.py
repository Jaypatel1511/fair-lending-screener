"""
Edge case tests — every typed exception path must be exercised here.

These tests verify that the package raises the correct typed exception
(never a silent empty return, never a generic RuntimeError) in all
error conditions documented in docs/methodology.md.
"""

import numpy as np
import pandas as pd
import pytest

from fair_lending_screener import (
    adjusted_denial_disparity,
    InsufficientDataError,
    InvalidProtectedClassError,
    MissingControlsError,
    ModelConvergenceError,
    InsufficientGroupSizeError,
    load_sample,
    prepare_for_analysis,
)


@pytest.fixture
def base_df():
    """Prepared sample DataFrame with all standard controls."""
    raw = load_sample(n=500, seed=0)
    return prepare_for_analysis(raw, validate_controls=False)


# ── InsufficientDataError ──────────────────────────────────────────────────────

def test_insufficient_data_raises(base_df):
    """Sample below min_sample_size raises InsufficientDataError, not a result."""
    tiny = base_df[base_df["derived_race"].isin(["Black or African American", "White"])].head(50)
    with pytest.raises(InsufficientDataError) as exc_info:
        adjusted_denial_disparity(tiny, min_sample_size=100, data_year=2023)
    err = exc_info.value
    assert err.actual < 100
    assert err.minimum == 100
    assert "Peduzzi" in str(err)


def test_insufficient_data_error_fields():
    """InsufficientDataError carries actual and minimum fields."""
    err = InsufficientDataError(actual=42, minimum=100,
                                protected_class="Black or African American",
                                comparison_class="White")
    assert err.actual == 42
    assert err.minimum == 100
    assert "42" in str(err)
    assert "100" in str(err)


# ── InvalidProtectedClassError ────────────────────────────────────────────────

def test_protected_class_not_in_data(base_df):
    """Requesting a race not present raises InvalidProtectedClassError with valid values listed."""
    with pytest.raises(InvalidProtectedClassError) as exc_info:
        adjusted_denial_disparity(base_df, protected_class="Martian", data_year=2023)
    err = exc_info.value
    assert err.requested == "Martian"
    assert "White" in err.valid_values
    assert "Martian" not in err.valid_values


def test_comparison_class_not_in_data(base_df):
    """Requesting a comparison class not present raises InvalidProtectedClassError."""
    with pytest.raises(InvalidProtectedClassError) as exc_info:
        adjusted_denial_disparity(base_df, comparison_class="Martian", data_year=2023)
    err = exc_info.value
    assert err.requested == "Martian"


# ── MissingControlsError ──────────────────────────────────────────────────────

def test_missing_required_column():
    """DataFrame without derived_race raises MissingControlsError, not KeyError."""
    df = pd.DataFrame({
        "action_taken": [1, 3, 1, 3],
        "loan_type": [1, 1, 1, 1],
        "is_denied": [0, 1, 0, 1],
        "log_income": [4.0, 3.5, 4.2, 3.8],
    })
    with pytest.raises(MissingControlsError) as exc_info:
        adjusted_denial_disparity(df, data_year=2023)
    assert "derived_race" in exc_info.value.missing_columns


def test_explicitly_requested_control_missing(base_df):
    """Explicitly requesting a missing control column raises MissingControlsError."""
    with pytest.raises(MissingControlsError) as exc_info:
        adjusted_denial_disparity(base_df, controls=["nonexistent_column"], min_sample_size=100, data_year=2023)
    assert "nonexistent_column" in exc_info.value.missing_columns
    assert "nonexistent_column" in str(exc_info.value)


def test_prepare_for_analysis_missing_action_taken():
    """prepare_for_analysis raises MissingControlsError when action_taken is absent."""
    df = pd.DataFrame({"derived_race": ["White", "Black or African American"]})
    with pytest.raises(MissingControlsError):
        prepare_for_analysis(df)


# ── All-denial / all-origination degenerate groups ────────────────────────────

def test_all_denials_one_group_raises():
    """If one group has only denials, ModelConvergenceError (not a crash) is raised."""
    n = 200
    rng = np.random.default_rng(1)

    # Black group: all denials
    black_rows = {
        "action_taken": [3] * 100,
        "derived_race": ["Black or African American"] * 100,
        "loan_type": [1] * 100,
        "loan_purpose": [1] * 100,
        "lien_status": [1] * 100,
        "occupancy_type": [1] * 100,
        "property_type": [1] * 100,
        "construction_method": [1] * 100,
        "loan_to_value_ratio": list(rng.uniform(60, 95, 100)),
        "applicant_income": list(rng.uniform(40, 120, 100)),
        "loan_amount": list(rng.uniform(100, 400, 100)),
        "property_value": list(rng.uniform(150, 600, 100)),
        "debt_to_income_ratio": list(rng.uniform(20, 55, 100)),
        "msa_md": ["MSA_001"] * 100,
    }
    # White group: all originations
    white_rows = {
        "action_taken": [1] * 100,
        "derived_race": ["White"] * 100,
        "loan_type": [1] * 100,
        "loan_purpose": [1] * 100,
        "lien_status": [1] * 100,
        "occupancy_type": [1] * 100,
        "property_type": [1] * 100,
        "construction_method": [1] * 100,
        "loan_to_value_ratio": list(rng.uniform(60, 95, 100)),
        "applicant_income": list(rng.uniform(40, 120, 100)),
        "loan_amount": list(rng.uniform(100, 400, 100)),
        "property_value": list(rng.uniform(150, 600, 100)),
        "debt_to_income_ratio": list(rng.uniform(20, 55, 100)),
        "msa_md": ["MSA_001"] * 100,
    }

    df = pd.concat([pd.DataFrame(black_rows), pd.DataFrame(white_rows)], ignore_index=True)
    prepared = prepare_for_analysis(df, validate_controls=False)

    with pytest.raises(ModelConvergenceError) as exc_info:
        adjusted_denial_disparity(prepared, controls=[], min_sample_size=100, data_year=2023)
    assert "separation" in str(exc_info.value).lower() or "all" in str(exc_info.value).lower()


# ── Regression test: CRIT-2 controls_used overwrite ───────────────────────────

def test_controls_used_excludes_dropped_controls(base_df):
    """Controls dropped for zero variance must NOT appear in controls_used (CRIT-2 fix)."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(base_df, min_sample_size=100, data_year=2023)

    for dropped in result.dropped_controls:
        assert dropped not in result.controls_used, (
            f"'{dropped}' was in dropped_controls but also in controls_used — "
            f"the report would falsely claim this variable was used in the model."
        )


# ── Empty DataFrame after filters ─────────────────────────────────────────────

def test_empty_after_filters_raises():
    """DataFrame with no conventional home purchase loans raises ValueError from prepare_for_analysis."""
    df = pd.DataFrame({
        "action_taken": [1, 2, 4, 5],  # no originated or denied
        "derived_race": ["White", "White", "White", "White"],
        "loan_type": [2, 2, 2, 2],     # all FHA, filtered out
    })
    with pytest.raises(ValueError, match="empty after applying"):
        prepare_for_analysis(df, validate_controls=False)


# ── MSA filter with nonexistent MSA ───────────────────────────────────────────

def test_msa_filter_nonexistent(base_df):
    """Filtering to a nonexistent MSA raises InsufficientDataError."""
    with pytest.raises(InsufficientDataError):
        adjusted_denial_disparity(base_df, msa="NONEXISTENT_MSA_9999", data_year=2023)


# ── DataSourceError ───────────────────────────────────────────────────────────

def test_data_source_error_fields():
    """DataSourceError carries url and reason."""
    from fair_lending_screener import DataSourceError
    err = DataSourceError(url="https://example.com", reason="Connection refused")
    assert err.url == "https://example.com"
    assert "Connection refused" in str(err)
