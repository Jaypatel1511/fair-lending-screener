# Rate-Spread / Pricing Disparity Methodology — fair-lending-screener v0.3.0

**Status:** Full methodology draft (v2), resolving Audit-1 findings. Every ⚠ DECISION from the skeleton is now decided. This document is written to go back out for a **second fresh-session hostile audit** before any code. Provisional numeric bounds (calibration band, cluster-count floor) are flagged `[SET IN AUDIT-2]` where the value is a judgment the second audit should pressure-test.

**Scope decisions locked (Jay, July 14 2026):** conventional-only; originated `{1}` primary + approved-but-not-accepted `{1,2}` selection sensitivity; continuous `rate_spread` outcome only (no HPML binary this version).

---

## 1. Purpose & firewall placement

Adds regression-adjusted **pricing** disparity to fair-lending-screener, alongside the existing denial-disparity engine. The tool estimates whether a protected-class group receives systematically higher `rate_spread` (APR − APOR) after controlling for legitimate price drivers, and reports it **as a screening signal, never a finding of discrimination.**

This is **inferential** (regression-adjusted) and belongs here, on the inferential side of the descriptive/inferential firewall — not in hmda-analyzer. A raw, unadjusted rate_spread distribution (descriptive, no comparator, no inference) is a *separate* future decision for hmda-analyzer and is explicitly not in this feature. The screener is never named in general-audience/Lara contexts; pricing does not change that.

## 2. Scope

**In:** conventional (`loan_type == 1`), closed-end, first-lien and subordinate-lien, 1–4 unit site-built non-business mortgages; continuous rate_spread pricing disparity, regression-adjusted, protected-class coefficient in basis points.

**Out (with rationale):**
- **Government-backed loans (FHA/VA/USDA).** Priced on structurally different mechanics (e.g. FHA MIP is not a rate); a loan-type dummy is a weak control for that, and pooling diverges from the calibration anchor (§9). Ships later as a separately-scoped, separately-calibrated configuration. *(Resolves HIGH-6.)*
- **HPML binary cut.** Discards the continuous variation that is the entire point of a pricing screen (a 1.49 and a 0.10 spread would collapse to the same observation). Continuous-only. *(Resolves LOW-13.)*
- **Sample-selection (Heckman) correction.** No clean exclusion restriction in public HMDA; a mis-specified correction is worse than an honestly-bounded conditional estimate. Handled by the `{1}`/`{1,2}` sensitivity instead (§4).
- Reverse mortgages, open-end lines (HELOC), credit-score imputation, BISG (self-report available), Section 1071.

## 3. Outcome variable

- **Continuous `rate_spread`** (APR − APOR, percentage points; §1003.4(a)(12)). CFPB has already computed the APOR comparison — do **not** recompute APOR.
- **Model form: OLS** (`statsmodels.api.OLS`) with cluster-robust SEs (§8). Continuous outcome → linear model. Keeps statsmodels (p-values, CIs, diagnostics; no black-box ML; court-defensible). This is a genuine second regression path in the package, not a reuse of the Logit engine.

