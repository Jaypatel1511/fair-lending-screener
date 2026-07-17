# Rate-Spread / Pricing Disparity Methodology — fair-lending-screener v0.3.0 (v3)

**Status:** Full methodology draft v3, resolving all Audit-2 findings (5 CRIT, 8 HIGH). Supersedes v2. Written to go back out for a **third fresh-session hostile audit** before any code.

**What changed from v2 (the load-bearing reversals):**
- **Calibration: the external magnitude anchor is DROPPED.** No published study shares this tool's design; the tool is explicitly **uncalibrated-and-disclosed**, validated instead by synthetic-recovery tests (§9). This removes the anchor-provenance fabrication surface that failed twice.
- **Points/credits are NO LONGER controls** — they are finance charges inside the APR (§7).
- **`activity_year >= 2018` is a hard gate** (§5) — pre-2018 rate_spread is threshold-reported, blank ≠ missing.
- **`{1,2}` selection sensitivity is redesigned** as a genuine reduced-control model (§4), now viable because cost controls are gone.
- **§6 sentinel discipline extended to EVERY regressor**, incl. `intro_rate_period` (NA for fixed-rate) (§6).

**Scope locked (Jay):** conventional-only; 2018+; continuous rate_spread; `{1}` primary + `{1,2}` reduced-control sensitivity; uncalibrated + disclosed.

---

## 1. Purpose & firewall placement
Regression-adjusted **pricing** disparity on continuous HMDA `rate_spread` (APR − APOR), reported as a **screening signal, never a finding of discrimination.** Inferential → belongs in fair-lending-screener, not hmda-analyzer. Screener never named in general-audience/Lara contexts. (Ruled clean in both prior audits.)

## 2. Scope
**In:** conventional (`loan_type == 1`), closed-end, 1–4 unit site-built non-business mortgages, `activity_year >= 2018`; continuous rate_spread, regression-adjusted, protected-class coefficient in basis points.
**Out (rationale unchanged):** government-backed loans (separate calibrated config later); HPML binary cut; Heckman correction; reverse mortgages; open-end/HELOC; credit-score imputation; BISG; Section 1071.

## 3. Outcome variable
- Continuous `rate_spread` (APR − APOR, pp; §1003.4(a)(12)). Do not recompute APOR.
- **OLS** (`statsmodels.api.OLS`) with cluster-robust SEs (§8). Second regression path in the package (not a Logit reuse).
- **Why rate_spread, not the note rate** (`interest_rate`, which IS in the public LAR): the public LAR has **no month/day date** (only `activity_year`), so the within-year rate environment (2022: ~3%→~7%) is not absorbable by time FE. rate_spread is APOR-matched at the exact rate-set date before that date was stripped — the only date-normalized pricing outcome available. **Residual limitation:** year-level granularity leaves within-year lock-timing variation APOR-matching doesn't fully remove (§13).
- **rate_spread is a net-of-points price.** Because discount points are finance charges inside the APR (§1026.4(b)(3)), the spread already reflects the borrower's points/rate tradeoff. That tradeoff is **part of the outcome, not a confound to be controlled away** (see §7).

## 4. Population — primary + redesigned selection sensitivity
`rate_spread` is reported for `action_taken == 1` (originated) **and `== 2`** (approved-but-not-accepted), per Reg C commentary 4(a)(12)-7/-8.
- **Primary: `{1}` originated.**
- **Selection sensitivity: `{1,2}` reduced-control model.** In v2 this was a guaranteed no-op — cost fields come from the Closing Disclosure and are NA for unclosed action-2 rows, so requiring them as regressors dropped 100% of action-2 rows and `{1,2}` collapsed to `{1}`. Removing points/credits as controls (§7) fixes this: the §7 equation now uses only application-side regressors that exist for approved applications, so action-2 rows survive and `{1,2}` is a real, larger population. `[BUILD-RECON: confirm each §7 regressor is populated for action_taken == 2; any that is origination-only is excluded-with-reason and noted, not silently dropped.]`
- **Interpretation rule:** `{1,2}` conditions only on the lender's approval/price decision (the conduct under exam); `{1}` adds borrower-side acceptance selection. Material divergence between the two ⇒ selection is doing real work and must be surfaced, not buried under a disclaimer.

