# Changelog

All notable changes to `fair-lending-screener` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [0.2.0] — 2026-05-22

### Added

- `InvalidDataYearError` typed exception — raised when `data_year` fails validation
- `data_year` range validation in `adjusted_denial_disparity()`: must be `int`,
  `2018 ≤ data_year ≤ current calendar year`; pre-2018 years lack LTV/DTI/property_value
- `MethodologyDocNotFoundError` typed exception — raised by `get_methodology_path()` and
  `get_limitations_path()` when the bundled file is absent from the installed package
- Full Python 3.9–3.12 matrix in `data-health.yml` (previously 3.11 only)
- Release workflow (`.github/workflows/release.yml`): builds wheel from tagged commit,
  runs full test suite against the installed wheel in a fresh venv, refuses to publish if
  git tag ≠ pyproject.toml version, publishes via PyPI OIDC trusted publishing
- `CONTRIBUTING.md` with release-process runbook

### Changed

- `prepare_for_analysis()` now coerces `business_or_commercial_purpose` to numeric before
  filtering; documents the NaN/Exempt (code 1111) policy explicitly in methodology.md
- `adjusted_denial_disparity()` `sample_size < 100` guardrail branch in `_check_guardrails()`
  removed entirely; `InsufficientDataError` (raised before any result is returned when
  `n < min_sample_size`) supersedes it — fixing LOW-F from the v0.1.1 audit
- `DisparityResult.limitations` last entry is now conditional on `is_statistically_significant`
  (was always `STANDARD_DISCLAIMER` regardless of result)

### Fixed

- **HIGH-A / HIGH-B** — `data_year` validated on entry; string, float, pre-2018, and
  future-year values rejected with a typed exception and actionable message
- **HIGH-C** — Positive-guardrail test (`test_report_with_lender_name_significant`) replaced
  with a deterministic mock-based test that never skips
- **HIGH-D** — `business_or_commercial_purpose` column coerced to numeric before `== 2`
  comparison; string "2" from CSV no longer silently drops all records
- **HIGH-E / MED-2** — `data-health.yml` calls `prepare_for_analysis(validate_controls=True)`;
  workflow exits 1 on missing FFIEC-standard controls
- **MED-A** — `DisparityResult.limitations` last entry matches significance outcome
- **MED-B** — `get_methodology_path()` / `get_limitations_path()` raise typed exception when
  bundled file is absent; zero-test-coverage gap closed
- **CRIT-A** — pyproject.toml version now matches git tag (enforced by release workflow guard)
- **CRIT-B** — Test suite updated to pass `data_year=` in all `adjusted_denial_disparity()` calls;
  CI now tests the installed wheel, not the editable source
- **LOW-F** — Dead `sample_size < 100` guardrail branch removed; `InsufficientDataError`
  fires at the enforced minimum before a result is returned

---

## [0.1.1] — 2026-05-22 — **YANKED**

> **YANKED on PyPI.** Do not pin to this version. Superseded by v0.2.0.
>
> **Why it was yanked:**
> - `pyproject.toml` declared `version = "0.1.0"` while the published wheel declared `0.1.1` —
>   the repository and the PyPI artifact described different software (audit finding CRIT-A)
> - No `v0.1.1` git tag was created — the published release cannot be reproduced from any
>   ref in the repository (audit finding CRIT-A)
> - The test suite was never updated to pass `data_year=` to `adjusted_denial_disparity()`,
>   so CI (which tested the editable v0.1.0 source, not the published wheel) was green for
>   code that would `TypeError` on every caller of the published package (audit finding CRIT-B)
> - `data_year` was introduced as a required parameter in a patch release — a
>   backwards-incompatible API change that belongs in a minor bump (audit finding HIGH-A)
>
> The v0.2.0 release fixes all of the above.

### Fixed in v0.1.1 (carried forward to v0.2.0)

- **CRIT-1** — `generate_disparity_report()` now uses `STANDARD_DISCLAIMER_NON_SIGNIFICANT`
  on the non-significant path; `STANDARD_DISCLAIMER` ("identifies a statistically significant
  adjusted disparity") no longer appears in non-significant reports
- **CRIT-2** — Spurious second `controls_used` assignment (using pre-drop `feature_cols`) removed;
  `DisparityResult.controls_used` and `dropped_controls` are now mutually exclusive
- **HIGH-1** — `min_sample_size` default raised from 100 to 500; methodology.md derives
  EPV ≈ 5.5 at n = 500 and notes this is below the Peduzzi EPV = 10 threshold
- **HIGH-2** — `data_year` required parameter added; recorded in `DisparityResult.provenance`
- **HIGH-3** — `prepare_for_analysis()` applies `business_or_commercial_purpose == 2` filter
  (Filter 9 per The Markup spec)
- **HIGH-4** — `docs/methodology.md` bundled inside the wheel as
  `fair_lending_screener/_methodology_doc.md`; `get_methodology_path()` and
  `get_limitations_path()` added to public API
- `STANDARD_DISCLAIMER_NON_SIGNIFICANT` constant added to `methodology.py`
- `ALPHA_DISCLAIMER` updated from v0.1.0 to v0.1.1

### Introduced in v0.1.1 (fixed in v0.2.0)

- **HIGH-A** — `data_year` required with no default in a patch release (SemVer violation)
- **HIGH-B** — `data_year` accepted any type without validation
- **HIGH-D** — `business_or_commercial_purpose` not coerced to numeric; string "2" dropped all records
- **HIGH-E** — `data-health.yml` still called `validate_controls=False` (MED-2 from v0.1.0 audit)
- **LOW-D** — `data-health.yml` still used Python 3.11 only

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
- `load_sample()`: synthetic sample with all required fields
- `prepare_for_analysis()`: applies all FFIEC dataset filters and derives regression features
- `check_data_source()`: CFPB API health check before analysis

**Report generation**
- `generate_disparity_report()`: journalist-legible Markdown with headline finding, controls, limitations, "what this does NOT prove" section, reproducibility provenance block
- Safety guardrails (A7): lender name suppressed from headlines when p > 0.05, sample < 100, non-convergence, or pseudo-R² < 0.05

**Typed exceptions**
- `InsufficientDataError`, `ModelConvergenceError`, `InvalidProtectedClassError`,
  `MissingControlsError`, `DataSourceError`, `InsufficientGroupSizeError`

**Dual-import shim**
- `import fairlendingscreener` works as an alias for `import fair_lending_screener`

**Documentation**
- `docs/methodology.md`: complete statistical methodology with citations
- `docs/limitations.md`: HMDA public data limitations
- `docs/examples/quickstart.md`: working quickstart guide

**Tests**
- `test_disparity.py`, `test_report.py`, `test_edge_cases.py`, `test_known_results.py`

**CI**
- `test.yml`: pytest on every push (Python 3.9–3.12)
- `data-health.yml`: weekly Sunday 6am UTC, minimal live API analysis

### Methodology

> **Alpha release.** Methodology peer review by external fair lending expert planned before v1.0.0.

### Known Limitations at Release

- No credit score control (not in public HMDA)
- No AUS recommendation control (not in public HMDA)
- `min_sample_size=100` EPV ≈ 1.1 at n=100 — raised to 500 in v0.1.1
- No `business_or_commercial_purpose` filter — added in v0.1.1
- `data_year` absent from provenance — added in v0.1.1

---

[0.2.0]: https://github.com/Jaypatel1511/fair-lending-screener/compare/v0.1.0...v0.2.0
[0.1.1]: https://github.com/Jaypatel1511/fair-lending-screener/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Jaypatel1511/fair-lending-screener/releases/tag/v0.1.0
