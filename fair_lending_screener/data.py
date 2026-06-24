"""
Data loading and preparation for fair lending disparity analysis.

Wraps hmda-analyzer (hmdaanalyzer) for data access and applies the
dataset filters specified in docs/methodology.md before any analysis.

All filtering decisions are documented with citations. The public HMDA
dataset lacks credit score, AUS recommendations, and asset data — see
docs/methodology.md § "HMDA Public Data Limitations" for the full list.
"""

from __future__ import annotations

import warnings
from typing import Optional

import numpy as np
import pandas as pd
import requests

from .exceptions import DataSourceError, MissingControlsError

CFPB_API_HEALTH_URL = "https://ffiec.cfpb.gov/v2/data-browser-api/view/csv"
CFPB_API_BASE = "https://ffiec.cfpb.gov/v2/data-browser-api/view"

# Minimum columns that must be present for any analysis to proceed.
# Controls may be absent (handled via graceful degradation + warning),
# but these identity/outcome columns are non-negotiable.
_REQUIRED_COLUMNS = {"action_taken", "derived_race"}

# The FFIEC-standard controls this package targets.
# Columns present in real HMDA data from the CFPB API but absent from
# hmda-analyzer's synthetic load_sample() output are marked (*).
STANDARD_CONTROLS = [
    "applicant_income",        # also appears as "income" in hmdaanalyzer sample
    "loan_amount",
    "loan_to_value_ratio",     # (*) not in hmdaanalyzer sample
    "debt_to_income_ratio",    # (*) not in hmdaanalyzer sample
    "property_value",          # (*) not in hmdaanalyzer sample
]

# Dataset filters per docs/methodology.md § "Dataset Filters"
_LOAN_TYPE_CONVENTIONAL = 1
_LIEN_STATUS_FIRST = 1
_OCCUPANCY_PRIMARY = 1
_PROPERTY_TYPE_1_4_UNIT = 1
_CONSTRUCTION_SITE_BUILT = 1
_ACTION_TAKEN_ORIGINATED = 1
_ACTION_TAKEN_DENIED = 3
_MAX_LTV = 100.0

# DTI bin definitions from The Markup (2021), consistent with HMDA categorical encoding.
_DTI_BINS = [0, 35, 42, 49, float("inf")]
_DTI_LABELS = ["dti_le35", "dti_36_42", "dti_43_49", "dti_ge50"]


def check_data_source(timeout: int = 15) -> dict:
    """
    Optional diagnostic: probe whether the CFPB HMDA Data Browser API is reachable.

    This is a standalone health check you can call before a long analysis run. As of
    v0.2.1 it is NO LONGER called by load_from_api() — a pre-flight health gate was
    causing every call to fail on cloud/datacenter IPs (the bare HEAD request drew an
    HTTP 403 from the CFPB/Akamai edge), so the gate was removed from the data path.

    The request now sends identifying headers (a non-default User-Agent, Accept, and
    Accept-Language) so it is not mistaken for an anonymous bot client.

    Returns:
        dict with keys: reachable (bool), status_code (int), url (str)

    Raises:
        DataSourceError if the endpoint is unreachable or returns an unexpected status.
    """
    from . import __version__ as _pkg_version

    headers = {
        "User-Agent": (
            f"fair-lending-screener/{_pkg_version} "
            "(+https://github.com/Jaypatel1511/fair-lending-screener)"
        ),
        "Accept": "text/csv, application/json;q=0.9, */*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        r = requests.head(
            CFPB_API_HEALTH_URL, timeout=timeout, allow_redirects=True, headers=headers
        )
        # 200/400/405 all mean the endpoint exists — 400 = needs parameters,
        # 405 = HEAD not allowed but the resource is there.
        if r.status_code in (200, 400, 405):
            return {"reachable": True, "status_code": r.status_code, "url": CFPB_API_HEALTH_URL}
        if r.status_code == 403:
            raise DataSourceError(
                CFPB_API_HEALTH_URL,
                "HTTP 403 Access Denied from the CFPB/Akamai edge. This is an edge/access "
                "block commonly returned to cloud/datacenter environments (e.g. Google "
                "Colab); it does NOT mean the CFPB API has moved or changed, and it is not "
                "a problem with your query. Retry from a residential network, or use "
                "load_from_file() with a manually downloaded CFPB modified-LAR CSV."
            )
        raise DataSourceError(
            CFPB_API_HEALTH_URL,
            f"Unexpected HTTP status {r.status_code}. CFPB API may have moved or changed."
        )
    except requests.RequestException as exc:
        raise DataSourceError(CFPB_API_HEALTH_URL, str(exc)) from exc


