# fair-lending-screener v0.3.0 — Rate-Spread / Pricing Disparity

## Methodology Document — PRE-AUDIT SKELETON

**Status:** Draft outline for hostile audit OF the methodology. No code exists or should exist until this document reaches GO through a fresh-session hostile audit. This is the highest legal- and methodology-risk feature in the portfolio.

**How to read this:** Every `⚠ DECISION` is an open call the audit must pressure-test. Every `⚠ VERIFY` is a fact that must be confirmed against a primary source *at write time* (CBLR-from-memory lesson — regulatory anchors and published benchmarks get live verification, never asserted from prior knowledge). Nothing here is settled until the audit says so.

---

## 0. Firewall Placement (decide first — everything else depends on it)

- Pricing disparity is **regression-adjusted / inferential**, same side of the firewall as the existing denial-disparity engine. It belongs in **fair-lending-screener**, NOT in hmda-analyzer (descriptive).
- The descriptive counterpart — raw rate-spread distributions with no adjustment, no comparator, no protected-class inference — could live in hmda-analyzer as a future descriptive feature, but that is a **separate decision and separate package**. Do not let pricing analysis blur across the firewall.
- Reaffirm the cdfi-superpowers rule: the screener is **never named** in Lara/Shelterforce or general-audience contexts. Pricing disparity does not change that posture.

## 1. Scope

**In scope**
- Mortgage pricing disparity from public HMDA, regression-adjusted, protected-class coefficient reported as a screening signal.

**Out of scope (state explicitly, with rationale)**
- Section 1071 small-business pricing.
- Reverse mortgages and open-end lines (HELOCs) — priced on different mechanics; exclude.
- ⚠ DECISION: **Heckman / sample-selection correction — OUT for v0.3.0.** Public HMDA has no clean exclusion restriction (instrument) to identify the selection equation; a mis-specified correction is worse than an honestly-disclaimed conditional estimate. Recommend disclaim-not-correct (§4). Audit must confirm the disclaimer is sufficient given the tool's "examiner methodology" tagline.
- Credit-score imputation, BISG (self-report available under Reg C), AUS reconstruction — all remain out, same as denial engine.

## 2. Outcome Variable

- **Primary: continuous `rate_spread`** (APR − APOR, in percentage points), reported by the lender. CFPB has already computed the APOR comparison — do NOT recompute APOR.
- ⚠ DECISION: **Model form flips from Logit to OLS.** Continuous outcome → `statsmodels.api.OLS` with heteroskedasticity-robust (HC1/HC3) standard errors. Keep statsmodels (p-values, CIs, diagnostics out of the box; no black-box ML; court-defensible). This is a genuine engine change — the existing codebase is Logit-only.
- ⚠ DECISION: **Secondary (optional) binary cut — priced as HPML (higher-priced mortgage loan).** Logit on "spread ≥ HPML threshold," which reuses the existing Logit machinery and disclaimer stack. Decide whether v0.3.0 ships continuous-only or continuous + HPML-binary. Recommend continuous primary; HPML binary only if it doesn't expand the audit surface unacceptably.
- ✅ VERIFIED (eCFR / CFPB, checked July 14 2026): HPML thresholds are **current and unchanged** — first-lien conforming APR ≥ **1.5 pp** over APOR; first-lien **jumbo ≥ 2.5 pp**; **subordinate-lien ≥ 3.5 pp** (12 CFR §1026.35). The annual figure that moves is the small-creditor asset threshold ($2,785,000,000 for 2026) and the appraisal-exemption threshold — NOT the rate triggers. HOEPA (§1026.32) high-cost trigger (~6.5 pp first-lien over APOR) was NOT re-verified live and is not the binary cut anyway — if a HOEPA reference is cited, verify it separately at write time.

## 3. Population / Conditioning — THE load-bearing hazard

- Price is observed **only for originated loans.** Denied applicants have no rate_spread. Every pricing model is therefore **conditional on origination.**
- This means a protected-class pricing coefficient conflates *pricing* differences with *selection into origination* differences. This is the single point the audit will hit hardest.
- ⚠ DECISION: v0.3.0 **conditions on origination and discloses the selection caveat as a hard-bound limitation** (not a correctable defect). The caveat travels with the metric and every table (strippable-caveat HIGH pattern from the CRA-proxy cycle — bind it to the number, not a footer).
- Base population: `action_taken == 1` (originated) only. Note this is a deliberate departure from the denial engine's {1,3} — document why.
- ✅ VERIFIED (FFIEC FIG, July 14 2026) — reinforces this decision: `rate_spread` is reported as **"NA" for any action other than *loan originated*.** NA is therefore **definitionally a non-origination marker**, not a generic missing value. The field only exists for originations — which is the structural reason price is unobserved for denials and the conditioning-on-origination hazard is unavoidable, not a modeling choice. On an originations-only population, NA should be near-absent; any residual NA/Exempt is a genuine partial-exemption or data-quality case (see §4).
- Same FFIEC-aligned sample filters as denial: property_type == 1, construction_method == 1, business_or_commercial_purpose == 2 (Exempt/1111/NaN → DROP, per existing Filter 9 policy). loan_purpose configurable (home purchase default; refi 31 / cash-out 32 separate).

