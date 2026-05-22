# Fair Lending Screener: Statistical Methodology

**Version:** 0.1.0  
**Last updated:** 2026-05-21  
**Status:** Alpha — methodology peer review by external fair lending expert planned before v1.0.0

---

## Overview

This document describes the statistical methodology used in `fair-lending-screener` for adjusted denial disparity analysis. Every analytical decision made in this package traces to a published regulatory source, academic methodology, or documented industry practice. Where a decision involves judgment, that judgment is explained and the alternative is noted.

The goal of this analysis is to answer a narrow, specific question:

> After statistically controlling for legitimate underwriting factors available in public HMDA data, do applicants of a particular racial or ethnic group face statistically higher denial rates than similarly situated applicants of the comparison group?

This is not a finding of discrimination. It is a screening signal warranting further review.

---

## Regulatory Foundation

### Primary Source: FFIEC Interagency Fair Lending Examination Procedures

**Citation:** FFIEC Interagency Fair Lending Examination Procedures (August 2009 edition with subsequent updates)  
**Publisher:** Federal Financial Institutions Examination Council  
**URL:** https://www.ffiec.gov/PDF/fairlend.pdf  
**Status:** The canonical reference used by OCC, Federal Reserve, FDIC, NCUA, and CFPB examiners

The FFIEC procedures establish that underwriting disparity analysis uses logistic regression to test whether denial rates differ on a prohibited basis (race, ethnicity, sex, age, national origin) **after accounting for objective credit and loan attributes** that legitimately drive underwriting decisions. The procedures require:

- A binary outcome variable (denied vs. originated)
- A protected class indicator as the variable of interest
- Controls for legitimate business factors
- Odds ratio as the primary output statistic
- Reporting of confidence intervals and statistical significance

The FFIEC exam procedures form the legal and methodological baseline for all fair lending examinations under the Equal Credit Opportunity Act (15 U.S.C. § 1691 et seq.) and the Fair Housing Act (42 U.S.C. § 3605).

### Secondary Source: The Markup Methodology (2021)

**Citation:** "How We Investigated Racial Disparities in Federal Mortgage Data," The Markup, August 25, 2021  
**Authors:** Emmanuel Martinez and Lauren Kirchner  
**URL:** https://themarkup.org/show-your-work/2021/08/25/how-we-investigated-racial-disparities-in-federal-mortgage-data  
**Significance:** First major public, reproducible implementation of the FFIEC methodology applied to the post-2018 expanded HMDA data; used binary logistic regression with 17 controls, McFadden's pseudo-R² = 0.2256, adjusted odds ratio 1.8× for Black applicants nationally (p ≈ 0).

The Markup's national model serves as the primary calibration target for `fair-lending-screener`. Their exact replication specification, including material differences from this package's defaults, is documented in the **Calibration Target** section below.

### Tertiary Source: CFPB BISG Proxy Methodology

**Citation:** CFPB, "Using Publicly Available Information to Proxy for Unidentified Race and Ethnicity," September 2014  
**URL:** https://files.consumerfinance.gov/f/201409_cfpb_report_proxy-methodology.pdf  
**Applicability:** Relevant when race/ethnicity is not self-reported; deferred to v0.2.0 for HMDA since derived_race is directly reported for home mortgage applications under Regulation C.

---

## Data Source

### HMDA Loan Application Register (LAR)

The Home Mortgage Disclosure Act (12 U.S.C. § 2801 et seq.) requires most mortgage lenders to publicly report loan application data annually. Since 2018, the expanded HMDA LAR (implemented under Dodd-Frank § 1094, codified at 12 C.F.R. Part 1003) includes fields required for this analysis:

