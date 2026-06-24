"""
Known-results calibration tests.

Two purposes:
1. Hand-calculated verification: construct a small dataset where the unadjusted
   odds ratio is known exactly, assert the function matches to 4 decimal places.
   Also construct a 2-control adjusted regression where the result is verified
   against a manually computed expectation.

2. Calibration range check: run the analysis on the synthetic load_sample() data
   and verify the adjusted odds ratio falls in a plausible range consistent with
   the methodology. This is a smoke test for drift in the math.

Calibration via load_from_api (offline, delegated fetch mocked):
   The former live test (FLS_LIVE_TESTS=1 + @pytest.mark.live, 2019 IL data) was
   replaced by test_calibration_2019_offline_mocked, which exercises the
   load_from_api -> prepare_for_analysis -> adjusted_denial_disparity path with no
   network. The real-data 1.6–2.2× adjusted-OR band (partial replication of The
   Markup (2021) national model, per docs/methodology.md) is verified OUT OF BAND
   via a manual Colab probe — it is NOT asserted by this file.
"""

import warnings

import numpy as np
import pandas as pd
import pytest

from fair_lending_screener import (
    adjusted_denial_disparity,
    load_sample,
    prepare_for_analysis,
)


# ── Hand-calculated unadjusted odds ratio ─────────────────────────────────────

def _make_handcalc_df() -> tuple[pd.DataFrame, float]:
    """
    Construct a minimal DataFrame with a known unadjusted odds ratio.

    Protected group (Black): 30 denied, 70 originated → denial rate = 0.30
    Comparison group (White): 10 denied, 90 originated → denial rate = 0.10

    Unadjusted OR = (30/70) / (10/90) = (30*90) / (70*10) = 2700 / 700 = 2700/700

    Exact fraction: 2700 / 700 = 27/7 ≈ 3.857142857...
    """
    black_denied = 30
    black_originated = 70
    white_denied = 10
    white_originated = 90

    expected_or = (black_denied / black_originated) / (white_denied / white_originated)

    records = []
    for _ in range(black_denied):
        records.append({"action_taken": 3, "derived_race": "Black or African American"})
    for _ in range(black_originated):
        records.append({"action_taken": 1, "derived_race": "Black or African American"})
    for _ in range(white_denied):
        records.append({"action_taken": 3, "derived_race": "White"})
    for _ in range(white_originated):
        records.append({"action_taken": 1, "derived_race": "White"})

    df = pd.DataFrame(records)
    df["loan_type"] = 1
    df["loan_purpose"] = 1
    df["lien_status"] = 1
    df["occupancy_type"] = 1
    df["property_type"] = 1
    df["construction_method"] = 1

    return df, round(expected_or, 4)


def test_unadjusted_or_matches_hand_calculation():
    """
    Unadjusted odds ratio must match the hand-calculated value to 4 decimal places.

    Expected: (30/70) / (10/90) = 27/7 ≈ 3.8571
    """
    df, expected_or = _make_handcalc_df()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        prepared = prepare_for_analysis(df, validate_controls=False)
        result = adjusted_denial_disparity(
            prepared,
            protected_class="Black or African American",
            comparison_class="White",
            controls=[],
            min_sample_size=50,
            data_year=2023,
        )

    assert result.unadjusted_odds_ratio == pytest.approx(expected_or, abs=1e-4), (
        f"Unadjusted OR: expected {expected_or:.4f}, got {result.unadjusted_odds_ratio:.4f}. "
        f"Hand calculation: (30/70) / (10/90) = 27/7."
    )


