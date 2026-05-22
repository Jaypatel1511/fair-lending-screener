"""Tests for report generation and A7 safety guardrails."""

import warnings

import pytest

from fair_lending_screener import (
    adjusted_denial_disparity,
    generate_disparity_report,
    load_sample,
    prepare_for_analysis,
)


@pytest.fixture(scope="module")
def result():
    raw = load_sample(n=2000, seed=11)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        prepared = prepare_for_analysis(raw, validate_controls=False)
        return adjusted_denial_disparity(prepared, min_sample_size=100, data_year=2023)


def test_report_is_string(result):
    report = generate_disparity_report(result)
    assert isinstance(report, str)
    assert len(report) > 200


def test_report_contains_headline(result):
    report = generate_disparity_report(result)
    assert "## Headline Finding" in report


def test_report_contains_key_numbers(result):
    report = generate_disparity_report(result)
    assert "Adjusted odds ratio" in report or "adjusted odds ratio" in report
    assert "Unadjusted odds ratio" in report or "unadjusted" in report.lower()
    assert "95%" in report or "confidence" in report.lower()


def test_report_contains_limitations(result):
    report = generate_disparity_report(result)
    assert "Limitations" in report
    assert "credit score" in report.lower()


def test_report_contains_what_not_prove(result):
    report = generate_disparity_report(result)
    assert "does NOT prove" in report or "does not prove" in report.lower() or "Does NOT Prove" in report


def test_report_no_affirmative_discrimination_language(result):
    """Report must never affirmatively claim the lender discriminated."""
    report = generate_disparity_report(result, lender_name="Test Bank")
    for phrase in ["the lender discriminat", "constitutes discrimination", "is discrimination"]:
        assert phrase not in report.lower(), (
            f"Found affirmative discrimination claim {phrase!r} in report."
        )


def test_report_contains_reproducibility(result):
    report = generate_disparity_report(result)
    assert "Reproducibility" in report
    assert "package_version" in report
    assert "timestamp" in report


def test_report_contains_ffiec_citation(result):
    report = generate_disparity_report(result, include_methodology=True)
    assert "FFIEC" in report


def test_report_with_lender_name_significant(result):
    """When result passes all guardrails, lender name appears in the report."""
    pseudo_r2 = result.model_diagnostics.get("pseudo_r2_mcfadden", 0)
    if not result.is_statistically_significant:
        pytest.skip("Result not significant — guardrail suppresses lender name")
    if pseudo_r2 < 0.05:
        pytest.skip(
            f"Synthetic data pseudo-R²={pseudo_r2:.3f} < 0.05 — guardrail suppresses "
            "lender name (this is correct behavior; synthetic data has low model fit)"
        )
    report = generate_disparity_report(result, lender_name="First National Bank")
    assert "First National Bank" in report


# ── Guardrail tests ───────────────────────────────────────────────────────────

def _make_nonsig_result():
    """Build a result with a high p-value to trigger the guardrail."""
    from fair_lending_screener.disparity import DisparityResult
    from fair_lending_screener.methodology import STANDARD_LIMITATIONS, FFIEC_FAIR_LENDING_PROCEDURES

    return DisparityResult(
        protected_class="Black or African American",
        comparison_class="White",
        unadjusted_odds_ratio=1.05,
        adjusted_odds_ratio=1.03,
        confidence_interval_95=(0.85, 1.25),
        p_value=0.72,
        sample_size=500,
        sample_size_protected=120,
        sample_size_comparison=380,
        controls_used=["log_income", "loan_to_value_ratio"],
        dropped_controls=[],
        model_diagnostics={
            "pseudo_r2_mcfadden": 0.15,
            "log_likelihood": -280.0,
            "converged": True,
            "n_msa_dummies": 5,
            "n_obs_in_model": 500,
            "pseudo_r2_flag": "OK",
        },
        methodology_citation=FFIEC_FAIR_LENDING_PROCEDURES,
        limitations=STANDARD_LIMITATIONS.copy(),
        is_statistically_significant=False,
        interpretation="No significant disparity found.",
        provenance={
            "package_version": "0.1.0",
            "dependency_versions": {},
            "data_source_url": "test",
            "timestamp": "2026-05-21T00:00:00Z",
            "input_parameters": {},
        },
    )


def test_report_with_lender_name_significant_strong_model():
    """When all guardrails pass (significant, converged, pseudo-R²≥0.05), lender name is in headline."""
    from fair_lending_screener.disparity import DisparityResult
    from fair_lending_screener.methodology import STANDARD_LIMITATIONS, FFIEC_FAIR_LENDING_PROCEDURES

    strong_result = DisparityResult(
        protected_class="Black or African American",
        comparison_class="White",
        unadjusted_odds_ratio=2.1,
        adjusted_odds_ratio=1.9,
        confidence_interval_95=(1.4, 2.6),
        p_value=0.002,
        sample_size=5000,
        sample_size_protected=1200,
        sample_size_comparison=3800,
        controls_used=["log_income", "log_loan_amount", "loan_to_value_ratio"],
        dropped_controls=[],
        model_diagnostics={
            "pseudo_r2_mcfadden": 0.18,
            "log_likelihood": -2800.0,
            "converged": True,
            "n_msa_dummies": 15,
            "n_obs_in_model": 5000,
            "pseudo_r2_flag": "OK",
        },
        methodology_citation=FFIEC_FAIR_LENDING_PROCEDURES,
        limitations=STANDARD_LIMITATIONS.copy(),
        is_statistically_significant=True,
        interpretation="Statistically significant adjusted disparity found.",
        provenance={
            "package_version": "0.1.1",
            "dependency_versions": {},
            "data_source_url": "test",
            "timestamp": "2026-05-21T00:00:00Z",
            "input_parameters": {},
        },
    )

    report = generate_disparity_report(strong_result, lender_name="Test Community Bank")
    headline_section = report.split("## Headline Finding")[1].split("##")[0]
    assert "Test Community Bank" in headline_section, (
        f"Expected 'Test Community Bank' in report headline when all guardrails pass. "
        f"Headline section: {headline_section[:300]}"
    )


def test_guardrail_suppresses_lender_name_when_nonsignificant():
    """Lender name must be withheld when p > 0.05."""
    result = _make_nonsig_result()
    report = generate_disparity_report(result, lender_name="Test Community Bank")
    # Name should NOT appear unqualified in the headline
    assert "withheld" in report or "Test Community Bank" not in report.split("## Headline")[1].split("##")[0]


def test_guardrail_flags_shown_when_nonsignificant():
    """Quality flags section must appear when p > 0.05."""
    result = _make_nonsig_result()
    report = generate_disparity_report(result, lender_name="Test Bank")
    assert "Quality Flags" in report or "quality flags" in report.lower()