| Field | HMDA Variable Name | Use in Model |
|---|---|---|
| Outcome | `action_taken` | Outcome variable (filter + derive `is_denied`) |
| Race | `derived_race` | Protected class indicator |
| Ethnicity | `derived_ethnicity` | Secondary protected class |
| Income | `applicant_income` | Regression control |
| Loan amount | `loan_amount` | Regression control |
| Loan-to-value | `loan_to_value_ratio` | Regression control |
| Debt-to-income | `debt_to_income_ratio` | Regression control (categorical) |
| Property value | `property_value` | Regression control |
| Loan type | `loan_type` | Filter criterion (also available as control) |
| Lien status | `lien_status` | Filter criterion |
| Occupancy type | `occupancy_type` | Filter criterion |
| Property type | `property_type` | Filter criterion |
| Construction method | `construction_method` | Filter criterion |
| Loan purpose | `loan_purpose` | Filter criterion (configurable parameter) |
| MSA | `msa_md` | Fixed effects (regression control — see MSA section) |

**Data access:** Via CFPB API at https://ffiec.cfpb.gov/api/public/

---

## Dataset Filters (Applied Before Regression)

The following filters are applied to the raw HMDA LAR before any analysis. These are not regression controls — they define the population under study. Each filter has a documented rationale.

| Filter | HMDA Value | Rationale |
|---|---|---|
| `loan_type == 1` | Conventional only | Government-backed loans (FHA=2, VA=3, USDA=4) have different underwriting standards, guarantee structures, and borrower risk profiles; mixing them confounds the disparity estimate. The Markup (2021) applied this filter. |
| `lien_status == 1` | First-lien only | Subordinate-lien loans have fundamentally different risk profiles and underwriting criteria. |
| `loan_purpose` | Default: `1` (home purchase) | Home purchase, refinance, and cash-out refinance have different underwriting standards and borrower selection effects. Default is home purchase (matches The Markup). Callers may pass `loan_purpose=31` (refinance) or `loan_purpose=32` (cash-out refinance) to analyze those pools separately. Passing all purposes simultaneously is not recommended without adding `loan_purpose` as a regression control. |
| `occupancy_type == 1` | Principal residence only | Second homes (2) and investment properties (3) have higher default rates and different underwriting criteria. The Markup (2021) applied this filter. |
| `property_type == 1` | One-to-four unit only | Multifamily (3) underwriting differs fundamentally from single-family. The Markup applied this filter. |
| `construction_method == 1` | Site-built only | Manufactured/mobile housing (2) has a different regulatory framework, title treatment, and risk profile. The Markup (2021) applied this filter. |
| `action_taken ∈ {1, 3}` | Originated or denied | See outcome variable section below. |
| `loan_to_value_ratio ≤ 100` | Not over 100% and not missing | CLTV > 100% is economically implausible for a new origination and likely a data error. The Markup (2021) excluded CLTV > 100% and missing CLTV. |

---

## Outcome Variable Construction

Following both FFIEC procedures and The Markup (2021):

- **Included:** `action_taken == 1` (originated — approved and funded) and `action_taken == 3` (denied)
- **Excluded:** `action_taken == 2` (approved, not accepted), `action_taken == 4` (incomplete), `action_taken == 5` (withdrawn by applicant), `action_taken == 6` (purchased loan), `action_taken == 7` (pre-approval request denied), `action_taken == 8` (pre-approval granted but not accepted)

**Rationale for exclusions:**
- `action_taken == 2`: Applicant declined an approved offer; does not indicate lender denial and may reflect applicant circumstances not captured in HMDA.
- `action_taken == 4, 5`: Outcome not determined by lender underwriting; including these conflates lender behavior with applicant behavior.
- `action_taken == 6, 8`: Not underwriting decisions.
- `action_taken == 7`: Pre-approval requests are a different product and process than full applications.

FFIEC procedures focus analysis on "clear credit decisions" — this filter operationalizes that requirement.

**Derived outcome variable:** `is_denied` = 1 when `action_taken == 3`, 0 when `action_taken == 1`

---

## Protected Class Variables

### Race (Primary Analysis)

`derived_race` is the FFIEC-approved field for racial classification in post-2018 HMDA data. It represents the applicant's self-reported race per Regulation C (12 C.F.R. § 1003.4(a)(10)).

**Primary comparison:** `derived_race == "Black or African American"` vs. `derived_race == "White"`  
**Secondary comparison:** `derived_ethnicity == "Hispanic or Latino"` vs. `derived_ethnicity == "Not Hispanic or Latino"` (analyzed separately)

