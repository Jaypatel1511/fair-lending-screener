"""
Adjusted denial disparity analysis using binary logistic regression.

Methodology: FFIEC Interagency Fair Lending Examination Procedures (2009).
Statistical method: statsmodels.api.Logit (inference-mode; provides p-values,
confidence intervals, pseudo-R², and convergence diagnostics).

See docs/methodology.md for the full specification including the regression
equation, control variable justifications, MSA fixed effects implementation,
and calibration target.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import importlib.metadata
import numpy as np
import pandas as pd
import statsmodels.api as sm

from .exceptions import (
    InsufficientDataError,
    InvalidProtectedClassError,
    MissingControlsError,
    ModelConvergenceError,
)
from .methodology import (
    FFIEC_FAIR_LENDING_PROCEDURES,
    FFIEC_URL,
    MARKUP_METHODOLOGY_CITATION,
    STANDARD_LIMITATIONS,
    STANDARD_DISCLAIMER,
    WOOLDRIDGE_OVB_CITATION,
)

CFPB_API_BASE = "https://ffiec.cfpb.gov/v2/data-browser-api/view"

# Minimum observations per MSA to receive its own dummy variable.
# Below this threshold, the MSA is assigned to the MSA_other reference category.
_MSA_DUMMY_MIN_OBS = 30

# Minimum observations per group (protected + comparison) before raising InsufficientGroupSizeError.
_MIN_GROUP_OBS = 10

# Default logistic regression maximum iterations.
_DEFAULT_MAX_ITER = 200

# FFIEC-standard controls, in regression order.
# Log-transformed versions (log_income, log_loan_amount, log_property_value) are added
# by data.prepare_for_analysis(). Raw fields are listed here for documentation.
_FFIEC_CONTROLS = [
    "log_income",          # log(applicant_income + 1)
    "log_loan_amount",     # log(loan_amount)
    "loan_to_value_ratio", # entered as-is (already a bounded ratio)
    "log_property_value",  # log(property_value + 1)
]

# DTI dummy columns (bin 1 = ≤35% is the baseline, not included as a dummy)
_DTI_DUMMY_COLS = ["dti_36_42", "dti_43_49", "dti_ge50", "dti_missing"]

_METHODOLOGY_CITATION = (
    f"{FFIEC_FAIR_LENDING_PROCEDURES} {FFIEC_URL} | {MARKUP_METHODOLOGY_CITATION}"
)


@dataclass
class DisparityResult:
    """
    Output of adjusted_denial_disparity().

    All fields are populated on success. Raise typed exceptions on failure —
    this dataclass is never returned in a partial or error state.
    """

    # ── Group labels ──────────────────────────────────────────────────────────
    protected_class: str
    comparison_class: str

    # ── Core statistical outputs ───────────────────────────────────────────────
    unadjusted_odds_ratio: float
    adjusted_odds_ratio: float
    confidence_interval_95: tuple[float, float]
    p_value: float

    # ── Sample size ───────────────────────────────────────────────────────────
    sample_size: int
    sample_size_protected: int
    sample_size_comparison: int

    # ── Model metadata ────────────────────────────────────────────────────────
    controls_used: list[str]
    dropped_controls: list[str]   # controls excluded by zero-variance check (see disparity.py)
    model_diagnostics: dict       # pseudo_r2, log_likelihood, converged, n_iterations, n_msa_dummies
    methodology_citation: str
    limitations: list[str]

    # ── Interpretation ────────────────────────────────────────────────────────
    is_statistically_significant: bool
    interpretation: str        # journalist-legible, never uses "discriminates"

    # ── Provenance (A2: legal defensibility) ──────────────────────────────────
    provenance: dict   # package_version, dependency_versions, timestamp, input_parameters


def adjusted_denial_disparity(
    df: pd.DataFrame,
    protected_class: str = "Black or African American",
    comparison_class: str = "White",
    controls: Optional[list[str]] = None,
    msa: Optional[str] = None,
    min_sample_size: int = 100,
) -> DisparityResult:
    """
    Compute the adjusted denial disparity between a protected class and a comparison class.

    Uses binary logistic regression (statsmodels.api.Logit) with FFIEC-standard controls.
    Returns an adjusted odds ratio, 95% confidence interval, p-value, and model diagnostics.

    The input DataFrame must be prepared with data.prepare_for_analysis() first.

    Args:
        df:               DataFrame prepared by data.prepare_for_analysis().
        protected_class:  Race/ethnicity string matching derived_race values
                          (default: "Black or African American").
        comparison_class: Reference group for the odds ratio (default: "White").
        controls:         List of column names to use as controls. Defaults to
                          FFIEC-standard controls available in the DataFrame.
                          Pass [] for unadjusted only (not recommended).
        msa:              If provided, restrict analysis to this MSA code
                          (value of msa_md column).
        min_sample_size:  Minimum combined observations required. Below this
                          threshold, InsufficientDataError is raised.
                          Citation: Peduzzi et al. (1996), J. Clin. Epidemiol. 49(12):1373–1379.

    Returns:
        DisparityResult dataclass.

    Raises:
        InvalidProtectedClassError: protected_class or comparison_class not in data.
        InsufficientDataError: combined sample below min_sample_size.
        MissingControlsError: an explicitly requested control column is absent.
        ModelConvergenceError: logistic regression fails to converge.
    """
    df = df.copy()

    # ── MSA filter ────────────────────────────────────────────────────────────
    if msa is not None:
        if "msa_md" not in df.columns:
            raise MissingControlsError(
                missing_columns=["msa_md"],
                available_columns=sorted(df.columns.tolist()),
            )
        df = df[df["msa_md"] == msa]
        if df.empty:
            raise InsufficientDataError(0, min_sample_size, protected_class, comparison_class)

    # ── Validate protected class values ───────────────────────────────────────
    race_col = "derived_race"
    if race_col not in df.columns:
        raise MissingControlsError(
            missing_columns=[race_col],
            available_columns=sorted(df.columns.tolist()),
        )

    valid_races = sorted(df[race_col].dropna().unique().tolist())

    if protected_class not in df[race_col].values:
        raise InvalidProtectedClassError(protected_class, race_col, valid_races)
    if comparison_class not in df[race_col].values:
        raise InvalidProtectedClassError(comparison_class, race_col, valid_races)

    # ── Restrict to protected vs. comparison class ────────────────────────────
    mask = df[race_col].isin([protected_class, comparison_class])
    df = df[mask].copy()
    df["protected_class_ind"] = (df[race_col] == protected_class).astype(int)

    n_protected = int((df[race_col] == protected_class).sum())
    n_comparison = int((df[race_col] == comparison_class).sum())
    n_total = len(df)

    # ── Sample size check ─────────────────────────────────────────────────────
    if n_total < min_sample_size:
        raise InsufficientDataError(n_total, min_sample_size, protected_class, comparison_class)

    if n_protected < _MIN_GROUP_OBS or n_comparison < _MIN_GROUP_OBS:
        from .exceptions import InsufficientGroupSizeError
        small_group = protected_class if n_protected < _MIN_GROUP_OBS else comparison_class
        small_n = n_protected if n_protected < _MIN_GROUP_OBS else n_comparison
        raise InsufficientGroupSizeError(small_group, small_n, _MIN_GROUP_OBS)

    # ── Check for degenerate outcomes ─────────────────────────────────────────
    if "is_denied" not in df.columns:
        raise MissingControlsError(
            missing_columns=["is_denied"],
            available_columns=sorted(df.columns.tolist()),
        )
    _check_outcome_variation(df, protected_class, comparison_class)

    # ── Unadjusted odds ratio (simple 2×2 table) ──────────────────────────────
    unadjusted_or = _compute_unadjusted_or(df, protected_class, comparison_class)

    # ── Resolve control columns ───────────────────────────────────────────────
    if controls is None:
        controls = _resolve_default_controls(df)
    else:
        # Validate explicitly requested controls
        missing = [c for c in controls if c not in df.columns]
        if missing:
            raise MissingControlsError(
                missing_columns=missing,
                available_columns=sorted(df.columns.tolist()),
            )

    # ── Add DTI dummies ───────────────────────────────────────────────────────
    dti_dummies_used = []
    if "dti_bin" in df.columns:
        dti_dummies_used, df = _add_dti_dummies(df)

    # ── Add MSA dummies ───────────────────────────────────────────────────────
    msa_dummies_used = []
    if "msa_md" in df.columns and msa is None:
        msa_dummies_used, df = _add_msa_dummies(df)

    # ── Assemble feature matrix ───────────────────────────────────────────────
    feature_cols = (
        ["protected_class_ind"]
        + [c for c in controls if c in df.columns]
        + dti_dummies_used
        + msa_dummies_used
    )
    feature_cols = _deduplicate_ordered(feature_cols)

    X = df[feature_cols].copy()
    X = X.apply(pd.to_numeric, errors="coerce")

    # Drop rows with any NaN in features or outcome
    valid = X.notna().all(axis=1) & df["is_denied"].notna()
    X = X[valid]
    y = df.loc[valid, "is_denied"]

    if len(X) < min_sample_size:
        raise InsufficientDataError(len(X), min_sample_size, protected_class, comparison_class)

    # Drop zero-variance columns (e.g., dti_missing when DTI is complete, MSA dummies
    # that cover only one group, or filter-constant columns like lien_status_dummy).
    # A zero-variance column contributes nothing and causes a singular Hessian.
    zero_var = [c for c in X.columns if c != "protected_class_ind" and X[c].nunique() <= 1]
    if zero_var:
        warnings.warn(
            f"Dropping {len(zero_var)} zero-variance control(s) before fitting — "
            f"they are constant in this sample and would cause a singular Hessian: {zero_var}. "
            f"Common cause: 'dti_missing' when no DTI values are missing, or an MSA dummy "
            f"covering only one outcome category. Results use the remaining controls.",
            UserWarning,
            stacklevel=2,
        )
        X = X.drop(columns=zero_var)

    # Rebuild controls_used to reflect what survived after zero-variance drop
    dropped_controls = zero_var
    controls_used = [c for c in X.columns if c != "protected_class_ind"]

    X_with_const = sm.add_constant(X, has_constant="add")

    # ── Fit logistic regression ───────────────────────────────────────────────
    result = _fit_logit(X_with_const, y)

    # ── Extract outputs ───────────────────────────────────────────────────────
    coef = result.params["protected_class_ind"]
    adjusted_or = float(np.exp(coef))

    ci_log = result.conf_int().loc["protected_class_ind"]
    ci = (float(np.exp(ci_log[0])), float(np.exp(ci_log[1])))

    p_value = float(result.pvalues["protected_class_ind"])
    is_sig = (p_value < 0.05) and (ci[0] > 1.0 or ci[1] < 1.0)

    pseudo_r2 = float(result.prsquared)
    log_lik = float(result.llf)

    controls_used = [c for c in feature_cols if c != "protected_class_ind"]

    diagnostics = {
        "pseudo_r2_mcfadden": pseudo_r2,
        "log_likelihood": log_lik,
        "converged": result.mle_retvals.get("converged", True) if hasattr(result, "mle_retvals") else True,
        "n_iterations": result.mle_retvals.get("iterations", None) if hasattr(result, "mle_retvals") else None,
        "n_msa_dummies": len(msa_dummies_used),
        "n_obs_in_model": int(len(X)),
        "pseudo_r2_flag": "BELOW_0.05_THRESHOLD" if pseudo_r2 < 0.05 else (
            "BELOW_0.10_THRESHOLD" if pseudo_r2 < 0.10 else "OK"
        ),
    }

    interpretation = _build_interpretation(
        protected_class=protected_class,
        comparison_class=comparison_class,
        unadjusted_or=unadjusted_or,
        adjusted_or=adjusted_or,
        ci=ci,
        p_value=p_value,
        is_sig=is_sig,
        controls_used=controls_used,
        n_total=n_total,
    )

    provenance = _build_provenance(
        protected_class=protected_class,
        comparison_class=comparison_class,
        controls=controls,
        msa=msa,
        min_sample_size=min_sample_size,
    )

    return DisparityResult(
        protected_class=protected_class,
        comparison_class=comparison_class,
        unadjusted_odds_ratio=unadjusted_or,
        adjusted_odds_ratio=adjusted_or,
        confidence_interval_95=ci,
        p_value=p_value,
        sample_size=n_total,
        sample_size_protected=n_protected,
        sample_size_comparison=n_comparison,
        controls_used=controls_used,
        dropped_controls=dropped_controls,
        model_diagnostics=diagnostics,
        methodology_citation=_METHODOLOGY_CITATION,
        limitations=STANDARD_LIMITATIONS.copy(),
        is_statistically_significant=is_sig,
        interpretation=interpretation,
        provenance=provenance,
    )


# ── Private helpers ────────────────────────────────────────────────────────────

def _check_outcome_variation(df: pd.DataFrame, protected: str, comparison: str) -> None:
    """Raise a clear error if one group has only denials or only originations."""
    for group, label in [(protected, "protected"), (comparison, "comparison")]:
        sub = df[df["derived_race"] == group]["is_denied"]
        if sub.nunique() < 2:
            outcome = "all denials" if sub.iloc[0] == 1 else "all originations"
            raise ModelConvergenceError(
                iterations=0,
                final_log_likelihood=float("nan"),
                message=(
                    f"Perfect separation: {group!r} ({label} class) has {outcome} "
                    f"in this sample. Logistic regression cannot estimate a coefficient. "
                    f"Expand the sample geography or year range."
                ),
            )


def _compute_unadjusted_or(df: pd.DataFrame, protected: str, comparison: str) -> float:
    """Compute the unadjusted odds ratio from a simple 2×2 table."""
    p_denied = (df[df["derived_race"] == protected]["is_denied"] == 1).mean()
    c_denied = (df[df["derived_race"] == comparison]["is_denied"] == 1).mean()

    if c_denied == 0 or p_denied == 0:
        return float("nan")
    if c_denied == 1 or p_denied == 1:
        return float("nan")

    p_odds = p_denied / (1 - p_denied)
    c_odds = c_denied / (1 - c_denied)
    return round(p_odds / c_odds, 4)


def _resolve_default_controls(df: pd.DataFrame) -> list[str]:
    """Return FFIEC-standard controls that are present in the DataFrame."""
    available = []
    for col in _FFIEC_CONTROLS:
        if col in df.columns:
            available.append(col)
        else:
            warnings.warn(
                f"FFIEC-standard control {col!r} not found in DataFrame; omitting from model. "
                f"Use data.prepare_for_analysis() on real HMDA data (2018+) for the full control set.",
                UserWarning,
                stacklevel=3,
            )
    return available


def _add_dti_dummies(df: pd.DataFrame) -> tuple[list[str], pd.DataFrame]:
    """Create DTI dummy columns. Baseline = dti_le35 (not included as a column)."""
    added = []
    for col in _DTI_DUMMY_COLS:
        df[col] = (df["dti_bin"] == col).astype(int)
        added.append(col)
    return added, df


def _add_msa_dummies(df: pd.DataFrame) -> tuple[list[str], pd.DataFrame]:
    """
    Create MSA dummy variables.

    MSAs with < _MSA_DUMMY_MIN_OBS observations are assigned to MSA_other (reference).
    The most-common qualifying MSA serves as the baseline (dropped automatically by
    pd.get_dummies with drop_first=False; we handle baseline via reference category).
    """
    msa_counts = df["msa_md"].value_counts()
    qualifying_msas = msa_counts[msa_counts >= _MSA_DUMMY_MIN_OBS].index.tolist()

    if not qualifying_msas:
        return [], df

    # Assign sparse MSAs to reference category
    df["_msa_for_dummy"] = df["msa_md"].where(
        df["msa_md"].isin(qualifying_msas), other="MSA_other"
    )

    # Sort so the first MSA (alphabetically) is dropped as baseline
    sorted_msas = sorted(qualifying_msas)
    baseline_msa = sorted_msas[0]

    dummy_cols = []
    for msa_val in sorted_msas[1:]:  # skip baseline
        col = f"msa__{msa_val}"
        df[col] = (df["_msa_for_dummy"] == msa_val).astype(int)
        dummy_cols.append(col)

    df = df.drop(columns=["_msa_for_dummy"])
    return dummy_cols, df


def _fit_logit(X: pd.DataFrame, y: pd.Series) -> sm.regression.linear_model.RegressionResultsWrapper:
    """Fit statsmodels Logit and raise ModelConvergenceError on failure."""
    try:
        model = sm.Logit(y, X)
        result = model.fit(maxiter=_DEFAULT_MAX_ITER, disp=False)
    except Exception as exc:
        raise ModelConvergenceError(
            iterations=_DEFAULT_MAX_ITER,
            final_log_likelihood=float("nan"),
            message=str(exc),
        ) from exc

    if hasattr(result, "mle_retvals"):
        converged = result.mle_retvals.get("converged", True)
        if not converged:
            iters = result.mle_retvals.get("iterations", _DEFAULT_MAX_ITER)
            llf = float(result.llf)
            raise ModelConvergenceError(iterations=iters, final_log_likelihood=llf)

    return result


def _build_interpretation(
    protected_class: str,
    comparison_class: str,
    unadjusted_or: float,
    adjusted_or: float,
    ci: tuple[float, float],
    p_value: float,
    is_sig: bool,
    controls_used: list[str],
    n_total: int,
) -> str:
    """
    Build a journalist-legible interpretation string.

    CRITICAL: does not use "discriminates" or "discrimination".
    Uses "statistically significant adjusted disparity" per methodology.md.
    """
    n_controls = len(controls_used)

    if is_sig:
        sig_phrase = (
            f"a statistically significant adjusted disparity "
            f"(adjusted odds ratio: {adjusted_or:.2f}×, "
            f"95% CI: {ci[0]:.2f}–{ci[1]:.2f}, p={p_value:.4f})"
        )
        direction = (
            f"{protected_class} applicants faced {adjusted_or:.2f}× higher odds of denial "
            f"than {comparison_class} applicants after controlling for {n_controls} legitimate "
            f"underwriting factors."
        )
    else:
        sig_phrase = (
            f"no statistically significant adjusted disparity "
            f"(adjusted odds ratio: {adjusted_or:.2f}×, "
            f"95% CI: {ci[0]:.2f}–{ci[1]:.2f}, p={p_value:.4f})"
        )
        direction = (
            f"The adjusted odds ratio of {adjusted_or:.2f}× was not statistically significant "
            f"after controlling for {n_controls} legitimate underwriting factors."
        )

    unadj_str = f"{unadjusted_or:.2f}×" if not (isinstance(unadjusted_or, float) and np.isnan(unadjusted_or)) else "N/A"

    return (
        f"Analysis of {n_total:,} applications ({protected_class} vs. {comparison_class}) "
        f"found {sig_phrase}. "
        f"Unadjusted denial rate disparity: {unadj_str}. "
        f"{direction} "
        f"This is a screening signal, not a finding of discrimination. "
        f"{STANDARD_DISCLAIMER}"
    )


def _build_provenance(
    protected_class: str,
    comparison_class: str,
    controls: Optional[list[str]],
    msa: Optional[str],
    min_sample_size: int,
) -> dict:
    """Build the provenance block for legal/reproducibility defensibility (addition A2)."""
    try:
        pkg_version = importlib.metadata.version("fair-lending-screener")
    except importlib.metadata.PackageNotFoundError:
        pkg_version = "dev"

    try:
        import statsmodels
        sm_version = statsmodels.__version__
    except Exception:
        sm_version = "unknown"

    try:
        import pandas as _pd
        pd_version = _pd.__version__
    except Exception:
        pd_version = "unknown"

    try:
        np_version = np.__version__
    except Exception:
        np_version = "unknown"

    return {
        "package_version": pkg_version,
        "dependency_versions": {
            "statsmodels": sm_version,
            "pandas": pd_version,
            "numpy": np_version,
        },
        "data_source_url": CFPB_API_BASE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_parameters": {
            "protected_class": protected_class,
            "comparison_class": comparison_class,
            "controls": controls,
            "msa": msa,
            "min_sample_size": min_sample_size,
        },
        "methodology_reference": "docs/methodology.md",
        "calibration_reference": (
            "The Markup (2021): adjusted OR 1.8× for Black vs. White, "
            "2019 HMDA conventional first-lien home purchase. "
            "Expected range for this model (without AUS/credit score controls): 1.6–2.2×."
        ),
    }


def _deduplicate_ordered(lst: list[str]) -> list[str]:
    """Remove duplicates while preserving order."""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]