def load_from_api(
    year: int = 2023,
    state: Optional[str] = None,
    lei: Optional[str] = None,
    county: Optional[str] = None,
    limit: int = 50_000,
) -> pd.DataFrame:
    """
    Load HMDA LAR data from the CFPB Data Browser API.

    This is a thin wrapper around hmdaanalyzer.load_from_api() that:
    1. Delegates the fetch to hmdaanalyzer (>=0.3.1, which sends an identifying
       User-Agent so cloud/datacenter IPs are not 403'd by the CFPB/Akamai edge)
    2. Re-raises any hmdaanalyzer errors with context

    Note: there is intentionally NO pre-flight health check here. A bare HEAD probe
    (see check_data_source) draws an HTTP 403 from the edge on cloud IPs and would
    short-circuit every call before the data fetch ran. check_data_source remains
    available as an optional standalone diagnostic.

    Returns a raw DataFrame; call prepare_for_analysis() before running disparity analysis.

    Args:
        year:   HMDA data year (2018+ for expanded fields including LTV, DTI, property_value)
        state:  Two-letter state code, e.g. "IL"
        lei:    Lender LEI identifier
        county: County FIPS code
        limit:  Max records to fetch (default 50,000)

    Note:
        Data years before 2018 lack loan_to_value_ratio, debt_to_income_ratio, and
        property_value — controls required for the FFIEC-standard disparity model.
        Use 2018+ data for analysis with the full control set.
    """
    try:
        from hmdaanalyzer import load_from_api as _load
        df = _load(year=year, state=state, lei=lei, county=county, limit=limit)
        if df.empty:
            raise DataSourceError(CFPB_API_BASE, "API returned empty dataset.")
        return _normalize_columns(df)
    except DataSourceError:
        raise
    except Exception as exc:
        raise DataSourceError(CFPB_API_BASE, f"hmdaanalyzer.load_from_api failed: {exc}") from exc


def load_from_file(path: str) -> pd.DataFrame:
    """
    Load HMDA LAR data from a local CSV file (CFPB modified LAR format).

    Returns a raw DataFrame; call prepare_for_analysis() before running disparity analysis.
    """
    try:
        from hmdaanalyzer import load_from_file as _load
        df = _load(path)
        return _normalize_columns(df)
    except Exception as exc:
        raise DataSourceError(path, f"Failed to load file: {exc}") from exc


def load_sample(n: int = 2000, seed: int = 42) -> pd.DataFrame:
    """
    Load a synthetic HMDA-like sample dataset for testing and demonstration.

    WARNING: This dataset is synthetic. It is NOT real HMDA data and MUST NOT
    be used to draw conclusions about any lender or geography. It includes
    constructed racial disparities for testing purposes only.

    The sample includes all columns required for the full FFIEC control set,
    unlike hmdaanalyzer's load_sample() which omits LTV, DTI, and property_value.

    Note on pseudo-R² with synthetic data: MSA assignments are random, so MSA
    dummy variables carry no real geographic signal. This produces pseudo-R²
    values of 0.03–0.06 — far below the 0.15–0.25 expected on real HMDA data.
    This is expected; it reflects the absence of genuine geographic variation,
    not a problem with the model. See docs/methodology.md § "Pseudo-R²" for detail.

    Note on adjusted vs. unadjusted OR: On real HMDA, adjusted OR < unadjusted OR
    because income/LTV/DTI partially explain the raw disparity. On this synthetic
    sample, the generator makes race the primary driver, so controlling for mild
    income correlation can produce adjusted OR slightly above unadjusted OR.
    This is expected behavior on synthetic data.

    Args:
        n:    Number of records (default 2000; use ≥1000 for meaningful regression)
        seed: Random seed for reproducibility
    """
    rng = np.random.default_rng(seed)

    race_denial_rates = {
        "White": 0.095,
        "Black or African American": 0.195,
        "Asian": 0.090,
        "Hispanic or Latino": 0.145,
        "American Indian or Alaska Native": 0.175,
        "Native Hawaiian or Other Pacific Islander": 0.160,
    }
    races = list(race_denial_rates.keys())
    weights = [0.65, 0.13, 0.07, 0.10, 0.02, 0.03]

    msas = [f"MSA_{i:03d}" for i in range(1, 21)]

    records = []
    for _ in range(n):
        race = rng.choice(races, p=weights)
        denial_prob = race_denial_rates[race]

        income = float(max(25, rng.normal(85, 40)))
        loan_amount = float(max(50, income * rng.uniform(2.5, 5.5)))
        property_value = float(loan_amount * rng.uniform(1.05, 1.40))
        ltv = round(loan_amount / property_value * 100, 1)
        ltv = min(ltv, 97.0)

        dti_raw = float(rng.choice([22, 28, 32, 36, 38, 41, 44, 47, 51, 55, 62],
                                   p=[0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.08, 0.07]))

        action = 3 if rng.random() < denial_prob else 1

        records.append({
            "action_taken": action,
            "loan_type": 1,
            "loan_purpose": 1,
            "lien_status": 1,
            "occupancy_type": 1,
            "property_type": 1,
            "construction_method": 1,
            "derived_race": race,
            "derived_ethnicity": (
                "Hispanic or Latino" if race == "Hispanic or Latino"
                else "Not Hispanic or Latino"
            ),
            "applicant_income": round(income, 1),
            "loan_amount": round(loan_amount),
            "loan_to_value_ratio": ltv,
            "debt_to_income_ratio": dti_raw,
            "property_value": round(property_value),
            "msa_md": rng.choice(msas),
        })

    return pd.DataFrame(records)