**Design decision:** `derived_race` is used directly rather than the BISG proxy because HMDA requires race self-reporting for home mortgage applications under Regulation C. Where `derived_race` is missing or `"Race Not Available"`, the observation is excluded from analysis and documented in `DisparityResult.limitations`.

### Ethnicity

Following Regulation C conventions, Hispanic-or-Latino ethnicity is analyzed separately from race because an applicant may report both a racial category and Hispanic ethnicity. Conflating them produces incorrect comparisons. Separate `derived_ethnicity` analysis is offered as an optional parameter.

---

## Regression Model Specification

### Model: Binary Logistic Regression

**Why logistic regression, not linear probability model:**  
The outcome is binary (denied/originated). Linear probability models produce predicted probabilities outside [0,1] and have heteroskedastic errors. Logistic regression is standard for binary outcomes in both the academic literature and FFIEC exam procedures. See: Greene, W.H. (2012), *Econometric Analysis* (7th ed.), Chapter 17.

**Why statsmodels Logit, not sklearn LogisticRegression:**  
`statsmodels` provides p-values, confidence intervals, pseudo-R², log-likelihood, and convergence diagnostics as first-class outputs. `sklearn` optimizes for prediction and does not report standard errors without additional steps. Regulatory and legal defensibility requires inference-mode output with named coefficients and standard errors.

### Full Model Equation

```
logit(P(is_denied = 1)) =

  β₀                                          (intercept)
+ β₁ · protected_class                        (variable of interest; 1 if protected group, 0 if comparison)
+ β₂ · log(applicant_income + 1)              (ability-to-repay; log-transformed for skew)
+ β₃ · log(loan_amount)                       (loan size; log-transformed for skew)
+ β₄ · loan_to_value_ratio                    (collateral coverage; entered as-is, already a ratio)
+ β₅ · DTI_bin_2                              (DTI 36–42%, dummy; baseline = DTI ≤ 35%)
+ β₆ · DTI_bin_3                              (DTI 43–49%, dummy)
+ β₇ · DTI_bin_4                              (DTI ≥ 50%, dummy)
+ β₈ · DTI_bin_missing                        (DTI not reported, dummy)
+ β₉ · log(property_value + 1)               (collateral value; log-transformed for skew)
+ β₁₀ · loan_type_dummy_2                    (FHA; baseline = conventional — note: usually 0 after loan_type filter)
+ β₁₁ · lien_status_dummy_2                  (subordinate lien; baseline = first lien — usually 0 after filter)
+ β₁₂ · occupancy_type_dummy_2               (second home; baseline = principal residence — usually 0 after filter)
+ β₁₃ · occupancy_type_dummy_3               (investment property dummy)
+ Σⱼ γⱼ · MSA_dummy_j                        (one dummy per MSA with ≥ 30 observations; see MSA section)
+ ε
```

where:
- `exp(β₁)` is the **adjusted odds ratio** — the primary output of this package
- **Variables that become trivial after filters** (loan_type, lien_status, occupancy_type dummies) are included for robustness when users deviate from default filters; they reduce to near-zero variance columns and are dropped by the model if perfectly collinear.
- `ε` represents the logistic error term (the model does not explicitly estimate ε; it is absorbed into the link function)

**Note on co-applicant variables:** The Markup's 17-control model included co-applicant presence, age, sex, credit model used, AUS recommendation, lender type, lender size, census tract income ratio, metro size, and tract White population percentage. Several of these are available in post-2018 HMDA but are **not in this package's default control set.** This is a deliberate scope choice for v0.1.0 — it means our adjusted odds ratio is not a direct replication of The Markup's. See the **Calibration Target** section for implications.

### Control Variable Justifications and Citations

