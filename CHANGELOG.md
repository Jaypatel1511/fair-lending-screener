# Changelog

All notable changes to `fair-lending-screener` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [0.1.0] — 2026-05-21

### Added

**Core analysis**
- `adjusted_denial_disparity()`: binary logistic regression (statsmodels.api.Logit) for adjusted denial disparity analysis
- `DisparityResult` dataclass: adjusted odds ratio, 95% CI, p-value, sample sizes, controls used, model diagnostics, limitations, provenance
- FFIEC-standard dataset filters: conventional first-lien home purchase, site-built 1–4 unit, principal residence, LTV ≤ 100%
- MSA fixed effects: pooled national model with MSA dummy variables; MSAs with <30 observations grouped to reference category
- DTI binning: four categories (≤35%, 36–42%, 43–49%, ≥50%) + missing indicator, consistent with The Markup (2021)
- Log transformation of continuous controls (income, loan amount, property value) per Wooldridge (2019) §6.2
- Unadjusted odds ratio from 2×2 table alongside adjusted odds ratio

**Data layer**
- `load_from_api()`: wraps hmda-analyzer for CFPB Data Browser API access with endpoint health check
- `load_from_file()`: local CSV loading
- `load_sample()`: synthetic sample with all required fields (unlike hmda-analyzer's sample which lacks LTV/DTI/property_value)
- `prepare_for_analysis()`: applies all FFIEC dataset filters and derives regression features
- `check_data_source()`: CFPB API health check before analysis

**Report generation**
- `generate_disparity_report()`: journalist-legible Markdown with headline finding, controls, limitations, "what this does NOT prove" section, reproducibility provenance block
- Safety guardrails (A7): lender name suppressed from headlines when p > 0.05, sample < 100, non-convergence, or pseudo-R² < 0.05

**Typed exceptions**
- `InsufficientDataError`: sample below minimum with Peduzzi et al. (1996) EPV citation
- `ModelConvergenceError`: with iteration count and log-likelihood at failure
- `InvalidProtectedClassError`: lists valid values from data
- `MissingControlsError`: names missing columns
- `DataSourceError`: with URL and reason
- `InsufficientGroupSizeError`: per-group minimum check

**Dual-import shim**
- `import fairlendingscreener` works as an alias for `import fair_lending_screener`

**Documentation**
- `docs/methodology.md` (405 lines): complete statistical methodology with citations for every decision
  - FFIEC procedures as primary source
  - The Markup (2021) as calibration target with exact replication spec
  - Peduzzi et al. (1996) for sample size minimum
  - Wooldridge (2019) for log transformation and omitted-variable bias
  - McFadden (1973) for pseudo-R² interpretation
  - MSA fixed effects: why dummies vs. multilevel vs. stratified, sparse handling, DoF cost
  - Calibration tolerance 1.6–2.2× with asymmetric-band rationale (omitted AUS/credit score produces upward bias)
- `docs/limitations.md`: HMDA public data limitations
- `docs/examples/quickstart.md`: working quickstart guide

**Tests**
- `test_disparity.py`: happy-path and parametric tests
- `test_report.py`: report generation and guardrail tests
- `test_edge_cases.py`: all typed exception paths
- `test_known_results.py`: hand-calculated unadjusted OR verification + calibration range check

**CI**
- `test.yml`: pytest on every push (Python 3.9–3.12)
- `data-health.yml`: weekly Sunday 6am UTC, minimal live API analysis

### Methodology

> **Alpha release.** Methodology peer review by external fair lending expert planned before v1.0.0. Use as a screening tool to identify cases warranting further analysis, not as a basis for enforcement or accusation.

**What v0.1.0 covers:** Adjusted denial disparity analysis for conventional first-lien home purchase mortgage applications.

**Deferred to v0.2.0+:**
- BISG race/ethnicity proxy (for non-HMDA products)
- Extended control set (AUS, credit model, lender type, census tract demographics — toward full Markup 17-variable replication)
- Pricing disparity analysis (linear regression on rate spread/APR)
- Redlining geographic analysis (census-tract lender presence)
- Peer benchmarking (lender vs. market)
- Multilevel/hierarchical MSA modeling (replacing current dummy approach)
- Section 1071 small business lending

### Known Limitations

- No credit score control (not in public HMDA)
- No AUS recommendation control (not in public HMDA)
- MSA dummies differ from The Markup's categorical tract proxies — results not directly comparable
- Synthetic sample data (load_sample) not suitable for production analysis

### Known Issues

- Example notebook (`examples/disparity_demo.ipynb`) is included in the source distribution but not in the binary wheel due to `pyproject.toml` `package-data` scoping — `package-data` only applies to files inside Python package directories, and `examples/` has no `__init__.py`. To run the notebook, clone the GitHub repository. This will be fixed in v0.2.0.

---

[0.1.0]: https://github.com/Jaypatel1511/fair-lending-screener/releases/tag/v0.1.0