## 5. Sample filters
- `loan_type == 1` (conventional).
- **`activity_year >= 2018` (HARD GATE).** Pre-2018, rate_spread was reported **only if** the spread exceeded 1.5/3.5 pp (2009–2017 threshold reporting); a pre-2018 blank means *below threshold* = a real, normally-priced loan. Admitting pre-2018 data + §6 "blank → exclude" would drop every normally-priced loan and fit the subprime tail. 2018+ only. *(Resolves the CRIT.)*
- 1–4 unit, `construction_method == 1`, `business_or_commercial_purpose == 2` (Exempt/1111/NaN → DROP), `occupancy_type == 1`, `loan_to_value_ratio ≤ 100`.
- `loan_purpose` configurable (home purchase default; refi 31 / cash-out 32 run separately).

## 6. Sentinel handling — per-field, EVERY regressor (not just cost fields)
Handling is per-field, sourced to each field's Reg C cite, with three states (real-value / NA / Exempt). **Every regressor in §7 has an explicit row** — a field without a rule is a silent-imputation/silent-drop hazard.

| Field | Cite | blank/absent means | Handling |
|---|---|---|---|
| `rate_spread` | (a)(12) | missing (0 = priced at APOR, real favorable) | blank/NA/Exempt → exclude-with-reason; never 0 |
| `combined_loan_to_value_ratio` | (a)(24) | missing | NA/Exempt → exclude-with-reason |
| `debt_to_income_ratio` | (a)(23) | missing / binned | NA/Exempt → exclude-with-reason; use HMDA bin encoding |
| `property_value` | (a)(28) | missing | NA/Exempt → exclude-with-reason; guard log() domain (§ below) |
| `income` (applicant) | (a)(10) | thousands; **`1111` = real $1.111M**, NOT an exemption | NA → exclude-with-reason; **never treat 1111 as a sentinel here** |
| `loan_amount` | (a)(7) | present | guard log() domain |
| `loan_term` | (a)(25) | NA for open-end/reverse (already excluded) | NA → exclude-with-reason |
| `lien_status` | (a)(33) | present for the covered set | — |
| `intro_rate_period` | (a)(26) | **NA for every fixed-rate loan** (Cmt 4(a)(26)-3) | **derive `is_arm`**: real number → ARM (1); NA → fixed (0). Use `is_arm` dummy. **Do NOT use `intro_rate_period` as a continuous regressor** — it is undefined for the fixed-rate majority; a generic NA-drop would silently model ARMs only. *(Resolves the CRIT.)* |

- **`1111` is never a global sentinel** — only the partial-exemption code for the specific fields whose cite defines it; for `income` (thousands) it is a real $1.111M applicant. *(Portfolio-recurring — the hmda-analyzer CRA-proxy cycle hit the same 1111 hazard.)*
- **log() domain guard:** `income`/`loan_amount`/`property_value` ≤ 0 or non-finite → exclude-with-reason (`out_of_range_*`), never log a zero/negative.
- **Attribution fix (Audit-2):** the "leave blank if none" wording for `discount_points`/`lender_credits` is **FFIEC FIG/reporting-form language, not CFR text** — cite it as FIG, not §1003.4. (These fields are no longer controls, but the convention still matters if ever surfaced.)
- **TDD:** one sentinel mutation test per field per state; each must bite.

## 7. Controls & exact equation (points REMOVED)