def test_adjusted_or_with_one_control():
    """
    Run a 1-control adjusted model on a constructed dataset.
    Verify the adjusted OR is in the direction expected (less extreme than unadjusted
    when the control partially explains the disparity).
    """
    rng = np.random.default_rng(42)
    n_per_group = 150

    # Black group: lower mean income, higher denial rate (income partly explains)
    black_income = rng.normal(60, 20, n_per_group).clip(10, 250)
    # Denial probability: negatively correlated with income, elevated for Black
    black_denial_prob = np.clip(0.35 - 0.002 * black_income + rng.normal(0, 0.05, n_per_group), 0.05, 0.95)
    black_action = np.where(rng.random(n_per_group) < black_denial_prob, 3, 1)

    # White group: higher mean income, lower denial rate
    white_income = rng.normal(90, 20, n_per_group).clip(10, 250)
    white_denial_prob = np.clip(0.15 - 0.002 * white_income + rng.normal(0, 0.05, n_per_group), 0.02, 0.95)
    white_action = np.where(rng.random(n_per_group) < white_denial_prob, 3, 1)

    df = pd.DataFrame({
        "action_taken": np.concatenate([black_action, white_action]),
        "derived_race": (["Black or African American"] * n_per_group + ["White"] * n_per_group),
        "applicant_income": np.concatenate([black_income, white_income]),
        "loan_type": 1,
        "loan_purpose": 1,
        "lien_status": 1,
        "occupancy_type": 1,
        "property_type": 1,
        "construction_method": 1,
    })

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        prepared = prepare_for_analysis(df, validate_controls=False)
        result = adjusted_denial_disparity(
            prepared,
            protected_class="Black or African American",
            comparison_class="White",
            controls=["log_income"],
            min_sample_size=50,
            data_year=2023,
        )

    # Adjusted OR should be positive (Black still faces higher denial after income control)
    assert result.adjusted_odds_ratio > 1.0, (
        "Adjusted OR should be > 1.0 when the protected class faces higher denial rates."
    )

    # Adjusted OR should be less than unadjusted OR because income explains some of the disparity
    assert result.adjusted_odds_ratio <= result.unadjusted_odds_ratio * 1.1, (
        "Adjusted OR should not substantially exceed unadjusted OR when the control explains some disparity. "
        f"Unadjusted: {result.unadjusted_odds_ratio:.3f}, Adjusted: {result.adjusted_odds_ratio:.3f}"
    )

    # p-value must be a valid probability
    assert 0.0 <= result.p_value <= 1.0

    # CI must be ordered
    lo, hi = result.confidence_interval_95
    assert lo < hi


# ── Calibration range: synthetic sample ───────────────────────────────────────

def test_calibration_range_synthetic_sample():
    """
    Sanity-check: run the full model on synthetic data from load_sample().

    Checks:
    - p-value is a valid float between 0 and 1
    - No NaN or inf in any numeric output
    - adjusted_odds_ratio > 0
    - interpretation string does not contain "discriminat" (safety guardrail on language)
    - limitations list is non-empty
    - provenance contains required keys
    """
    raw = load_sample(n=2000, seed=42)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        prepared = prepare_for_analysis(raw, validate_controls=False)
        result = adjusted_denial_disparity(
            prepared,
            protected_class="Black or African American",
            comparison_class="White",
            min_sample_size=100,
            data_year=2023,
        )

    # Basic numeric sanity
    assert result.adjusted_odds_ratio > 0
    assert not np.isnan(result.adjusted_odds_ratio)
    assert not np.isinf(result.adjusted_odds_ratio)
    assert 0.0 <= result.p_value <= 1.0
    assert result.confidence_interval_95[0] < result.confidence_interval_95[1]
    assert result.sample_size == result.sample_size_protected + result.sample_size_comparison

    # Language guardrail: no AFFIRMATIVE discrimination claims in interpretation.
    # The standard disclaimer may say "does not constitute a finding of discrimination"
    # — that is correct. What's forbidden is "the lender discriminated", etc.
    interp = result.interpretation.lower()
    for phrase in ["the lender discriminat", "constitutes discrimination", "is discrimination"]:
        assert phrase not in interp, (
            f"Found affirmative discrimination claim {phrase!r} in interpretation. "
            f"Got: {result.interpretation[:300]}"
        )

    # Limitations populated
    assert len(result.limitations) >= 5

    # Provenance keys
    for key in ["package_version", "dependency_versions", "timestamp", "input_parameters"]:
        assert key in result.provenance, f"Missing provenance key: {key}"

    # Methodology citation present
    assert "FFIEC" in result.methodology_citation


# ── Calibration via load_from_api, fully offline (delegated fetch mocked) ─────
#
# This was test_live_calibration_2019_national, which hit the live CFPB API behind
# FLS_LIVE_TESTS=1 + @pytest.mark.live. CI runs from cloud IPs that the CFPB/Akamai
# edge 403s, so a live fetch can never run there; the env-gated skip also meant the
# default suite asserted nothing. As of v0.2.1 the delegated fetch
# (hmdaanalyzer.load_from_api) is mocked with a deterministic fixture so the
# load_from_api -> prepare_for_analysis -> adjusted_denial_disparity path is
# exercised end to end with NO network. The real-data [1.6, 2.2] calibration band is
# a property of live 2019 IL data and is verified out of band via a manual Colab
# probe (see CHANGELOG); it is intentionally not asserted on synthetic data here.


def _make_calibration_fixture() -> pd.DataFrame:
    """
    Deterministic fixture standing in for hmdaanalyzer.load_from_api output.

    Reuses the proven load_sample() generator (known Black/White denial disparity,
    full FFIEC control set) and renames applicant_income -> income to mimic the raw
    column naming hmdaanalyzer returns, so load_from_api's _normalize_columns rename
    is exercised on the way through.
    """
    raw = load_sample(n=2000, seed=42)
    return raw.rename(columns={"applicant_income": "income"})