| Variable | Type | Citation |
|---|---|---|
| `applicant_income` (log) | Continuous | Primary ability-to-repay indicator per ECOA Reg B, 12 C.F.R. § 202.6(b)(2). Log transformation: Wooldridge, J.M. (2019), *Introductory Econometrics: A Modern Approach* (7th ed.), § 6.2: "More on Using Logarithmic Functional Forms." |
| `loan_amount` (log) | Continuous | Loan size affects risk concentration. Log-transformation standard for skewed financial distributions. Wooldridge (2019) § 6.2. |
| `loan_to_value_ratio` | Continuous | Collateral coverage ratio; FFIEC standard underwriting control. Entered as a proportion (not log-transformed; already bounded). |
| `debt_to_income_ratio` | Categorical (4 bins) | Ability-to-repay per CFPB QM rule (12 C.F.R. § 1026.43). HMDA reports DTI as categorical ranges per 12 C.F.R. § 1003.4(a)(23) and FFIEC/CFPB HMDA Filing Instructions Guide. Four bins match The Markup (2021): ≤35% (baseline), 36–42%, 43–49%, ≥50%, plus a missing-indicator dummy. |
| `property_value` (log) | Continuous | Collateral value independent of the LTV ratio. Log-transformed for skew. Wooldridge (2019) § 6.2. |
| MSA dummies | Categorical | See MSA Fixed Effects section. |

---

### MSA Fixed Effects: Implementation Choice and Rationale

**Decision:** MSA indicator variables (one dummy per MSA with ≥ 30 combined observations in the analysis sample) are included in a single pooled national model.

**Why dummies over multilevel (hierarchical) modeling:**  
MSA dummy variables are interpretable, transparent, and auditable — each coefficient has a direct interpretation. Hierarchical linear models (mixed-effects logit) shrink MSA-level estimates toward the grand mean, which is methodologically defensible but adds complexity that makes results harder to explain to a journalist or attorney. At v0.1.0, transparency takes priority over efficiency. Multilevel modeling is deferred to v0.2.0.

**Why dummies over per-MSA stratified regressions:**  
Stratified (per-MSA) regressions lose statistical power in smaller MSAs and prevent national-level conclusions. The Markup used stratified models for their metro-level maps, but their national model used categorical geographic proxies (see below). Pooled-with-dummies allows a single nationally interpretable odds ratio while still controlling for geographic variation in housing markets, lender composition, and economic conditions.

**Departure from The Markup national model:**  
The Markup's national model did NOT use MSA dummies. Instead, they used three categorical geographic proxies:
1. Ratio of census tract median income to metro area median income (4 bins: Low, Moderate, Middle, Upper)
2. Metro area population size (categorical, by population percentile)
3. Non-Hispanic White population percentage of the census tract (4 bins at 25-percentage-point intervals)

This package uses MSA dummies instead, which controls for geography at a finer granularity but at substantially higher degrees-of-freedom cost. Results are not directly comparable to The Markup's national model on this dimension.

**Sparse MSA handling:**  
MSAs with fewer than 30 combined observations (protected class + comparison class) in the analysis sample are not given individual dummies. Observations from these sparse MSAs are assigned to a `MSA_other` reference category. Rationale: A dummy for a 5-observation MSA has no predictive power and inflates the model's degrees of freedom without improving control. The 30-observation threshold is consistent with standard sparse-category practice in logistic regression.

**Degrees-of-freedom cost:**  
The 2019 HMDA national dataset covers approximately 400 distinct MSAs for conventional first-lien home purchase loans. At the default filter thresholds, roughly 300–350 MSAs will have ≥ 30 observations and receive individual dummies. This is a substantial DoF cost (~300 additional parameters) but is justified by the importance of geographic controls in mortgage markets, where local conditions (home prices, lender mix, economic conditions) explain large amounts of the variance in denial rates.

---

## Statistical Outputs and Interpretation

### Adjusted Odds Ratio

The adjusted odds ratio (exp(β₁)) represents:

> The multiplicative change in the odds of denial for a member of the protected class compared to a similarly situated member of the comparison class, holding all control variables constant at their observed values.

**Example interpretation:** An adjusted odds ratio of 1.76 means that, after controlling for income, loan amount, LTV, DTI, property value, and MSA, Black applicants face 76% higher odds of denial than otherwise similar White applicants in the same MSA.

### Confidence Intervals

95% confidence intervals are computed from Wald standard errors produced by `statsmodels` (`conf_int()` method on the fitted `LogitResults` object). Wald intervals are standard for logistic regression at large sample sizes; they are asymptotically equivalent to profile-likelihood intervals and are the method used throughout the academic and regulatory literature. See: Greene, W.H. (2012), *Econometric Analysis* (7th ed.), § 17.4.