```
rate_spread_i = β0
              + β_pc · protected_class_i          # coefficient of interest (bps)
              + β1 · log(loan_amount_i)
              + β2 · combined_LTV_i
              + Σ β · DTI_bin_i                     # categorical, (a)(23)
              + β3 · log(property_value_i)
              + β4 · log(income_i)
              + Σ β · lien_status_i
              + β5 · loan_term_i
              + β6 · is_arm_i                       # derived from intro_rate_period (§6)
              + Σ β · MSA_i                          # pooled dummies, sparse handling §10
              + ε_i
```
- **No `discount_points` / `lender_credits`.** They are finance charges *inside* the APR (§1026.4(b)(3)); rate_spread is APR−APOR, so controlling for points conditions the outcome on a component of its own construction. The anchor literature's own 2018/2019 HMDA test found the minority coefficient **rose** when controlling for points — the v2 "attenuation" claim was refuted. The points/rate tradeoff is disclosed as **part of the net-of-points outcome** (§3), not removed. *(Resolves the §7 CRIT.)*
- No `loan_type` dummy (conventional-only). `total_loan_costs`/`origination_charges` not used (overlap + missingness).
- **`n` in every output is the post-exclusion modeled n** (rows in the regression), never a pre-drop count. *(MED-4 carried.)*
- Equation == code, exactly — no drift. *(MED-1 carried.)*

## 8. Inference — cluster-robust SEs
- Default `cov_type='cluster'`, clustered on `lei`. Prices come off lender rate sheets → within-lender residual correlation; HC1/HC3 don't touch it and on 10⁵–10⁶ rows manufacture significance. Single-lender screen → cluster on MSA.
- **Adequacy = effective cluster count**, not `n`. Below the floor `[SET IN AUDIT-3: ~30–50 effective clusters]` → wide-CI/low-power flag + lender-name suppression (§12). `[SET IN AUDIT-3: whether to offer a wild-cluster bootstrap for the few-cluster regime, or hard-suppress only.]`

## 9. Engine validation — UNCALIBRATED + DISCLOSED (replaces the external anchor)

**No external magnitude anchor is used, by decision.** No published study shares this tool's design: this tool is pooled public HMDA, APR-spread outcome, **includes** CRA tracts, has **no** GSE risk grid and **no** credit score. The most-cited benchmark (Bartlett et al.) uses the note-rate outcome, a GSE credit-score/LTV risk grid, conventional-conforming 30-yr fixed 2009–2015, and **excludes** CRA tracts — a fundamentally different estimand. Anchoring a magnitude to it produced two provenance fabrications in prior drafts. **The tool therefore asserts no expected coefficient magnitude.**

**What replaces calibration:**
1. **Synthetic-recovery validation (dev-time, the real engine check).** Simulate LAR-shaped data with realistic covariate structure and a **planted** protected-class disparity δ; confirm the OLS + cluster estimator recovers δ within its CI across many seeds and at several δ (including δ = 0, which must NOT produce significance above the nominal rate). This validates the estimator's unbiasedness and CI coverage **without asserting any real-world magnitude.** This is the honest analogue of calibration: it tests the machine, not the world.
2. **Plausibility guard, not a band.** A `|coefficient|` beyond a wide ceiling `[SET IN AUDIT-3: e.g. ±100 bps]` is flagged as a probable spec/data error — a sanity signal, explicitly **not** a fair-lending threshold and **never** a runtime gate on a named lender.
3. **Mandatory disclosure on every output:** "This estimate is not calibrated to an external benchmark; no published study shares this tool's data and design. Interpret the sign and significance as a screening signal only, not a magnitude to be compared against any published figure."

**For directional context only** (NOT a target, NOT in any output as a comparator): the peer literature finds small adjusted rate disparities (single-digit to low-double-digit basis points). Cited to orient the developer, never to calibrate or to appear beside a result.

## 10. Outliers & sparse MSAs — no silent substitution
- **No winsorizing** (rewrites observed values, attenuates toward a lender-favorable result). Extremes excluded-with-reason (threshold + count reported) or retained — never rewritten.
- **Sparse MSAs not silently collapsed to reference.** Reassignment is neither classified nor excluded and evades a naive identity → report the reassigned count, or exclude-with-reason `sparse_msa`.

