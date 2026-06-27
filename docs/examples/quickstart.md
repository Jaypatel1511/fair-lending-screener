# Quickstart Guide

## Installation

```bash
pip install fair-lending-screener
```

## Basic Analysis (Real HMDA Data)

```python
import warnings
import fair_lending_screener as fls

# Step 1: Load HMDA data from the CFPB public API
# Use 2018+ for the full control set (LTV, DTI, property_value)
df_raw = fls.load_from_api(year=2023, state="IL", limit=20_000)
print(f"Loaded {len(df_raw):,} records")

# Step 2: Apply FFIEC-standard dataset filters and prepare features
# Filters: conventional, first-lien, home purchase, site-built 1-4 unit,
#          principal residence, LTV ≤ 100%
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    df = fls.prepare_for_analysis(df_raw)
print(f"After filters: {len(df):,} records")

# Step 3: Run the analysis
result = fls.adjusted_denial_disparity(
    df,
    protected_class="Black or African American",
    comparison_class="White",
    data_year=2023,  # required; recorded in the provenance dict
)

# Step 4: Read the results
print(f"\nUnadjusted denial rate disparity:  {result.unadjusted_odds_ratio:.2f}×")
print(f"Adjusted denial rate disparity:    {result.adjusted_odds_ratio:.2f}×")
print(f"95% Confidence interval:           {result.confidence_interval_95[0]:.2f}–{result.confidence_interval_95[1]:.2f}×")
print(f"P-value:                           {result.p_value:.4f}")
print(f"Statistically significant:         {result.is_statistically_significant}")
print(f"Sample size:                       {result.sample_size:,}")
print(f"\nControls used: {result.controls_used}")

# Step 5: Generate a report
report = fls.generate_disparity_report(result, geography="Illinois", year=2023)
print(report)
```

## Analyze a Specific Lender

```python
# Pass an LEI to analyze a specific lender
# Find LEIs at https://ffiec.cfpb.gov/data-browser/
df_raw = fls.load_from_api(year=2023, lei="YOUR_LENDER_LEI", limit=50_000)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    df = fls.prepare_for_analysis(df_raw)

result = fls.adjusted_denial_disparity(df, data_year=2023)
report = fls.generate_disparity_report(result, lender_name="Lender Name", year=2023)
print(report)
```

## Error Handling

```python
from fair_lending_screener import (
    adjusted_denial_disparity,
    InsufficientDataError,
    InvalidProtectedClassError,
    ModelConvergenceError,
)

try:
    result = adjusted_denial_disparity(df, protected_class="Black or African American", data_year=2023)
except InsufficientDataError as e:
    print(f"Not enough data: {e.actual} observations (need {e.minimum})")
except InvalidProtectedClassError as e:
    print(f"Class not found: {e.requested}. Valid values: {e.valid_values}")
except ModelConvergenceError as e:
    print(f"Model failed to converge: {e}")
```

## Understanding What the Numbers Mean

An adjusted odds ratio of **1.8×** means:

> Among applicants who appear similarly situated on paper — same income, same loan-to-value ratio, same debt-to-income category, same property value, and same metropolitan area — Black applicants faced **80% higher odds of denial** than White applicants.

This is a statistical screening finding. It does not mean the lender discriminated. It means the disparity warrants further review with full loan-file data. See `docs/limitations.md` for what public HMDA cannot tell you.