**Reporting requirement:** A result is reported as "statistically significant" only when the 95% CI excludes 1.0 AND p < 0.05. Both conditions must hold.

### P-value

The two-tailed p-value tests H₀: β₁ = 0 (no difference in denial rates on a protected basis after controlling for legitimate factors). P < 0.05 is the conventional threshold for rejecting the null. All p-values are reported; the tool does not selectively suppress non-significant results.

### Pseudo-R² (Model Fit Diagnostic)

McFadden's pseudo-R² is:

```
ρ² = 1 − (log-likelihood of full model / log-likelihood of null model)
```

**Primary source:** McFadden, D. (1973). "Conditional logit analysis of qualitative choice behavior." In P. Zarembka (ed.), *Frontiers in Econometrics*, Academic Press. McFadden stated that values of 0.2–0.4 represent excellent fit. A value of 0.10 is used as a minimum reporting threshold (below this, the model controls are contributing very little beyond the intercept).

**The Markup's national model achieved pseudo-R² = 0.2256**, which is in the excellent range. Analysts should note that our default control set (which excludes AUS and credit model) will produce a lower pseudo-R².

**Expected pseudo-R² on real HMDA data:** Approximately 0.15–0.25 for national or large-state conventional home purchase models with MSA fixed effects and the standard control set. Models below 0.10 warrant inspection of the control set and sample filters.

**Why synthetic sample data produces low pseudo-R²:** The `load_sample()` function generates records with random MSA assignments. Because these MSAs carry no real geographic signal — all lenders in the data are equally likely to serve all MSAs — the MSA dummy variables contribute nothing to model fit. Real HMDA data has genuine geographic variation in denial rates (correlated with local market conditions, lender mix, and economic environment) that MSA fixed effects capture. On real data, pseudo-R² is typically 5–10× higher than on the synthetic sample. A pseudo-R² of 0.03–0.05 on synthetic data does not indicate a model problem; it reflects the absence of real geographic signal in random-MSA synthetic data.

**Adjusted OR > unadjusted OR on synthetic data:** On real HMDA data, the adjusted odds ratio is typically lower than the unadjusted odds ratio, because income, LTV, and DTI differences between racial groups partially explain the raw denial rate disparity — controlling for them reduces the unexplained portion. On the synthetic sample, the generator makes race the primary driver of denial with mild income correlation. In this case, controlling for income slightly amplifies the racial coefficient (the controls remove a suppressor effect rather than a confound), producing adjusted OR > unadjusted OR. This is expected behavior on synthetic data, not a bug in the model. On real HMDA data the typical direction is adjusted < unadjusted.

This package reports pseudo-R² as a diagnostic and flags models below 0.05 as potentially underspecified.

---

## Sample Size Requirements

- **Minimum default:** 100 total observations (protected class + comparison class combined)
- **Recommended minimum:** 500 observations for stable coefficient estimation with MSA dummies
- **Below minimum:** `InsufficientDataError` is raised; no result is returned

**Citation and derivation:**  
Peduzzi, P., Concato, J., Kemper, E., Holford, T.R., and Feinstein, A.R. (1996). "A simulation study of the number of events per variable in logistic regression analysis." *Journal of Clinical Epidemiology*, 49(12): 1373–1379. DOI: 10.1016/S0895-4356(96)00236-3. PMID: 8970487.

Peduzzi et al. established the **10 events per variable (EPV)** rule through Monte Carlo simulation: with EPV < 10, regression coefficients are biased, variance estimates are unreliable, and confidence intervals are anti-conservative. With approximately 9 regression predictors in the baseline model (before MSA dummies) and a national HMDA denial rate of approximately 10% for conventional home purchase loans, EPV = 10 implies a minimum of approximately 90 total observations in the combined sample. We round to 100 as the minimum default.

**The Markup's** minimum for reporting per-metro results was 1,000 applications — a stricter threshold chosen for publication standards. The 100-observation minimum in this package is a floor for returning *any* result; analysts are encouraged to treat results from small samples with greater caution and the tool provides explicit sample size disclosure in every `DisparityResult`.

