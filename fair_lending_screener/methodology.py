"""
Regulatory and methodological citations as versioned Python constants.

Storing citations here (rather than in docstrings or comments) means:
- They are importable and testable
- They appear verbatim in every generated report
- A citation change produces a visible code diff and changelog entry

Sources:
  FFIEC Interagency Fair Lending Examination Procedures (2009)
  The Markup national logistic regression methodology (2021)
  Peduzzi et al. (1996) — events-per-variable rule for logistic regression
  Wooldridge (2019) — omitted-variable bias, log transformation
  McFadden (1973) — pseudo-R² for discrete choice models
"""

# ── Primary Regulatory Source ──────────────────────────────────────────────────

FFIEC_FAIR_LENDING_PROCEDURES = (
    "FFIEC Interagency Fair Lending Examination Procedures (August 2009). "
    "Federal Financial Institutions Examination Council."
)
FFIEC_URL = "https://www.ffiec.gov/PDF/fairlend.pdf"
FFIEC_STATUTE_ECOA = "Equal Credit Opportunity Act, 15 U.S.C. § 1691 et seq."
FFIEC_STATUTE_FHA = "Fair Housing Act, 42 U.S.C. § 3605."

# ── Regulation C / HMDA ───────────────────────────────────────────────────────

REGULATION_C_CITATION = "Regulation C, 12 C.F.R. Part 1003 (implementing 12 U.S.C. § 2801 et seq.)."
HMDA_DTI_FIELD_CITATION = (
    "Debt-to-income ratio reporting: 12 C.F.R. § 1003.4(a)(23) and "
    "CFPB/FFIEC HMDA Filing Instructions Guide (current year edition)."
)
HMDA_RACE_FIELD_CITATION = (
    "Race self-reporting requirement for home mortgage applications: "
    "12 C.F.R. § 1003.4(a)(10) (Regulation C)."
)
HMDA_CREDIT_SCORE_EXCLUSION = (
    "Credit score excluded from public HMDA data. "
    "CFPB shares credit score with federal regulators under supervisory authority "
    "but not publicly. See 12 C.F.R. § 1003.4(a)(15) note."
)

# ── CFPB BISG Proxy ───────────────────────────────────────────────────────────

CFPB_BISG_METHODOLOGY = (
    "CFPB, 'Using Publicly Available Information to Proxy for Unidentified Race and Ethnicity' "
    "(September 2014, updated 2024). "
    "Consumer Financial Protection Bureau."
)
CFPB_BISG_URL = "https://files.consumerfinance.gov/f/201409_cfpb_report_proxy-methodology.pdf"

# ── The Markup Methodology ────────────────────────────────────────────────────

MARKUP_METHODOLOGY_CITATION = (
    "Martinez, Emmanuel and Lauren Kirchner. "
    "'How We Investigated Racial Disparities in Federal Mortgage Data.' "
    "The Markup, August 25, 2021."
)
MARKUP_METHODOLOGY_URL = (
    "https://themarkup.org/show-your-work/2021/08/25/"
    "how-we-investigated-racial-disparities-in-federal-mortgage-data"
)
MARKUP_NATIONAL_ODDS_RATIO = 1.8
MARKUP_NATIONAL_PSEUDO_R2 = 0.2256
MARKUP_DATA_YEAR = 2019

# ── Statistical Methodology Citations ─────────────────────────────────────────

PEDUZZI_EPV_CITATION = (
    "Peduzzi, P., Concato, J., Kemper, E., Holford, T.R., and Feinstein, A.R. (1996). "
    "'A simulation study of the number of events per variable in logistic regression analysis.' "
    "Journal of Clinical Epidemiology, 49(12): 1373–1379. "
    "DOI: 10.1016/S0895-4356(96)00236-3. PMID: 8970487."
)

MCFADDEN_PSEUDO_R2_CITATION = (
    "McFadden, D. (1973). 'Conditional logit analysis of qualitative choice behavior.' "
    "In P. Zarembka (ed.), Frontiers in Econometrics, Academic Press. "
    "McFadden noted that pseudo-R² values of 0.2–0.4 indicate excellent model fit."
)

