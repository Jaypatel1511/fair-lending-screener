"""Happy-path and parametric tests for adjusted_denial_disparity()."""

import warnings

import pytest

from fair_lending_screener import (
    adjusted_denial_disparity,
    DisparityResult,
    load_sample,
    prepare_for_analysis,
)


@pytest.fixture(scope="module")
def prepared_df():
    raw = load_sample(n=2000, seed=7)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return prepare_for_analysis(raw, validate_controls=False)


def test_returns_disparity_result(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100)
    assert isinstance(result, DisparityResult)


def test_adjusted_or_is_positive(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100)
    assert result.adjusted_odds_ratio > 0


def test_ci_is_ordered(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100)
    lo, hi = result.confidence_interval_95
    assert lo < hi


def test_p_value_valid(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100)
    assert 0.0 <= result.p_value <= 1.0


def test_sample_sizes_consistent(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100)
    assert result.sample_size == result.sample_size_protected + result.sample_size_comparison


def test_controls_used_is_list(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100)
    assert isinstance(result.controls_used, list)


def test_limitations_present(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100)
    assert len(result.limitations) >= 5
    assert any("credit score" in lim.lower() for lim in result.limitations)


def test_provenance_has_required_keys(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100)
    for key in ["package_version", "dependency_versions", "timestamp", "input_parameters"]:
        assert key in result.provenance


def test_interpretation_no_affirmative_discrimination_language(prepared_df):
    """
    The interpretation must not affirmatively say the lender discriminates.
    The word 'discrimination' may appear in the standard disclaimer context
    ("does not constitute a finding of discrimination") — that is correct usage.
    What is forbidden is affirmative claims like "the lender discriminated".
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100)
    interp = result.interpretation.lower()
    forbidden_phrases = [
        "the lender discriminat",
        "lender discriminat",
        "constitutes discrimination",
        "is discrimination",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in interp, (
            f"Found forbidden affirmative discrimination language: {phrase!r}\n"
            f"Interpretation: {result.interpretation[:300]}"
        )


def test_methodology_citation_contains_ffiec(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100)
    assert "FFIEC" in result.methodology_citation


def test_is_statistically_significant_consistent_with_p_value(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100)
    lo, hi = result.confidence_interval_95
    if result.is_statistically_significant:
        assert result.p_value < 0.05
        assert lo > 1.0 or hi < 1.0
    else:
        assert result.p_value >= 0.05 or (lo <= 1.0 <= hi)


def test_model_diagnostics_has_pseudo_r2(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100)
    assert "pseudo_r2_mcfadden" in result.model_diagnostics
    r2 = result.model_diagnostics["pseudo_r2_mcfadden"]
    assert 0.0 <= r2 <= 1.0


@pytest.mark.parametrize("protected,comparison", [
    ("Black or African American", "White"),
    ("Asian", "White"),
    ("Hispanic or Latino", "White"),
])
def test_multiple_protected_classes(prepared_df, protected, comparison):
    """Analysis should run for any racial group present in the data."""
    if protected not in prepared_df["derived_race"].values:
        pytest.skip(f"{protected!r} not in synthetic sample")
    if comparison not in prepared_df["derived_race"].values:
        pytest.skip(f"{comparison!r} not in synthetic sample")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(
            prepared_df,
            protected_class=protected,
            comparison_class=comparison,
            min_sample_size=50,
        )
    assert isinstance(result, DisparityResult)
    assert result.adjusted_odds_ratio > 0