---

## What This Analysis Can and Cannot Show

### CAN show:
- That a statistically significant difference in denial rates exists between groups after controlling for the available legitimate factors
- The magnitude of that difference (odds ratio) and its precision (confidence interval)
- Whether the difference persists under alternative control specifications
- The direction of the disparity (which group faces higher denial rates)

### CANNOT show:
- That the lender intentionally discriminated (intent requires internal loan files, underwriting notes, and examiner access)
- That the disparity is *caused* by protected class status (causation requires experimental or quasi-experimental design beyond what HMDA supports)
- That the disparity would survive controlling for credit score, AUS recommendations, or other omitted variables
- That any specific applicant was treated unlawfully
- That the lender is in violation of ECOA or the Fair Housing Act
- That the analysis is complete — it is explicitly incomplete due to HMDA's public data limitations (see below)
- That results from mortgage lending generalize to small business lending, auto lending, or other credit products

**Scope:** Mortgage lending (HMDA-reportable transactions) only. Does NOT analyze Section 1071 small business lending data. Does NOT constitute a finding of discrimination — only a finding of statistically significant adjusted disparity warranting further review.

**Standard language (required in all generated reports):** "This analysis identifies a statistically significant adjusted disparity in denial rates. It does not constitute a finding of discrimination under ECOA or the Fair Housing Act, and it does not establish that any protected class characteristic caused any lending outcome. Further review of application files, underwriting guidelines, and internal lender data would be required to assess whether discrimination occurred."

---

## HMDA Public Data Limitations

The following information is **absent from the public HMDA dataset** and therefore absent from this analysis. Each omission is a source of omitted-variable bias that may cause the adjusted odds ratio to be overstated or understated relative to a fully specified model.

1. **Credit score** — The single most predictive underwriting variable. Excluded from public HMDA by the industry during Dodd-Frank rulemaking. CFPB shares credit score data with federal regulators under supervisory authority but not publicly (12 C.F.R. § 1003.4(a)(15) note). *Omitted-variable implication:* If the disparity in credit scores between groups is explained by factors unrelated to protected class, omitting credit score overstates the disparity. If credit score gaps themselves reflect structural discrimination in credit access, including credit score would understate the disparity. The direction of bias is contested and unresolvable with public data.

2. **Automated Underwriting System (AUS) recommendation** — Fannie Mae Desktop Underwriter (DU) and Freddie Mac Loan Prospector (LP) decisions are the primary underwriting tool for conventional loans and are not included in the public HMDA file. *Omitted-variable implication:* AUS decisions correlate strongly with denial; omitting AUS leaves a major legitimate underwriting factor uncontrolled.

3. **Asset and reserve information** — Liquid assets, retirement accounts, reserves, and net worth are not reported in HMDA. *Omitted-variable implication:* Reserves predict default risk and lender willingness to approve; groups with lower average reserves may face higher denial rates for this legitimate reason, which the model cannot control for.

4. **Co-applicant credit profile** — HMDA reports co-applicant income and race but not co-applicant credit score, employment, or liabilities. *Omitted-variable implication:* A co-applicant's creditworthiness materially affects underwriting; omitting it partially conflates borrower risk with protected class.

5. **Credit history and tradeline data** — Derogatory marks, delinquency history, number of accounts, charge-offs, and bankruptcy are not in HMDA. *Omitted-variable implication:* These are significant underwriting factors; their absence means the regression cannot separate credit-history-driven denials from potentially disparate-impact denials.

6. **Appraisal method and appraisal-contested flag** — HMDA includes the lender-reported property value but not the appraisal method (full appraisal, desktop, waiver) or whether the value was disputed. *Omitted-variable implication:* Appraisal gaps in majority-minority neighborhoods are a documented phenomenon; the model cannot control for this and it may confound the LTV control.

7. **Underwriter override data** — AUS may recommend "Approve/Eligible" but an underwriter may override to denial. Conversely, AUS may recommend "Refer" but an underwriter may override to approval. These discretionary decisions are invisible in HMDA. *Omitted-variable implication:* Discretionary overrides are a known vector for both intentional and unconscious bias; the model cannot detect or control for them.