## 4. Sentinel & Fabrication-Path Pre-emption (portfolio signature — enumerate before code)

- `rate_spread` **NA / "Exempt" / 1111 / blank → EXCLUDE with a labeled reason, NEVER impute 0.** A spread of 0 means "priced at APOR" — a real, favorable value. Imputing 0 for missing fabricates good pricing and dilutes disparity. This is the pricing analogue of the CRA-proxy divide-by-zero-fabricates-Upper bug.
  - ✅ VERIFIED distinction (FFIEC FIG): among originations, a residual **NA is genuine missing data** while a real **`0.0` spread = priced exactly at APOR** (a favorable value). These two must never collapse to the same value — the whole no-impute-0 rule rests on keeping them distinct. Note NA-in-rate_spread on a supposedly originations-only frame is itself a data-quality signal worth surfacing, not silently dropping.
  - "Exempt" arises under the EGRRCPA partial exemption (low-volume depositories/credit unions); FIG encodes it with a leading capital **"E"**. Treat as excluded-with-reason (`exempt_rate_spread`), never coerced to a number.
- Reverse-mortgage / HELOC / non-reportable rows → exclude before modeling, reason-labeled.
- Every excluded row surfaces with a reason key (mirror the hmda-analyzer vocabulary: `na_rate_spread`, `exempt_rate_spread`, `open_end_excluded`, `reverse_mortgage_excluded`, `missing_price_control`, …); classified + excluded == universe, exact reconciliation, no silent drops.
- ⚠ Address deferred **MED-4** here: n reported in output must be the **post-exclusion modeled n**, not a pre-NaN-drop count. The pricing rewrite touches this surface — fix it in-cycle.

## 5. Controls (pricing is driven by different factors than denial)

Legitimate price drivers that MUST be controlled to isolate the protected-class effect:
- log(loan_amount), combined LTV, DTI bins (12 CFR §1003.4(a)(23) encoding), log(property_value), log(applicant_income)
- loan_type dummies (FHA/VA/USDA/conventional price differently), lien_status, occupancy_type
- loan_term, introductory_rate_period / rate_type (amortization features), loan_purpose
- **⚠ DECISION — discount_points, lender_credits, origination_charges, total_loan_costs.** HMDA reports these. Borrowers who buy points get a lower rate → lower spread. Failing to control confounds pricing with the points/credits tradeoff. BUT these fields carry their own NA/Exempt sentinels and are themselves outcomes of the transaction (post-treatment / "bad control" risk — controlling for a variable the borrower chose partly in response to the offered rate can bias the estimate). This is a genuine methodological fork the audit must resolve: include (risk bad-control bias) vs exclude (risk points-confounding). Document the choice and its direction of bias explicitly.
- MSA fixed effects (pooled dummies, <30-obs MSAs → reference), same as denial engine.
- ⚠ Address deferred **MED-1** here: the methodology equation must list exactly the variables the code creates — no equation/implementation drift. The pricing rewrite is the moment to close this.

## 6. Calibration Anchor (do NOT ship uncalibrated)