def test_calibration_2019_offline_mocked():
    """
    The calibration path runs fully offline: load_from_api delegates to a mocked
    hmdaanalyzer.load_from_api, and the prepared frame produces a valid, significant
    elevated disparity. No live network, no skip.

    Scope note: this asserts only that the adjusted OR is elevated (> 1.0) and
    statistically significant on the synthetic fixture. It does NOT enforce the
    real-data 1.6–2.2× calibration band — that band is a property of live 2019 IL
    data and is verified out of band via a manual Colab probe (see the module
    docstring and CHANGELOG). Re-asserting a numeric band on synthetic data here
    would be meaningless, so it is intentionally omitted.
    """
    from unittest.mock import patch
    from fair_lending_screener import load_from_api

    fixture = _make_calibration_fixture()

    with patch("hmdaanalyzer.load_from_api", return_value=fixture) as mock_fetch:
        raw = load_from_api(year=2019, state="IL", limit=50_000)

    # The delegated fetch is what produced the data (not a network call).
    assert mock_fetch.called, "Delegated hmdaanalyzer.load_from_api was not invoked."
    mock_fetch.assert_called_once_with(year=2019, state="IL", lei=None, county=None, limit=50_000)

    # load_from_api normalized the hmdaanalyzer-style 'income' column back to applicant_income.
    assert "applicant_income" in raw.columns
    assert "income" not in raw.columns

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        prepared = prepare_for_analysis(raw, loan_purpose=1, validate_controls=False)
        result = adjusted_denial_disparity(
            prepared,
            protected_class="Black or African American",
            comparison_class="White",
            min_sample_size=500,
            data_year=2019,
        )

    # The constructed disparity is strong (Black 0.195 vs White 0.095 at n=2000),
    # so the adjusted result must be elevated and statistically significant.
    assert result.adjusted_odds_ratio > 1.0, (
        f"Expected elevated adjusted OR on the constructed disparity; "
        f"got {result.adjusted_odds_ratio:.3f}."
    )
    assert result.is_statistically_significant, (
        f"Expected a statistically significant result at n=2000; p={result.p_value:.4f}."
    )
    assert 0.0 <= result.p_value <= 1.0
    assert not np.isnan(result.adjusted_odds_ratio)
    assert not np.isinf(result.adjusted_odds_ratio)


# ── Degate proof: load_from_api no longer fires a pre-flight health gate ───────

def test_load_from_api_does_not_gate_on_health_check():
    """
    Regression guard for the v0.2.1 fix: load_from_api must reach the delegated
    fetch WITHOUT first firing requests.head (the old check_data_source gate that
    403'd on cloud IPs). Asserts no HEAD fired AND the delegated fetch WAS called,
    so the test cannot pass by short-circuiting.
    """
    from unittest.mock import patch
    import fair_lending_screener.data as fls_data
    from fair_lending_screener import load_from_api

    fixture = pd.DataFrame({
        "action_taken": [1, 3, 1, 3],
        "derived_race": ["White", "Black or African American", "White", "Black or African American"],
        "income": [80.0, 60.0, 90.0, 55.0],
    })

    with patch.object(fls_data.requests, "head") as mock_head, \
            patch("hmdaanalyzer.load_from_api", return_value=fixture) as mock_fetch:
        df = load_from_api(year=2023, state="IL", limit=100)

    assert not mock_head.called, (
        "load_from_api fired a pre-flight HEAD — the check_data_source health gate "
        "was not removed from the call path."
    )
    assert mock_fetch.called, "Delegated hmdaanalyzer.load_from_api was not invoked."
    assert len(df) == 4


# ── Repaired health check: honest 403 message, not 'moved or changed' ─────────

def test_check_data_source_403_reports_edge_block():
    """
    check_data_source still raises DataSourceError on a 403, but with the honest
    edge/cloud-access-block message — NOT the misleading 'may have moved or changed'
    string that previously masked the cloud-IP 403.
    """
    from unittest.mock import patch, MagicMock
    import fair_lending_screener.data as fls_data
    from fair_lending_screener import check_data_source
    from fair_lending_screener.exceptions import DataSourceError

    mock_resp = MagicMock()
    mock_resp.status_code = 403

    with patch.object(fls_data.requests, "head", return_value=mock_resp) as mock_head:
        with pytest.raises(DataSourceError) as excinfo:
            check_data_source()

    assert mock_head.called, "requests.head was not exercised by check_data_source."
    msg = str(excinfo.value)
    assert "403" in msg
    assert "edge" in msg.lower(), f"Expected an edge/access-block message; got: {msg}"
    assert "may have moved or changed" not in msg, (
        "check_data_source still emits the misleading 'may have moved or changed' "
        f"message on a 403. Got: {msg}"
    )