**Why rate_spread and not the note rate (`interest_rate`)** — the correct, primary-source-backed justification (replacing the skeleton's effort-based one):
- `interest_rate` **is** in the public LAR (§1003.4(a)(21)); the tool holds the note rate. *(HIGH-7: the skeleton's "no note rate" limitation was false and is deleted.)*
- The public LAR has **no month/day date** — only `activity_year`. Application date and action-taken date are stripped. The rate environment can move hundreds of bps within one calendar year (e.g. 2022: ~3% → ~7%). A note-rate model cannot absorb that with time fixed effects the way the anchor study does (it uses month-year FE). Any within-group difference in application timing would swamp a note-rate disparity estimate.
- `rate_spread` solves this precisely: the reporter matched APOR **at the exact rate-set date**, before that date was stripped from the public file. It is the only date-normalized pricing outcome available in public HMDA.
- **Honest residual limitation this creates:** year-level granularity means rate_spread still carries whatever within-year lock-timing variation APOR-matching doesn't fully remove. Stated in §12.

## 4. Population — conditioning, and the selection sensitivity

`rate_spread` is reported for `action_taken == 1` (originated) **and `== 2` (approved but not accepted)**, per Reg C commentary 4(a)(12)-7 (not-applicable list excludes approved-but-not-accepted) and -8 (which APR to use for those). *(CRIT-1: the skeleton's "field only exists for originations" claim was false and is deleted.)*

This makes the population a **real decision, not a structural given:**
- **Primary estimate: `{1}` originated.** Retains the full cost-control set (see §7 — cost fields are NA for non-originations, so `{2}` loses them).
- **Published selection sensitivity: `{1,2}` approved.** `action_taken == 2` is a price the lender *offered*, uncontaminated by the borrower's accept/decline decision — conditioning on `{1,2}` conditions only on the lender's decision (the conduct under examination), while `{1}` layers borrower-side acceptance selection on top. Reported alongside the primary estimate.
- **Interpretation rule:** if `{1}` and `{1,2}` diverge materially, selection is doing real work and the disclaimer alone is not sufficient — the divergence must be surfaced, not buried. This is the honest, bounded answer to "is conditioning-by-disclaimer enough?" — and it needs no exclusion restriction. *(Resolves CRIT-1 remedy + MED-11: population and controls are one joint decision.)*

## 5. Sample filters (FFIEC-aligned, conventional-only)

Restrict the sample (not regression controls):
- `loan_type == 1` (conventional) — matches the denial engine and the anchor. *(HIGH-6.)*
- `property_type`/derived dwelling: 1–4 unit, site-built (`construction_method == 1`).
- `business_or_commercial_purpose == 2` (non-business); Exempt/1111/NaN → DROP with reason, per existing Filter 9.
- `occupancy_type == 1` and `loan_to_value_ratio ≤ 100` — restored; the skeleton silently omitted both, which the denial engine applies. *(HIGH-6.)*
- `loan_purpose` configurable (home purchase default; refi 31 / cash-out 32 run separately — they calibrate to different anchors, §9).

## 6. Sentinel handling — PER-FIELD table (the CRIT-2 rewrite)

The skeleton's single blanket rule ("blank/NA/1111 → exclude, never impute 0") is **wrong for two of the four cost fields** and would silently delete the modal borrower. HMDA cost fields carry **two incompatible zero conventions.** Handling is now **per-field, sourced to each field's Reg C cite, with three distinct states.** *(Resolves CRIT-2 + MED-12.)*

| Field | Reg C cite | blank means | Handling |
|---|---|---|---|
| `rate_spread` | §1003.4(a)(12) | missing (NOT zero — 0 = priced at APOR, a real favorable value) | blank/NA/Exempt → **exclude-with-reason** (`na_rate_spread` / `exempt_rate_spread`); never 0 |
| `discount_points` | §1003.4(a)(19) | **real 0** ("if no points were paid, leave blank") | blank → **`0.0`**; NA → exclude-with-reason; Exempt → exclude-with-reason |
| `lender_credits` | §1003.4(a)(20) | **real 0** ("if no lender credits, leave blank") | blank → **`0.0`**; NA → exclude-with-reason; Exempt → exclude-with-reason |
| `total_loan_costs` | §1003.4(a)(17) | missing (a real 0 is reported as `0`) | blank → exclude-with-reason; `0` → real 0.0 |
| `origination_charges` | §1003.4(a)(18) | missing (a real 0 is reported as `0`) | blank → exclude-with-reason; `0` → real 0.0 |

- **`1111` is never a global sentinel.** It is the partial-exemption code only for the specific fields whose Reg C cite defines it; for `applicant_income` (reported in thousands) `1111` = a real $1,111,000 applicant and must NOT be dropped. *(MED-12 — same 1111 hazard the hmda-analyzer CRA-proxy cycle already caught; portfolio-recurring.)*
- **`Exempt`** (EGRRCPA partial exemption, encoded per FIG — exact literal encoding a `[BUILD-RECON]` item) → excluded-with-reason, never coerced to a number.
- **TDD requirement:** one sentinel mutation test **per field per state** (real-0 / NA / Exempt), not one generic test. Each mutation must bite.

## 7. Controls & the exact regression equation (MED-1: equation == code, no drift)

The estimated model (write the code to build **exactly** these regressors — no more, no less):

```
rate_spread_i = β0
              + β_pc · protected_class_i          # coefficient of interest (bps)
              + β1 · log(loan_amount_i)
              + β2 · combined_LTV_i
              + Σ β · DTI_bin_i                     # categorical, §1003.4(a)(23) encoding
              + β3 · log(property_value_i)
              + β4 · log(applicant_income_i)
              + Σ β · lien_status_i                 # dummies
              + Σ β · occupancy_type_i              # (occ==1 filtered, so only if variation remains)
              + β5 · loan_term_i
              + β6 · intro_rate_period_i            # / rate_type where applicable
              + β7 · discount_points_i              # see decision below
              + β8 · lender_credits_i               # see decision below
              + Σ β · MSA_i                          # pooled dummies, sparse handling §10
              + ε_i
```
No `loan_type` dummy (conventional-only, §5). MSA FE pooled (not stratified, not multilevel), consistent with the denial engine.

**Points/credits fork — DECIDED (was the §5 open fork):** **include `discount_points` and `lender_credits` as controls,** because omitting them confounds the pricing comparison with the points/rate tradeoff (a borrower who bought points has a mechanically lower spread). This is done **only now that §6 handles their blank-means-zero convention correctly** — the confound-avoidance is worthless if the control silently drops all non-points-payers. Stated bad-control caveat: these are partly borrower-chosen in response to the offered rate (post-treatment risk); the direction is toward **attenuation** of the protected-class coefficient, which is why the calibration band's *lower* bound must catch it (§9). `total_loan_costs`/`origination_charges` are **not** added as controls in v0.3.0 (overlap with points/credits, own missingness) — noted for the second audit.

**`n` reported in every output is the post-exclusion modeled n** (rows actually in the regression), never a pre-NaN-drop count. *(Resolves MED-4.)*

## 8. Inference — cluster-robust SEs (HIGH-3, the strongest objection)

- **Default `cov_type='cluster'`, clustered on `lei`** (lender). Mortgage prices come off lender rate sheets → residuals are strongly correlated within lender (and within lender×MSA). Plain HC1/HC3 correct heteroskedasticity but **not** within-cluster correlation; on 10⁵–10⁶ rows they understate the protected-class SE by a large factor and manufacture significance. The anchor study clusters at the lender level on every table.
- Single-lender screen → cluster on **MSA**.
- **Adequacy rule is CLUSTER COUNT, not observation count `n`.** The small-cluster problem bites below ~`[SET IN AUDIT-2: ~30–50]` clusters — which is exactly where a small-lender or single-MSA screen lives. (Peduzzi EPV is Logit-specific and does not transfer; the OLS replacement is a cluster-count floor, not an R² floor.)
- Below the cluster-count floor → the estimate is reported with a wide-CI / low-power flag and **the lender name is suppressed** (§11).

## 9. Calibration — signed-wedge ledger, not an asserted band (HIGH-4, HIGH-5, MED-10)

**Anchor:** Bartlett, Morse, Stanton, Wallace, *Consumer-Lending Discrimination in the FinTech Era*, JFE 143(1):30–56 (2022) / NBER w25943. Verified: pooled Latinx/African-American coefficient **7.88 bps purchase** (Table 4 Panel A col (1)) / **3.6 bps refi**; credit-score × LTV enter as GSE-grid fixed effects (they control for credit risk); SEs clustered at lender level.

**Two corrections to how the skeleton used it:**
- The anchor's **dependent variable is the note rate, not APR−APOR.** APR embeds fees; if minority borrowers face higher fees (the literature's consistent finding), an APR-based disparity mechanically **exceeds** a note-rate one — a second upward wedge independent of omitted-variable bias. *(HIGH-4.)*
- The anchor **population is conventional-conforming, 30-yr fixed, 2009–2015, and excludes CRA tracts** — NOT "GSE + FHA." The CRA-tract exclusion is the sharpest mismatch for a CRA-adjacent advocacy tool and must be disclosed. *(HIGH-5.)*

**Spec-matched anchor:** the tool's spec (pooled national, MSA FE, **no lender FE**) maps to Bartlett Table 4 Panel A **col (2) ≈ 6.95 bps**, not the headline 7.88. Center the calibration on ~6.95 bps (purchase).

**Signed-wedge ledger** (direction the tool's Black-only public-HMDA coefficient should move vs the spec-matched anchor):

| Wedge | Direction | Note |
|---|---|---|
| Omitted credit score/AUS (public HMDA) | **↑** | controls correlated with race and price are absent (Wooldridge §3.3) |
| APR-embeds-fees vs note rate | **↑** | if minority fees higher, APR disparity > rate disparity |
| Vintage 2009–2015 → 2018+ ("discrimination declining") | **↓** | anchor era had more; tool era should read lower |
| Pooled Latinx+Black → Black-only | **?** | Black-only may differ either way from pooled |
| Anchor excludes CRA tracts; tool includes them | **? (lean ↓)** | CRA incentives in those tracts pull the included-sample disparity down |

Net: two clear ↑, one clear ↓, two ambiguous → expect the tool near-or-above ~7 bps with real uncertainty. **The anomaly to flag is a LOW result** — because the biases the design itself risks (points bad-control, any outlier rewriting) all **attenuate toward zero.** A permissive low floor would wave those through.

**Provisional dev-time bands** `[SET IN AUDIT-2]` — separate per configuration:
- Purchase: flag if the national pooled adjusted Black-vs-White coefficient falls **outside ~4–15 bps** (floor set to catch attenuation, not at 2).
- Refi: separate band centered on the 3.6 bps anchor — do NOT reuse the purchase band (against 3.6, a 4–15 band is nonsensical).

**Band is DEV-TIME engine calibration only, on a national pooled run. It is NEVER a runtime gate on a named lender** — the anchor is a national average; an individual lender can legitimately sit at 40 bps, and wiring a national band to a per-lender check would silence true positives on the worst actors. *(MED-10.)*

## 10. Outliers & sparse MSAs — no silent substitution

- **No winsorizing.** Winsorizing rewrites an observed value with a fabricated boundary — silent substitution, and it attenuates the protected-class coefficient toward a lender-favorable result (protected-class borrowers are over-represented in the upper tail that carries the signal). Extreme values are **excluded-with-reason** (threshold published, count reported alongside the coefficient) or **retained** — never rewritten. *(Resolves MED-8.)*
- **Sparse MSAs are not silently collapsed to reference.** A loan in a 7-obs MSA modeled as reference has its geography **reassigned**, not classified or excluded — and the reconciliation identity does not catch reassignment. Either report the reassigned count as a first-class output line, or exclude-with-reason (`sparse_msa`). *(Resolves MED-9.)*

## 11. Reconciliation identity (extended)

`classified + excluded + reassigned == universe`, exact, with every excluded row reason-keyed and every reassigned row counted. Reason vocabulary: `na_rate_spread`, `exempt_rate_spread`, `na_discount_points`, `na_lender_credits`, `missing_total_loan_costs`, `open_end_excluded`, `reverse_mortgage_excluded`, `sparse_msa`, `out_of_range_*`, … No silent drops; no silent reassignments. *(Extends the identity per MED-9 so reassignment can't hide inside a passing check.)*

## 12. Interpretation, language, lender-name suppression

- Coefficient reported as **adjusted pricing disparity in basis points** — "a statistically significant adjusted pricing disparity of X bps for [group] vs [group]." Never "discrimination," never "overcharging."
- Paired always with "This is a screening signal, not a finding of discrimination."
- **Three-location conditional disclaimer** (report render, `.limitations[-1]`, `.interpretation`), significant/non-significant variants; non-significant variant states absence of significance ≠ absence of disparity. Plus the **selection caveat** (§4) and the **within-year lock-timing caveat** (§3), bound to the metric/table, not a strippable footer.
- **Lender-name suppression** — suppress the lender name in headline/interpretation unless ALL hold:
  - cluster count ≥ the §8 floor `[SET IN AUDIT-2]`,
  - the protected-class **CI excludes zero AND CI width** is below `[SET IN AUDIT-2]` (precision, not just a point p-value),
  - every FFIEC-standard price control present,
  - model well-conditioned (condition number below `[SET IN AUDIT-2]`; multicollinearity gate),
  - sample ≥ min.
  - **Replaces the pseudo-R² floor** — R² does not transfer: a pricing OLS with MSA FE shows high R² driven by geography/rate-environment while the protected-class coefficient may be hopelessly imprecise. Fit is not the risk; **precision** is. And the bare `p > 0.05` limb is untrustworthy until SEs cluster (§8).

## 13. Limitations (documented in 3+ places; corrected)

Carry all denial-engine limitations (no credit score, no AUS, no assets/reserves, no co-applicant score, no appraisal/override/employment/tradeline data) PLUS pricing-specific:
- **Conditional on origination** — the `{1}` estimate conditions on both lender approval and borrower acceptance; the `{1,2}` sensitivity isolates the lender decision (§4).
- **Anchor is a different quantity and population** — note rate vs APR−APOR (fee wedge, §9), and 2009–2015 conventional-conforming excluding CRA tracts (§9). The calibration is order-of-magnitude, not a tight band.
- **Within-year lock-timing** variation not fully removed by APOR-matching (§3).
- Points/credits are partly borrower-chosen (bad-control caveat, §7).
- ~~"No note rate"~~ **DELETED — false; `interest_rate` is in the LAR.** *(HIGH-7.)*

## 14. Citations (to verify verbatim in the full-doc pass)

FFIEC Interagency Fair Lending Examination Procedures (pricing); 12 CFR §1026.35 (HPML thresholds, verified current); §1003.4(a)(12) rate_spread; §1003.4(a)(17)–(20) cost fields (verified zero conventions); §1003.4(a)(21) interest_rate; §1003.4(a)(23) DTI binning; Reg C commentary 4(a)(12)-7/-8; Bartlett et al. JFE 143(1):30–56 (2022); Wooldridge §3.3 (OVB); Greene §17 (OLS/robust inference); ECOA/Reg B pricing. Cite fair-lending/CRA rules **neutrally** — do not label an enjoined/rescinded rule "current."

## 15. Open items carried to Audit-2 / build-recon

- `[BUILD-RECON]` exact FIG literal encoding of `Exempt` per cost field; confirm `rate_spread` LAR dtype (string vs numeric) and the real-0-vs-blank representation in the public CSV.
- `[SET IN AUDIT-2]` cluster-count floor; purchase & refi band bounds; CI-width and condition-number thresholds for suppression.
- Second audit should pressure-test: the include-points decision (§7) for residual bad-control bias; whether `{1,2}` selection sensitivity is sufficient or whether the `{2}`-only quoted-price population deserves its own report; the col-(2) spec-match claim against the actual paper table.

---

### Gate from here
Full methodology (this doc) → **second fresh-session hostile audit** → resolve → build (TDD, per-field sentinel mutations bite) → fresh code audit → fix → ship → settle. Does not jump the current waterfall-py settle window (authoring + audit are neither code nor outreach).