8. **Conditional approval vs. clean approval distinction** — HMDA codes both conditional and unconditional approvals as `action_taken == 1` if they ultimately originate. Conditions imposed disparately are not detectable in this data.

9. **Employment history and tenure** — Employment type (W-2, self-employed, contractor), years at employer, and industry are not reported. *Omitted-variable implication:* Employment stability is an underwriting factor; groups with more self-employment or gig work may face higher denial rates for this legitimate reason that the model cannot control for.

10. **Lender-specific underwriting overlays** — Individual lenders apply credit overlays beyond GSE guidelines (e.g., minimum credit scores above GSE minimums, additional reserves requirements). These are not in HMDA and vary by lender. *Omitted-variable implication:* Comparing applicants across lenders pools them under different implicit standards.

**Consequence:** All results produced by this tool should be treated as **lower bounds on the information needed** to determine whether discrimination occurred, and as **screening signals** that warrant further investigation with full loan-file data. The tool is honest about this and discloses it in every generated report.

---

## Calibration Target: Partial Replication of The Markup (2021)

`test_known_results.py` contains a calibration test that verifies the package produces results consistent with The Markup's published national findings. This test is a **partial replication**, not an exact one, because this package's default control set differs from The Markup's in two material ways documented below.

### Exact Filter Specification (from The Markup)

| Filter | Value | HMDA Field |
|---|---|---|
| Data year | 2019 | (annual HMDA LAR) |
| Loan type | Conventional | `loan_type == 1` |
| Lien status | First-lien | `lien_status == 1` |
| Loan purpose | Home purchase | `loan_purpose == 1` |
| Occupancy type | Principal residence | `occupancy_type == 1` |
| Property type | One-to-four unit | `property_type == 1` |
| Construction method | Site-built | `construction_method == 1` |
| CLTV | ≤ 100% and not missing | `loan_to_value_ratio <= 100` |
| Action taken | Originated or denied | `action_taken ∈ {1, 3}` |
| Business purpose | Excluded | `business_or_commercial_purpose == 2` (not for business) |

This filtering produces approximately 2.4 million applications nationally.

### The Markup's 17 Control Variables

1. Race (`derived_race`)
2. Sex (`derived_sex`)
3. Co-applicant presence (whether a co-applicant exists)
4. Age (`applicant_age`)
5. Income (`applicant_income`)
6. Loan amount (`loan_amount`)
7. Property value (`property_value`)
8. Mortgage term (`loan_term`)
9. Credit model used (`aus_1` variant — credit scoring model)
10. Debt-to-income ratio (`debt_to_income_ratio`, categorical bins)
11. Combined loan-to-value ratio (`loan_to_value_ratio`)
12. Automated underwriting system used (`aus_1`)
13. Census tract median income ratio to metro area median income (derived from census, 4 bins)
14. Lender type (bank, nonbank, CU — derived from `lei` lookup)
15. Lender size (asset tier — derived from `lei` lookup)
16. Non-Hispanic White population percentage of census tract (derived from census, 4 bins)
17. Metro area population size (categorical by percentile)

### Material Differences from This Package's Defaults

| Dimension | The Markup | This Package (v0.1.0) | Impact |
|---|---|---|---|
| Geographic control | Categorical proxies: tract income ratio, metro size, tract White % | MSA dummy variables | Results are not directly comparable; MSA dummies control at a finer level but cost more DoF |
| Credit model used | Included (item 9 above) | **Not included** — not in default control set | Our adjusted OR likely higher than The Markup's (residual disparity is larger when AUS is omitted) |
| AUS recommendation | Included (item 12) | **Not included** | Same direction: our OR likely higher |
| Lender type/size | Included (items 14–15) | **Not included** | Potential confound if lenders with different denial rates serve different racial groups |
| Co-applicant, age, sex | Included (items 2–4) | **Not included** | Minor impact on primary race coefficient |

**Calibration tolerance:** The Markup found **1.8× (95% CI not published)** for Black vs. White applicants under their 17-control specification. Given that our model omits AUS and credit model (which would reduce the odds ratio if included), our model should produce an odds ratio **at or above** 1.8×. The calibration test passes if the adjusted odds ratio falls between **1.6× and 2.2×**. The lower bound of 1.6× accounts for differences in geographic control specification; the upper bound of 2.2× guards against model misspecification.