- Denial engine calibrates to The Markup's ~1.8× OR. Pricing needs its own **published, verified** benchmark with a tolerance band.
- ✅ VERIFIED ANCHOR (Bartlett, Morse, Stanton, Wallace, *Consumer-Lending Discrimination in the FinTech Era*, **Journal of Financial Economics 143(1):30–56, 2022**; NBER w25943 — checked July 14 2026): risk-equivalent minority borrowers are charged **7.9 bps more on purchase mortgages and 3.6 bps more on refinance mortgages.** Use **~7.9 bps (purchase)** as the primary anchor; **3.6 bps** for the refi configuration.
- ⚠ THREE calibration caveats the audit must see (the anchor is directional/order-of-magnitude, NOT a tight tolerance band like denial's 1.6–2.2×):
  1. **Group mismatch.** Bartlett pools **Latinx + Black** vs White. The screener's default protected class is **Black vs White with ethnicity analyzed separately**. The anchor group ≠ the tool's default group — calibrate order-of-magnitude, and expect the Black-only coefficient to differ from the pooled 7.9 bps.
  2. **Bartlett had credit-score access; the tool does not.** Their identification uses the **GSE risk grid (LTV + credit score)** to define "risk-equivalent" — i.e. they *control for* credit score. Public HMDA strips it. So the tool's coefficient carries the **same upward omitted-variable bias** as the denial engine (Wooldridge §3.3) and should be expected to run **higher than 7.9 bps.** Band is asymmetric upward for the same reason as denial.
  3. **Population/product mismatch.** Bartlett is GSE-securitized + FHA, risk-equivalent design; the screener is pooled HMDA with FFIEC filters. Treat 7.9 bps as an order-of-magnitude sanity anchor (single-digit-to-low-double-digit bps is plausible; a 100+ bps adjusted coefficient signals a spec error), not a pass/fail band.
- Recommend a **wide order-of-magnitude tolerance** (e.g. flag if the adjusted Black-vs-White purchase coefficient falls outside ~2–25 bps — the audit sets the exact bounds), NOT a narrow multiplicative band. Justify the bounds against the anchor + the three caveats.

## 7. Interpretation & Language Guardrails (reuse, adapted)

- Coefficient reported as **adjusted pricing disparity in basis points** ("a statistically significant adjusted pricing disparity of X bps for [group] vs [group]"). NEVER "discrimination," NEVER "overcharging."
- Paired always with "This is a screening signal, not a finding of discrimination."
- **Three-location conditional disclaimer** (report render, `.limitations[-1]`, `.interpretation`), significant vs non-significant variants; non-significant variant states absence of significance ≠ absence of disparity. Add the pricing-specific **selection caveat** (§3) to the stack so it can't be stripped.
- **Lender-name suppression** extends to pricing: suppress name in headline/interpretation when n < min, p > 0.05, model non-convergence/ill-conditioned, any FFIEC-standard price control excluded, OR R² below floor. ⚠ DECISION: OLS diagnostic gate — replace pseudo-R²<0.05 with an OLS-appropriate fit/condition check (adjusted R², condition number for multicollinearity). Define the floor.

## 8. Statistical Validity Checklist (OLS-specific — new relative to Logit engine)

- Heteroskedasticity-robust SEs (HC1 or HC3) as default — state which and why.
- Outlier / topcoding policy for extreme rate_spread values — exclude or winsorize? ⚠ DECISION; never silently.
- Multicollinearity among price controls (condition number / VIF gate feeding the suppression rule).
- Minimum sample and minimum per-group observation counts (Peduzzi EPV is Logit-specific and does NOT transfer to OLS — state the OLS-appropriate adequacy rule instead; addresses the InsufficientGroupSizeError zero-test gap, deferred LOW-NEW-3).
- Provenance dict includes data_year, model form, SE type, controls, exclusion tallies — reproducibility.

## 9. Limitations (documented in 3+ places, per house rule)

Carry all denial-engine limitations (no credit score, no AUS, no assets/reserves, no co-applicant score, no appraisal/override/employment/tradeline data) PLUS pricing-specific:
- **Conditional on origination — selection caveat** (§3), stated as the primary interpretive limit.
- Points/credits control decision and its bias direction (§5).
- rate_spread reflects lender-reported APR−APOR at lock; timing/lock-date effects only partially normalized.
- No note rate, no fees breakdown beyond HMDA-reported cost fields, no rate-lock or concession data.

## 10. Regulatory / Citation Status (verify neutrally, at write time)

- Cite the fair-lending framework and pricing rules neutrally; do not label an enjoined/rescinded rule "current" (the 2023 CRA-rule lesson). ⚠ VERIFY current status of any pricing-related rule cited.
- Anchor citations to verify verbatim: 12 CFR §1026.35 (HPML), §1026.32 (HOEPA), §1003.4(a) HMDA fields including rate_spread, ECOA/Reg B pricing, FFIEC Interagency Fair Lending Examination Procedures (pricing section).

---

## Gate sequence from here (unchanged house discipline)

1. Fill this skeleton into a full methodology.md — every ⚠ resolved, every number verified against a primary source in-session.
2. **Fresh-session hostile audit OF the methodology document.** No code.
3. Revise to GO.
4. Only then: build (TDD, negative-case-first, sentinel mutations bite) → fresh hostile code audit → fix → ship → settle.
5. Do not let this jump ahead of the current settle window (waterfall-py 0.2.0). Authoring + methodology audit do not break settle; code and outreach do.

## Audit hotspots (where a hostile reviewer will push hardest)

1. **§3 selection/conditioning** — is disclaim-not-correct defensible for a tool branded as examiner methodology?
2. **§5 points/credits bad-control fork** — either choice has a named bias; the doc must own the direction.
3. **§6 calibration anchor group/access mismatch** — anchor (7.9 bps) is verified but pools Latinx+Black and had credit-score access the tool lacks; using it as a tight band rather than an order-of-magnitude sanity check is the finding.
4. **§4 rate_spread==0 vs missing** — the fabrication analogue; prove the code can't impute 0.
5. **§2 OLS switch** — diagnostics, SEs, and suppression rules that were Logit-specific must be re-derived, not copied.