WOOLDRIDGE_LOG_CITATION = (
    "Wooldridge, J.M. (2019). Introductory Econometrics: A Modern Approach (7th ed.). "
    "Cengage Learning. § 6.2: 'More on Using Logarithmic Functional Forms.' "
    "Log transformation is appropriate for right-skewed financial variables such as "
    "income, loan amount, and property value."
)

WOOLDRIDGE_OVB_CITATION = (
    "Wooldridge, J.M. (2019). Introductory Econometrics: A Modern Approach (7th ed.). "
    "Cengage Learning. § 3.3: 'Omitted Variable Bias.' "
    "Omitting variables correlated with both the outcome and the regressor of interest "
    "biases the estimated coefficient away from zero."
)

GREENE_LOGIT_CITATION = (
    "Greene, W.H. (2012). Econometric Analysis (7th ed.). Prentice Hall. "
    "Chapter 17: 'Discrete Choice.' "
    "Wald confidence intervals for logistic regression coefficients are asymptotically "
    "equivalent to profile-likelihood intervals at large sample sizes."
)

# ── Required Disclaimer Language ──────────────────────────────────────────────

STANDARD_DISCLAIMER = (
    "This analysis identifies a statistically significant adjusted disparity in denial rates. "
    "It does not constitute a finding of discrimination under ECOA or the Fair Housing Act, "
    "and it does not establish that any protected class characteristic caused any lending outcome. "
    "Further review of application files, underwriting guidelines, and internal lender data "
    "would be required to assess whether discrimination occurred."
)

STANDARD_DISCLAIMER_NON_SIGNIFICANT = (
    "This analysis did NOT identify a statistically significant adjusted disparity at the "
    "conventional p<0.05 threshold. Absence of statistical significance does not prove the "
    "absence of disparity — it may reflect sample size, model specification, or genuinely "
    "small disparities. This tool is a screening signal and does not constitute a finding "
    "of discrimination."
)

ALPHA_DISCLAIMER = (
    "Alpha release. Methodology peer review by external fair lending expert "
    "planned before v1.0.0. Use as a screening tool to identify cases warranting further "
    "analysis, not as a basis for enforcement or accusation."
)

# ── Calibration Target ────────────────────────────────────────────────────────

CALIBRATION_LOWER_BOUND = 1.6
CALIBRATION_UPPER_BOUND = 2.2
CALIBRATION_REFERENCE = MARKUP_NATIONAL_ODDS_RATIO

# ── Standard HMDA Limitations (always included in DisparityResult) ─────────────

STANDARD_LIMITATIONS = [
    "No credit score in public HMDA data — the single most predictive underwriting variable "
    "(collected under supervisory authority but not released publicly; 12 C.F.R. § 1003.4(a)(15) note).",

    "No AUS recommendation in public HMDA data — Fannie/Freddie DU/LP decisions, the primary "
    "conventional loan underwriting tool, are not in the public file.",

    "No asset or reserve data — liquid assets, retirement accounts, and reserves are not reported "
    "and are a legitimate underwriting factor.",

    "No co-applicant credit profile — co-applicant income is reported but co-applicant credit "
    "score, employment, and liabilities are not.",

    "No credit history or tradeline data — derogatory marks, delinquency history, and charge-offs "
    "are significant underwriting factors absent from HMDA.",

    "No underwriter override data — AUS approvals overridden to denial (or vice versa) are "
    "invisible in HMDA; these discretionary decisions are a known vector for bias.",

    "No appraisal method flag — property value is lender-reported; appraisal gaps in "
    "majority-minority neighborhoods are a documented issue not controllable here.",

    "No employment history — employment type (W-2 vs. self-employed), tenure, and industry "
    "are underwriting factors not reported in HMDA.",

    "Omitted-variable bias direction: omitting AUS and credit score, both of which correlate "
    "with race and denial, produces a known upward bias in the racial disparity coefficient "
    "(Wooldridge 2019, § 3.3). The adjusted odds ratio from this tool is an upper bound "
    "estimate relative to a fully specified model.",

    STANDARD_DISCLAIMER,
]
