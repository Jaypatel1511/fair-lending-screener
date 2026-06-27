# fair-lending-screener

[![PyPI version](https://badge.fury.io/py/fair-lending-screener.svg)](https://pypi.org/project/fair-lending-screener/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/Jaypatel1511/fair-lending-screener/actions/workflows/test.yml/badge.svg)](https://github.com/Jaypatel1511/fair-lending-screener/actions/workflows/test.yml)

**Statistical disparate impact analysis for HMDA mortgage data — the methodology federal examiners use, open-sourced for community advocates and investigative journalists.**

---

## What This Tool Does / Does Not Do

**DOES:**
- Run adjusted denial disparity analysis on public HMDA mortgage data
- Use binary logistic regression with FFIEC-standard controls (income, LTV, DTI, property value, MSA)
- Report adjusted odds ratios with 95% confidence intervals and p-values
- Generate journalist-legible Markdown reports explaining what was found and what it means
- Cite the regulatory methodology (FFIEC Interagency Fair Lending Examination Procedures, 2009)
- Tell you clearly what it cannot conclude

**DOES NOT:**
- Prove discrimination — it identifies statistical screening signals warranting further review
- Include credit score, AUS recommendations, or asset data (not in public HMDA)
- Analyze Section 1071 small business lending (different statute, different data)
- Replace a full fair lending examination by federal regulators with access to internal lender data
- Use black-box ML — every result is an auditable logistic regression you can reproduce

> **Alpha release (v0.1.0).** Methodology peer review by an external fair lending expert is planned before v1.0.0. Use as a screening tool to identify cases warranting further analysis, not as a basis for enforcement or accusation.

---

## Why It Exists

Community advocates, investigative journalists, and fair housing nonprofits routinely need to answer the question: *"Are these denial rate disparities statistically suspicious after controlling for income, loan size, and geography?"*

Currently that analysis requires either:
- **$50K+ commercial software** (ComplianceTech, RiskExec, RATA Comply, Abrigo) — out of reach for nonprofits
- **Stata fluency** — out of reach for most journalists
- **Months of methodology work** — The Markup spent months building their 2021 analysis

This package makes that analysis installable in 30 seconds.

---

## Limitations — Read This First

**Public HMDA data does not include:**

1. **Credit score** — The most predictive underwriting variable, excluded from public HMDA by industry lobbying. Its absence means results are upper-bound estimates of the unexplained disparity.
2. **AUS recommendations** — Fannie/Freddie DU/LP decisions, the primary underwriting tool, are not public.
3. **Asset and reserve data** — Not reported in HMDA.
4. **Employment history** — Not reported in HMDA.
5. **Underwriter override data** — Discretionary overrides are internal lender data.

A statistically significant adjusted disparity does not mean the lender discriminated. It means the disparity warrants further review with full loan-file data. See [`docs/limitations.md`](docs/limitations.md) for the complete list.

---

## Installation

```bash
pip install fair-lending-screener
```

Both import styles work:

```python
import fair_lending_screener
import fairlendingscreener  # alias — identical
```

---

## Quickstart

```python
import warnings
import fair_lending_screener as fls

# Load HMDA data from the CFPB public API (real data; requires internet)
df_raw = fls.load_from_api(year=2023, state="IL", limit=20_000)

# Apply FFIEC-standard dataset filters:
# conventional, first-lien, home purchase, site-built 1-4 unit,
# principal residence, LTV ≤ 100%
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    df = fls.prepare_for_analysis(df_raw)

# Run adjusted denial disparity analysis:
# logistic regression with income, LTV, DTI, property value, MSA controls
result = fls.adjusted_denial_disparity(
    df,
    protected_class="Black or African American",
    comparison_class="White",
    data_year=2023,  # required; recorded in the provenance dict
)

# Key numbers
print(f"Unadjusted odds ratio:    {result.unadjusted_odds_ratio:.2f}×")
print(f"Adjusted odds ratio:      {result.adjusted_odds_ratio:.2f}×")
print(f"95% CI:                   {result.confidence_interval_95[0]:.2f}–{result.confidence_interval_95[1]:.2f}×")
print(f"p-value:                  {result.p_value:.4f}")
print(f"Statistically significant: {result.is_statistically_significant}")
print(f"Sample size:              {result.sample_size:,}")

# Generate a journalist-legible Markdown report
report = fls.generate_disparity_report(
    result,
    lender_name="First Midwest Bank",  # optional — suppressed if result is not statistically significant
    geography="Illinois",
    year=2023,
)
print(report)
```

### Using Synthetic Sample Data (no internet required)

```python
import warnings
import fair_lending_screener as fls

# Synthetic data for testing — NOT real HMDA, NOT for conclusions
raw = fls.load_sample(n=2000, seed=42)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    df = fls.prepare_for_analysis(raw)

result = fls.adjusted_denial_disparity(
    df,
    protected_class="Black or African American",
    comparison_class="White",
    data_year=2023,  # required; recorded in the provenance dict
)
print(f"Adjusted OR: {result.adjusted_odds_ratio:.2f}×, p={result.p_value:.4f}")
```

---

## Understanding the Output

### Unadjusted vs. Adjusted Odds Ratio

- **Unadjusted:** Raw denial rate disparity — no controls for income, loan size, or geography
- **Adjusted:** Disparity after statistically holding constant income (log), loan amount (log), LTV, DTI, property value (log), and MSA fixed effects

An adjusted odds ratio of 1.8× means: *among applicants who look similar on paper — same income, loan size, LTV, property value, and MSA — Black applicants faced 80% higher odds of denial than White applicants.*

The difference between the two ratios shows how much of the raw disparity is explained by the available controls.

### What "Statistically Significant" Means

A result is flagged as statistically significant when:
- **p-value < 0.05** (the disparity is unlikely to be due to chance)
- **95% CI excludes 1.0** (the direction of the disparity is reliable)

Both conditions must hold. A large odds ratio with p = 0.08 is not reported as significant.

### What Controls Are Used

Per FFIEC Interagency Fair Lending Examination Procedures (2009):

| Control | Notes |
|---|---|
| `log(applicant_income)` | Ability-to-repay; log-transformed for skew |
| `log(loan_amount)` | Loan size |
| `loan_to_value_ratio` | Collateral coverage |
| `debt_to_income_ratio` | Binned: ≤35%, 36–42%, 43–49%, ≥50%, missing |
| `log(property_value)` | Collateral value |
| MSA fixed effects | ~300–400 dummies for local market conditions |

---

## How This Compares to Commercial Tools

| | fair-lending-screener | Commercial tools (ComplianceTech, RATA Comply, etc.) |
|---|---|---|
| **Cost** | Free, open-source | $20K–$100K+/year |
| **Data** | Public HMDA only | Internal lender data + HMDA |
| **Credit score** | Not available (public HMDA) | Available via lender data feed |
| **AUS data** | Not available | Available |
| **Methodology** | Published, citable, auditable | Proprietary |
| **Target user** | Advocates, journalists, researchers | Lender compliance teams |
| **Intended use** | Screening signals for advocacy/research | Regulatory compliance management |

---

## Methodology

Full methodology documentation is in [`docs/methodology.md`](docs/methodology.md). Every statistical decision cites a regulatory or academic source.

**Short version:**

- Binary logistic regression (`statsmodels.api.Logit`) — not sklearn, not ML
- Outcome: `action_taken == 3` (denied) vs. `action_taken == 1` (originated)
- Protected class: `derived_race` (self-reported per Regulation C)
- Controls: FFIEC standard set (income, LTV, DTI, property value, MSA)
- Dataset filters: conventional, first-lien, home purchase, site-built 1–4 unit, owner-occupied, LTV ≤ 100%
- Calibration target: The Markup (2021) found 1.8× adjusted OR for Black vs. White applicants nationally. Expected range from this tool: 1.6–2.2× (above The Markup's figure because we omit AUS and credit score — known upward-bias direction per Wooldridge 2019 §3.3)

**Regulatory basis:** FFIEC Interagency Fair Lending Examination Procedures (2009). This is the methodology OCC, Federal Reserve, FDIC, NCUA, and CFPB examiners use.

---

## Coming in Future Versions

**v0.2.0 (planned):**
- Extended control set: AUS, credit model used, lender type, census tract demographics — toward full replication of The Markup's 17-variable specification
- Pricing disparity analysis (linear regression on rate spread or APR)

**v0.3.0+:**
- BISG race/ethnicity proxy for non-HMDA products (auto, student)
- Redlining geographic analysis (census-tract lender presence)
- Peer benchmarking (lender vs. market comparison)
- Multilevel/hierarchical MSA modeling

---

## Scope

Mortgage lending (HMDA-reportable transactions) only.
- Does **NOT** analyze Section 1071 small business lending
- Does **NOT** include credit score (not in public HMDA)
- Does **NOT** constitute a finding of discrimination
- **DOES** identify statistically significant adjusted disparities warranting further review

---

## Methodology Feedback

Open a GitHub issue tagged [`methodology`](https://github.com/Jaypatel1511/fair-lending-screener/issues) with specific concerns and citations. All methodology changes are versioned and documented in [`CHANGELOG.md`](CHANGELOG.md).

---

## Citation

If you use this tool in research or journalism, please cite it:

```
Patel, Jay (2026). fair-lending-screener (v0.1.0). MIT License.
https://github.com/Jaypatel1511/fair-lending-screener
```

See [`CITATION.cff`](CITATION.cff) for full citation metadata.

---

## License

MIT License. See [`LICENSE`](LICENSE).