def prepare_for_analysis(
    df: pd.DataFrame,
    loan_purpose: int = 1,
    validate_controls: bool = True,
) -> pd.DataFrame:
    """
    Apply FFIEC-standard dataset filters and prepare features for logistic regression.

    This function:
    1. Applies all dataset filters from docs/methodology.md § "Dataset Filters"
    2. Restricts to action_taken ∈ {1, 3} (originated or denied)
    3. Creates the is_denied outcome variable
    4. Log-transforms continuous controls (income, loan_amount, property_value)
    5. Bins debt_to_income_ratio into 4 FFIEC-standard categories
    6. Returns a clean DataFrame ready for adjusted_denial_disparity()

    Args:
        df:                 Raw HMDA DataFrame (from load_from_api, load_from_file, or load_sample)
        loan_purpose:       Filter to this loan purpose code (default 1 = home purchase).
                            Pass None to skip this filter (not recommended without adding
                            loan_purpose as a regression control).
        validate_controls:  If True, warn when FFIEC-standard controls are missing.

    Returns:
        Filtered DataFrame with derived columns added. Original columns preserved.

    Raises:
        MissingControlsError: if action_taken or derived_race are absent.
        ValueError: if the DataFrame is empty after filtering.
    """
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]

    # Normalize income column name (hmdaanalyzer uses "income", HMDA API uses "applicant_income")
    if "income" in df.columns and "applicant_income" not in df.columns:
        df = df.rename(columns={"income": "applicant_income"})

    # Validate required columns
    missing_required = _REQUIRED_COLUMNS - set(df.columns)
    if missing_required:
        raise MissingControlsError(
            missing_columns=sorted(missing_required),
            available_columns=sorted(df.columns.tolist()),
        )

    # Warn on missing FFIEC controls (don't raise — callers can still run with fewer controls)
    if validate_controls:
        missing_controls = [c for c in STANDARD_CONTROLS if c not in df.columns]
        if missing_controls:
            warnings.warn(
                f"FFIEC-standard control column(s) not found: {missing_controls}. "
                f"These will be omitted from the model. Results will be less complete. "
                f"Use real HMDA data (2018+) from load_from_api() for the full control set.",
                UserWarning,
                stacklevel=2,
            )

    # ── Coerce types ──────────────────────────────────────────────────────────
    for col in ["action_taken", "loan_type", "loan_purpose", "lien_status",
                "occupancy_type", "property_type", "construction_method"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["applicant_income", "loan_amount", "loan_to_value_ratio",
                "debt_to_income_ratio", "property_value"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Dataset filters per docs/methodology.md ───────────────────────────────
    # Filter 1: clear credit decisions only (FFIEC: "originated or denied")
    df = df[df["action_taken"].isin([_ACTION_TAKEN_ORIGINATED, _ACTION_TAKEN_DENIED])]

    # Filter 2: conventional loans only
    if "loan_type" in df.columns:
        df = df[df["loan_type"] == _LOAN_TYPE_CONVENTIONAL]

    # Filter 3: loan purpose (default: home purchase only)
    if loan_purpose is not None and "loan_purpose" in df.columns:
        df = df[df["loan_purpose"] == loan_purpose]

    # Filter 4: first-lien only
    if "lien_status" in df.columns:
        df = df[df["lien_status"] == _LIEN_STATUS_FIRST]

    # Filter 5: principal residence only
    if "occupancy_type" in df.columns:
        df = df[df["occupancy_type"] == _OCCUPANCY_PRIMARY]

    # Filter 6: one-to-four unit properties only
    if "property_type" in df.columns:
        df = df[df["property_type"] == _PROPERTY_TYPE_1_4_UNIT]

    # Filter 7: site-built only (exclude manufactured housing)
    if "construction_method" in df.columns:
        df = df[df["construction_method"] == _CONSTRUCTION_SITE_BUILT]

    # Filter 8: LTV ≤ 100% and not missing (CLTV > 100% is economically implausible)
    if "loan_to_value_ratio" in df.columns:
        df = df[df["loan_to_value_ratio"].notna() & (df["loan_to_value_ratio"] <= _MAX_LTV)]

    # Filter 9: exclude business/commercial purpose (The Markup spec, Filter 9)
    # HMDA code 1 = primarily for business/commercial purpose; code 2 = not for business/commercial.
    # Exempt reporters use code 1111; NaN results from coercion of Exempt or missing values.
    # Policy: only include rows explicitly coded 2 (not for business). NaN and Exempt (1111)
    # are excluded to err on the side of analyzing only clearly consumer-purpose loans.
    if "business_or_commercial_purpose" in df.columns:
        df["business_or_commercial_purpose"] = pd.to_numeric(
            df["business_or_commercial_purpose"], errors="coerce"
        )
        df = df[df["business_or_commercial_purpose"] == 2]
    elif validate_controls:
        warnings.warn(
            "'business_or_commercial_purpose' column not found in DataFrame. "
            "Filter 9 (exclude business-purpose loans per The Markup spec) could not be applied. "
            "Results may include business-purpose loans. "
            "Use real HMDA data (2018+) from load_from_api() for the full filter set.",
            UserWarning,
            stacklevel=2,
        )

    if df.empty:
        raise ValueError(
            "DataFrame is empty after applying FFIEC dataset filters. "
            "Check that the input data contains conventional first-lien home purchase loans "
            "with action_taken ∈ {1, 3}."
        )

    df = df.reset_index(drop=True)

    # ── Derived outcome variable ──────────────────────────────────────────────
    df["is_denied"] = (df["action_taken"] == _ACTION_TAKEN_DENIED).astype(int)

    # ── Log-transform continuous controls ─────────────────────────────────────
    # Wooldridge (2019) § 6.2: log transformation appropriate for right-skewed
    # financial variables; +1 prevents log(0) for zero-income edge cases.
    if "applicant_income" in df.columns:
        df["log_income"] = np.log1p(df["applicant_income"].clip(lower=0))

    if "loan_amount" in df.columns:
        df["log_loan_amount"] = np.log(df["loan_amount"].clip(lower=1))

    if "property_value" in df.columns:
        df["log_property_value"] = np.log1p(df["property_value"].clip(lower=0))

    # ── DTI binning ───────────────────────────────────────────────────────────
    # The Markup (2021) used four bins; HMDA 12 C.F.R. § 1003.4(a)(23) encodes
    # DTI in mixed format (numeric % or category string). We normalize to numeric,
    # extract midpoints from range strings, then bin.
    if "debt_to_income_ratio" in df.columns:
        df["dti_numeric"] = _parse_dti(df["debt_to_income_ratio"])
        df["dti_bin"] = pd.cut(
            df["dti_numeric"],
            bins=_DTI_BINS,
            labels=_DTI_LABELS,
            right=True,
            include_lowest=True,
        )
        df["dti_bin"] = df["dti_bin"].astype(object).fillna("dti_missing")

    return df


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase column names and normalize income field name."""
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]
    if "income" in df.columns and "applicant_income" not in df.columns:
        df = df.rename(columns={"income": "applicant_income"})
    return df


def _parse_dti(series: pd.Series) -> pd.Series:
    """
    Parse HMDA's mixed DTI encoding into numeric values.

    HMDA lenders report DTI as either:
    - A numeric percentage string: "27", "35.5"
    - A range string: "20%-<30%", "30%-<36%", "36%-<50%", ">60%", "<20%", "50%-60%"

    For range strings, we take the midpoint of the range.
    Returns a float Series; unparseable values become NaN (binned to dti_missing).
    """
    _range_midpoints = {
        "<20%": 17.5,
        "20%-<30%": 25.0,
        "30%-<36%": 33.0,
        "36%-<50%": 43.0,
        "50%-60%": 55.0,
        ">60%": 65.0,
        "exempt": float("nan"),
        "na": float("nan"),
    }

    def _parse_one(val):
        if pd.isna(val):
            return float("nan")
        s = str(val).strip().lower()
        if s in _range_midpoints:
            return _range_midpoints[s]
        # Strip trailing % and try numeric
        s_clean = s.rstrip("%")
        try:
            return float(s_clean)
        except ValueError:
            return float("nan")

    return series.apply(_parse_one)