## 11. Reconciliation identity
`classified + excluded + reassigned == universe`, exact; every excluded row reason-keyed, every reassigned row counted. Vocabulary: `na_rate_spread`, `exempt_rate_spread`, `na_ltv`, `na_dti`, `na_property_value`, `na_income`, `na_loan_term`, `pre_2018_excluded`, `sparse_msa`, `out_of_range_*`, `action2_field_unavailable`, … No silent drops or reassignments.

## 12. Interpretation, language, suppression
- Coefficient as **adjusted pricing disparity in basis points**; "screening signal, not a finding of discrimination." Never "discrimination"/"overcharging."
- **Three-location conditional disclaimer** (render / `.limitations[-1]` / `.interpretation`), significant/non-significant variants, PLUS the selection caveat (§4), the within-year lock-timing caveat (§3), and the **uncalibrated caveat** (§9) — all bound to the metric/table, non-strippable.
- **Lender-name suppression** — suppress unless ALL: effective cluster count ≥ §8 floor; protected-class CI excludes zero AND CI width < `[SET IN AUDIT-3]`; every FFIEC-standard control present; model well-conditioned (condition number < `[SET IN AUDIT-3]`); sample ≥ min. **Not** pseudo-R² (doesn't transfer — MSA FE inflate R² via geography while the coefficient stays imprecise; precision, not fit, is the risk). Bare `p>0.05` untrustworthy until SEs cluster (§8).

## 13. Limitations (3+ places)
All denial-engine limitations, PLUS:
- **Uncalibrated** — no published benchmark matches this tool's design; the estimate carries no expected magnitude (§9). Headline limitation.
- **Conditional on origination** — `{1}` conditions on approval + acceptance; `{1,2}` isolates the lender decision (§4).
- **Net-of-points outcome** — rate_spread embeds the points/rate tradeoff; a group difference in points-purchasing is part of the measured price, not removed (§7).
- **Within-year lock-timing** not fully removed by APOR-matching (§3).
- **2018+ only** — pre-2018 pricing not analyzable (threshold-reporting, §5).
- ~~"No note rate"~~ deleted (false; `interest_rate` is in the LAR).

## 14. Citations (verify verbatim in full-doc pass; NO fabricated table cells)
12 CFR §1026.35 (HPML, verified current); §1003.4(a)(12) rate_spread; §1003.4(a)(7)(10)(23)(24)(25)(26)(28)(33) regressor fields; §1003.4(a)(21) interest_rate; Reg C commentary 4(a)(12)-7/-8 and 4(a)(26)-3; §1026.4(b)(3) (points are finance charges); FFIEC FIG (blank-conventions, cited as FIG not CFR); Wooldridge §3.3; Greene §17 (OLS/robust + clustered inference). **Bartlett et al. is cited, if at all, only as directional context with an explicit "not a calibration target and design-mismatched" note — and never with a specific table/coefficient cell unless read directly from the published JFE typeset.**

## 15. Open items → Audit-3 / build-recon
- `[SET IN AUDIT-3]` effective-cluster floor; few-cluster policy (bootstrap vs hard-suppress); plausibility ceiling; CI-width & condition-number suppression thresholds.
- `[BUILD-RECON]` which §7 regressors are populated for `action_taken == 2` (drives the real `{1,2}` sample); `rate_spread` public-CSV dtype and blank representation; exact FIG Exempt encoding.
- Audit-3 should pressure-test: the synthetic-recovery design (is the planted-δ generator realistic enough to be a meaningful check?); the net-of-points framing (is disclosing-not-controlling honest, or does it hide a real confound?); the `is_arm` derivation; whether dropping the anchor leaves the tool *too* unmoored to claim "examiner methodology."

---
### Gate
This doc → **third fresh hostile audit** → resolve → build (TDD, per-field sentinel mutations bite, synthetic-recovery tests) → fresh code audit → fix → ship → settle. Authoring + audit don't break the waterfall-py settle window.