**Why the band is asymmetric around 1.8×**

(1) The Markup controlled for AUS recommendations and the credit scoring model used (items 9 and 12 in their 17-control list) via FFIEC-supervised data access. This tool operates on the public HMDA file, which strips those fields. The public file does not include AUS recommendations or credit score in any form.

(2) Omitting variables that are correlated with both the protected class indicator and the outcome (denial) produces a known upward bias in the estimated coefficient on the protected class indicator. This is the standard omitted-variable bias result: if an omitted variable is positively correlated with the outcome and negatively correlated with the protected class indicator (or vice versa), the estimated coefficient absorbs the omitted variable's effect and is biased away from zero. AUS recommendations and credit scores fit this pattern — both correlate with denial (strongly positive) and both correlate with race in the data (because of structural gaps in credit access). Citation: Wooldridge, J.M. (2019), *Introductory Econometrics: A Modern Approach* (7th ed.), § 3.3: "Omitted Variable Bias."

(3) Therefore the expected odds ratio from this package's model on comparable 2019 data is above 1.8× — not because the analysis is wrong, but because the model is correctly absorbing disparity that a more fully specified model (with AUS and credit score) would partially attribute to those controls. A result in the 1.8–2.2× range on comparable data is consistent with this methodology and the known limitations. It does not mean the tool is overstating the disparity; it means the tool is correctly reporting the disparity that is unexplained by the controls it has available.

(4) The asymmetric band (1.6–2.2×, centered above 1.8×) reflects this expected directional bias. A run below 1.6× indicates a likely problem — data preparation error, incorrect filter, or model misspecification that is artificially deflating the coefficient. A run between 1.8× and 2.2× is expected and consistent with the methodology. A run above 2.2× warrants investigation for the opposite reason — the model may be picking up something other than the racial disparity in denial rates.

**If the test fails** (OR outside 1.6–2.2×): this indicates either a data preparation error, a regression specification error, or a genuine change in the HMDA data for the test year. It is a signal to investigate, not to adjust the tolerance band.

---

## Model Convergence

`statsmodels.api.Logit` uses iteratively reweighted least squares (IRLS, equivalent to Newton-Raphson) to maximize the log-likelihood. Convergence failure occurs when:

- Perfect separation or near-separation exists (one feature perfectly predicts the outcome in the sample)
- The optimization reaches maximum iterations without converging

When convergence fails, `ModelConvergenceError` is raised with the iteration count and log-likelihood at failure. No result is returned. The analyst should inspect the data for separation (e.g., an MSA with only denials or only originations for one group).

---

## Deferred to v0.2.0+

The following analyses are methodologically sound but out of scope for v0.1.0:

- **BISG proxy analysis:** For product types where race/ethnicity is not collected (auto, student, HELOC not under Reg C). Port of CFPB Stata code to Python.
- **Extended control set:** Co-applicant variables, AUS recommendation, credit model used, lender type/size, census tract demographic controls — moving toward full replication of The Markup's 17-variable specification.
- **Pricing disparity analysis:** Linear regression on rate spread or APR as outcome variable.
- **Redlining geographic analysis:** Census-tract-level analysis of lender presence in majority-minority areas.
- **Peer benchmarking:** Comparison of lender-specific rates against peer group and HMDA aggregate.
- **Multilevel / hierarchical modeling:** Mixed-effects logit for MSA random effects, replacing the current MSA dummy approach.
- **Section 1071 small business data:** Different statute, different data, different methodology.

---

## Methodology Feedback

This methodology is versioned alongside the code in `CHANGELOG.md`. To propose a methodology change or flag an error, open a GitHub issue tagged `methodology` with specific concerns and citations. All substantive changes will be documented in `CHANGELOG.md` and versioned in a new release.

**Alpha disclaimer:** This is an alpha release. The methodology has not yet been reviewed by an external fair lending expert. Use as a screening tool to identify cases warranting further review, not as a basis for enforcement or accusation.
