"""Happy-path and parametric tests for adjusted_denial_disparity()."""

import warnings

import numpy as np
import pandas as pd
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
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100, data_year=2023)
    assert isinstance(result, DisparityResult)


def test_adjusted_or_is_positive(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100, data_year=2023)
    assert result.adjusted_odds_ratio > 0


def test_ci_is_ordered(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100, data_year=2023)
    lo, hi = result.confidence_interval_95
    assert lo < hi


def test_p_value_valid(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100, data_year=2023)
    assert 0.0 <= result.p_value <= 1.0


def test_sample_sizes_consistent(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100, data_year=2023)
    assert result.sample_size == result.sample_size_protected + result.sample_size_comparison


def test_controls_used_is_list(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100, data_year=2023)
    assert isinstance(result.controls_used, list)


def test_limitations_present(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100, data_year=2023)
    assert len(result.limitations) >= 5
    assert any("credit score" in lim.lower() for lim in result.limitations)


def test_provenance_has_required_keys(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100, data_year=2023)
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
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100, data_year=2023)
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
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100, data_year=2023)
    assert "FFIEC" in result.methodology_citation


def test_is_statistically_significant_consistent_with_p_value(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100, data_year=2023)
    lo, hi = result.confidence_interval_95
    if result.is_statistically_significant:
        assert result.p_value < 0.05
        assert lo > 1.0 or hi < 1.0
    else:
        assert result.p_value >= 0.05 or (lo <= 1.0 <= hi)


def test_model_diagnostics_has_pseudo_r2(prepared_df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adjusted_denial_disparity(prepared_df, min_sample_size=100, data_year=2023)
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
            data_year=2023,
        )
    assert isinstance(result, DisparityResult)
    assert result.adjusted_odds_ratio > 0


# ── Through-function non-significant disclaimer test ──────────────────────────

def test_nonsig_result_uses_correct_disclaimers():
    """
    Through-function regression test: when adjusted_denial_disparity() returns a
    non-significant result, BOTH limitations[-1] AND interpretation must use
    STANDARD_DISCLAIMER_NON_SIGNIFICANT, not STANDARD_DISCLAIMER.

    Catches HIGH-NEW-1 (interpretation field) and MED-A (limitations field)
    simultaneously via the real function path — not a hand-constructed result.

    Data: 300 Black + 300 White applicants, identical 10% denial rates, controls
    drawn from the same random distribution. OR ≈ 1.0 → p >> 0.05 → non-significant.
    """
    from fair_lending_screener.methodology import (
        STANDARD_DISCLAIMER,
        STANDARD_DISCLAIMER_NON_SIGNIFICANT,
    )

    rng = np.random.default_rng(0)
    n_per_group = 300
    denial_count = int(n_per_group * 0.10)  # exactly 30 denials per group

    records = []
    for race in ["Black or African American", "White"]:
        actions = [3] * denial_count + [1] * (n_per_group - denial_count)
        rng.shuffle(actions)
        for action in actions:
            income = float(max(20.0, rng.normal(85, 30)))
            loan_amount = float(max(50.0, income * rng.uniform(2.5, 5.5)))
            records.append({
                "action_taken": action,
                "derived_race": race,
                "loan_type": 1,
                "loan_purpose": 1,
                "lien_status": 1,
                "occupancy_type": 1,
                "property_type": 1,
                "construction_method": 1,
                "applicant_income": income,
                "loan_amount": loan_amount,
                "loan_to_value_ratio": float(rng.uniform(60, 95)),
                "debt_to_income_ratio": float(rng.choice([28.0, 35.0, 41.0, 48.0])),
                "property_value": loan_amount * float(rng.uniform(1.05, 1.40)),
                "msa_md": f"MSA_{int(rng.integers(1, 11)):03d}",
            })

    df = pd.DataFrame(records)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        prepared = prepare_for_analysis(df, validate_controls=False)
        result = adjusted_denial_disparity(prepared, min_sample_size=100, data_year=2023)

    assert result.is_statistically_significant is False, (
        f"Expected non-significant result (equal 10% denial rates); "
        f"got p={result.p_value:.4f}, OR={result.adjusted_odds_ratio:.3f}."
    )

    # MED-A: limitations[-1] must be the non-significant disclaimer
    assert result.limitations[-1] == STANDARD_DISCLAIMER_NON_SIGNIFICANT, (
        f"MED-A regression: limitations[-1] should be STANDARD_DISCLAIMER_NON_SIGNIFICANT.\n"
        f"Got: {result.limitations[-1]!r}"
    )

    # HIGH-NEW-1: interpretation must NOT contain the significant-result disclaimer text
    assert STANDARD_DISCLAIMER not in result.interpretation, (
        "HIGH-NEW-1 regression: STANDARD_DISCLAIMER ('identifies a statistically significant "
        "adjusted disparity') found in a non-significant result.interpretation."
    )

    # Interpretation must contain the correct non-significant disclaimer
    assert STANDARD_DISCLAIMER_NON_SIGNIFICANT in result.interpretation, (
        "Expected STANDARD_DISCLAIMER_NON_SIGNIFICANT in result.interpretation for non-significant result."
    )
