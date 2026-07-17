# Rate-Channel (APR-Spread) Disparity Methodology — fair-lending-screener v0.3.0 (v5)

**Status:** Draft v5, resolving Audit-4. Supersedes v4. **Major scope change (Jay): lender-naming is OUT of v0.3.0** — the tool reports a **market-level** adjusted rate-channel disparity as a screening signal and **names no lender.** This dissolves CRIT-4 (no lender-level estimand needed), most of HIGH-1 (no N-lender multiple testing), and HIGH-3-as-a-naming-gate. Bartlett §9 rewritten on the **verified** accepted-manuscript facts (Audit-4 CRIT-1 upheld; see `AUDIT-4-TRIAGE.md` + the retraction in `BARTLETT-DIRECT-READ.md`).

**Naming/label change (Audit-4 ruling 6):** the output is **"rate-channel (APR-spread) disparity,"** never "pricing disparity" — the fee/points channel is not examined (§3/§7), and an advocate must not read "not significant" as "the lender doesn't price-discriminate."

**Scope locked:** conventional-only; 2018+; continuous rate_spread; `{1}` primary + `{1,2}` inclusion diagnostic; **market-level, no lender named**; uncalibrated + disclosed; costs-as-outcome scoped out.

---

## 1. Purpose & firewall placement
Regression-adjusted **market-level rate-channel (APR-spread) disparity** — whether, in a given sample/market, a protected-class group receives a higher `rate_spread` (APR−APOR) after controlling for legitimate rate drivers. Reported as a **screening signal about the market, never a finding of discrimination and never an attribution to any lender.** Inferential → fair-lending-screener, not hmda-analyzer. Screener never named in general-audience/Lara contexts.

**What this tool does NOT do (v0.3.0):** it does not name, rank, or flag individual lenders. A single pooled coefficient is a **market average** that conflates within-lender pricing differences with between-lender sorting (borrowers of different groups using different lenders); it cannot identify any firm's conduct, and the tool does not claim to (§13). Lender-level identification (lender FE + interaction, FDR, OVB gating) is deferred to a later version.

## 2. Scope
**In:** conventional (`loan_type == 1`), closed-end, 1–4 unit site-built non-business mortgages, 2018+; continuous rate_spread; one market-level protected-class coefficient in bps.
**Out:** lender-level identification/naming (deferred); government-backed loans; HPML binary; Heckman; **reverse mortgages & open-end lines (now explicitly filtered, §5)**; credit-score imputation; BISG; Section 1071; **loan-cost/points disparity as an outcome** (scoped out; the fee channel is under-captured — a stated limitation, §13).

## 3. Outcome variable
- Continuous `rate_spread` (APR−APOR; §1003.4(a)(12)). Do not recompute APOR. OLS with cluster-robust SEs (§8).
- **Why rate_spread not the note rate** (`interest_rate` is in the LAR): no month/day date in the public LAR → within-year rate environment not absorbable by time FE; rate_spread is APOR-matched at the rate-set date. Residual limitation: within-year lock-timing variation remains (§13).
- **The fee/points channel is UNDER-captured** (not netted out): APOR is points-inclusive (§1026.35(a)(2), verified), and the APR amortizes points over the full term while loans prepay in ~7 years, so rate_spread **dampens** the fee channel. This is why the output is labeled **rate-channel** disparity and costs-as-outcome is a stated-limitation scope-out (§7, §13), not a silent omission.

## 4. Population — primary + inclusion diagnostic
`rate_spread` reported for `action_taken` 1 **and** 2 (Cmt 4(a)(12)-7; -8).
- **Primary: `{1}` originated.**
- **`{1,2}` action-2 inclusion diagnostic** (renamed from "selection sensitivity" — Audit-4 ruling 8: no decision follows from it, so it is a diagnostic, not a sensitivity). All §7 regressors are application-side by CFR text ((a)(7) "or the amount applied for"; (a)(28) "proposed to secure"; (a)(26) "proposed number of months in the case of an application"; (a)(23)/(a)(24) "relied on in making the credit decision"), so action-2 rows are usable.
- **Measurement caveat (verified):** action-2 rate_spread derives from the **Loan Estimate** APR (Cmt 4(a)(12)-8 → 1026.18/1026.37); action-1 from the **Closing Disclosure** APR (Cmt 4(a)(12)-**3** → 1026.18/1026.38). A `{1}` vs `{1,2}` divergence therefore reflects **selection AND/OR LE-vs-CD measurement drift — attributable to neither alone.** Report both; surface divergence unattributed. **`[BUILD-RECON: report the action-2 row share; if small, {1,2} has little diagnostic power — disclose it.]`**
- Non-degeneracy guard: `< min` per-group after exclusions → `InsufficientGroupSizeError`.

## 5. Sample filters
- `loan_type == 1` (conventional).
- **2018+ as row-level reason-coded exclusion** (`pre_2018_excluded`), surfaced & reconciled (not a silent filter, not a bare raise). Pre-2018 rate_spread was reported only if ≥ 1.5/3.5 pp (2017 CFR §203.4(a)(12)(i), "equal to or greater than") and **only for originations** (no action-2 pre-2018).
- **`open_end_line_of_credit == 2` and `reverse_mortgage == 2`** (Audit-4 MED-1). Reverse self-drops (rate_spread NA), but **HELOCs carry a real comparable-transaction rate_spread** (Cmt 4(a)(12)-3/-4) and would otherwise import differently-constructed values — the pricing analogue of the signature failure. Both are (a)(36)/(a)(37), exempt-eligible under (d)(1)(iii) → Exempt paths too.
- 1–4 unit, `construction_method == 1`, `business_or_commercial_purpose == 2` (Exempt/1111/NaN → DROP), `occupancy_type == 1`, `combined_loan_to_value_ratio ≤ 100` `[BUILD-RECON: confirm the bound]`.
- `loan_purpose` configurable (home purchase default; refi 31 / cash-out 32 separate).

## 6. Sentinel handling — per-field, EVERY regressor, with precedence

Per-field, three states (real-value / NA / Exempt), each sourced. **A field without a rule is a silent-imputation hazard.**

| Field | Source | Handling |
|---|---|---|
| `derived_race` **(β_pc)** | **FFIEC public-LAR derived field** (derived from §1003.4(a)(10)(i) race + Appendix B; **NOT a CFR data point** — do not cite (a)(5), which is construction method and collides with the §5 `construction_method` filter) | **Black or African American** → group (=1 default); **White** → reference (=0); **Race Not Available / Free Form Text Only** → exclude `na_race` (**never into reference**); **Joint** → exclude `joint_race`; **2+ minority races** → exclude `multiminority_race`; other single minority races → outside default comparison (configurable). Values per FFIEC LAR data-fields doc. Ethnicity separate. *(Fixes CRIT-3.)* |
| `rate_spread` | (a)(12) | blank/NA/Exempt → exclude (`na_rate_spread`/`exempt_rate_spread`); never 0 |
| `intro_rate_period` → `is_arm` | (a)(26); Cmt 4(a)(26)-2, -3 | **per-LEI reportability test (Audit-4 ruling 7):** if an LEI-year ever reports a non-NA intro_rate_period → it reports (a)(26), so its NA rows are genuine not-applicable → `is_arm=0`. If an LEI reports **NA on ~100%** of rows (≥ min count) → plausibly omitting (a)(26) à la carte (§1003.3(d)(4)) → exclude its rows `intro_rate_period_unreportable_lei`. Real positive integer → `is_arm=1`; Exempt → exclude. **Also NA for preferred-rate loans** whose rate can change (Cmt 4(a)(26)-2) — a third NA cause; handled by the same per-LEI test (a preferred-rate lender still reports non-NA on true ARMs). |
| `combined_loan_to_value_ratio` | (a)(24) | NA/Exempt → exclude |
| `debt_to_income_ratio` | (a)(23) | **binned Alphanumeric public-file construct — CATEGORICAL, forbid numeric coercion** (coercion deletes the tail bins). NA/Exempt → exclude. `[BUILD-RECON: exact bin labels — FFIEC page shows "Varying values".]` |
| `property_value` | (a)(28) | NA/Exempt → exclude; log guard |
| `income` | (a)(10) — **always-required, no Exempt path** ((a)(10) not in (d)(1)(iii)) | `1111` = real $1.111M, **not a sentinel**; NA → exclude; log guard |
| `loan_amount` | (a)(7) — always-required | log guard |
| `loan_term` | (a)(25) | NA/Exempt → exclude |
| `lien_status` | **(a)(14) — always-required, NO Exempt state** ((a)(14) not in (d)(4)(ii) or (d)(1)(iii)) | required regressor; no Exempt path (states the rule, not just the v3→v4 correction — MED-3) |
| `derived_msa-md` (MSA FE) | FFIEC derived | `[BUILD-RECON: no documented sentinel ("Varying values") — confirm non-metro/blank encoding before use.]` |

- **Reason-code precedence (Audit-4 MED-2):** a partially-exempt row (§1003.3(d)(2)) lacks *all* optional data at once → many codes apply. **Deterministic first-wins order** (outcome-defining first): `pre_2018_excluded` → `reverse_mortgage_excluded`/`open_end_excluded` → `na_race`/`joint_race`/`multiminority_race` → `na_rate_spread`/`exempt_rate_spread` → then remaining regressor NAs in fixed order. The reconciliation test asserts **exactly one** code per excluded row.
- `1111` never a global sentinel. log() domain guard: income/loan_amount/property_value ≤ 0 or non-finite → `out_of_range_*`.
- **TDD:** one sentinel mutation test per field per state; each bites.

## 7. Controls & exact equation (market-level; no lender FE by scope)

```
rate_spread_i = β0 + β_pc·protected_class_i
              + β1·log(loan_amount_i) + β2·combined_LTV_i + Σβ·DTI_bin_i
              + β3·log(property_value_i) + β4·log(income_i)
              + Σβ·lien_status_i + β5·loan_term_i + β6·is_arm_i    # is_arm per §6; dropped if a run has no reportable LEI
              + Σβ·MSA_i + ε_i
```
- **β_pc is a MARKET-LEVEL coefficient** — no lender FE, because v0.3.0 names no lender (so a within-lender estimand is not required). Its market-average nature (incl. between-lender sorting) is a disclosed limitation (§13), not a defect for a market-level screening signal.
- **No `discount_points`/`lender_credits`** (finance charges inside the APR, §1026.4(b)(3); controlling double-counts). Verified that the rate channel is not a points artifact (accepted-MS Table 10: controlling points *raises* the minority coefficient), so a rate-channel-only tool measures something real — but it is the **rate channel only** (§3, label).
- No `loan_type` dummy. `n` = post-exclusion modeled n (MED-4 carried). Equation == code exactly (MED-1 carried).

## 8. Inference — cluster-robust SEs, effective clusters
- `cov_type='cluster'` on `lei` (correct SEs for the market-level estimate given rate-sheet correlation). Single-cluster degenerate → error.
- **Adequacy = effective cluster count `G_eff`** = inverse-Herfindahl of cluster sizes (Carter–Schnepel–Steigerwald `[verify ref]`), NOT nominal count. **`G_eff ≥ 30`** for asymptotic cluster-robust CIs `[SET/verify]`; **10 ≤ G_eff < 30** → wild-cluster bootstrap-t (Webb weights, null imposed, B=9999) `[verify ref]`; **G_eff < 10** → report point estimate flagged "cannot be reliably inferred," no significance claim.
- Condition number computed on the **partialled-out design** (after absorbing FE), not raw (raw is dominated by the MSA-FE block and fires mechanically). `[SET: κ flag/suppress thresholds — verify Belsley–Kuh–Welsch.]`

## 9. Engine validation — UNCALIBRATED + DISCLOSED (Bartlett read correctly this time)

**The tool asserts no expected coefficient magnitude.** Grounded in the corrected direct read (`BARTLETT-DIRECT-READ.md` retraction + `AUDIT-4-TRIAGE.md`).

**Honest characterization of the closest published analog.** Bartlett et al.'s accepted manuscript **Table 10** ("Interest-rate differentials: 2018/2019 HMDA data controlling for points paid/total loan costs") **is a close analog** — it shares the tool's **era (2018/2019), data source (public HMDA), and credit-score handicap** (fn31, verbatim: "the HMDA data do not include individual credit scores," using census-tract credit-score deciles + individual income instead). The earlier "no study shares this design" framing was false and is withdrawn.

**Why uncalibrated still holds — on the surviving, verified wedges (not the broken ones):**
- **Outcome:** Table 10's DV is the **note interest rate in basis points**; the tool's is **APR−APOR (rate spread)**. Different quantity (APR embeds fees; spread is benchmark-relative). No valid magnitude mapping.
- **Controls/FE:** Table 10 **controls for points** and uses **lender×year FE**; the tool controls neither points (by design, §7) nor lender (by scope, §7). A number produced under different controls is not a target.
- **Group:** Table 10 pools Latinx+Black; tool default is Black-only (config).
- **Directional context only (not a target, never beside a result):** Table 10's minority coefficients are single-digit-to-low-double-digit bps on the note rate — enough to say the tool's output should be *order-of-magnitude* small, not enough to calibrate. A tool coefficient of, say, 300 bps is a spec/data error; 8 bps vs 15 bps is not adjudicable against Table 10 because the outcomes differ.

**What replaces calibration — synthetic-recovery engine validation** (tests the estimator, not the world; disjoint from calibration):
- Generator plants a **lender random effect + Herfindahl-heavy imbalance**; verify the cluster-robust estimator recovers planted δ (incl. δ=0 at nominal rate); include an **HC1 negative control that MUST over-reject** (so a build silently dropping `cov_type='cluster'` fails).
- **OVB is the error the design actually has, and it is reported, not gated:** synthetic recovery cannot detect it. Report an **Oster (2019) δ-style OVB sensitivity** `[verify ref]` alongside every estimate — how strong selection on unobservables (e.g. the absent credit score) must be, relative to observables, to zero the coefficient — and **flag the estimate as "not robust to plausible unobservable selection" if δ < 1.** This is a disclosed diagnostic on a market-level signal, not a lender gate.
- **Anchor-free plausibility tripwire** (Audit-4 ruling 5): `|β_pc| > 100 bps` OR `> IQR(rate_spread)` in-sample → probable spec/data error. Sanity only, never a fair-lending threshold.
- **Mandatory disclosure** on every output (see §12).

## 10. Outliers & sparse MSAs
- **No winsorizing.** Extremes excluded-with-reason (threshold+count) or retained — never rewritten.
- **Sparse MSAs** → report reassigned count or exclude `sparse_msa`; the identity counts reassignment.

## 11. Reconciliation identity
`classified + excluded + reassigned == universe`, exact, **exactly one reason code per excluded row** (precedence, §6). Vocabulary: `pre_2018_excluded`, `reverse_mortgage_excluded`, `open_end_excluded`, `na_race`, `joint_race`, `multiminority_race`, `na_rate_spread`, `exempt_rate_spread`, `intro_rate_period_unreportable_lei`, `exempt_intro_rate_period`, `na_ltv`, `na_dti`, `na_property_value`, `na_income`, `na_loan_term`, `sparse_msa`, `out_of_range_*`. (`action2_field_unavailable` removed as redundant — Audit-4 LOW-3.)

## 12. Interpretation, language, output (no lender named)
- One **market-level** coefficient in **bps**; "screening signal about the market, not a finding of discrimination, and not attributable to any lender."
- Reported with: CI (cluster-robust or bootstrap per §8), `G_eff`, the **Oster δ OVB sensitivity**, exclusion reconciliation, and the mandatory disclosures.
- **Three-location conditional disclaimer** + these caveats, all metric-bound & non-strippable: market-average/between-lender-sorting (§1/§13); rate-channel-only / fee-under-capture (§3); uncalibrated (§9); OVB-not-robust flag if δ<1 (§9); within-year lock-timing (§3); action-2 measurement drift (§4).
- **Multiplicity (residual HIGH-1):** the tool reports **one estimate per configuration** (purchase/refi × race/ethnicity × loan_purpose). If a caller runs many configurations or MSA subgroups, **disclose the count and apply Benjamini–Hochberg FDR** across the run's family; report adjusted q. (Far smaller surface than lender-naming, but not zero.)
- **No pseudo-R²/bare-p gate; no lender-name suppression** (nothing is named). Adequacy is `G_eff` + condition number + the OVB flag, all *disclosed*, not used to accuse.

## 13. Limitations (3+ places)
All denial-engine limitations, PLUS: **market-average — conflates within-lender pricing with between-lender sorting; identifies no lender** (§1); **rate-channel only — fee/points channel under-captured** (§3/§7); **uncalibrated — Table 10 is a close analog but measures the note rate, not APR-spread** (§9); **OVB undetectable — no credit score in public HMDA; see the reported Oster δ** (§9); conditional on origination + LE-vs-CD measurement drift (§4); within-year lock-timing (§3); 2018+ only (§5).

## 14. Citations (verify verbatim; version-scoped)
§1026.35 (HPML + points-inclusive APOR (a)(2)); §1026.4(b)(3); §1003.4(a)(7)(9)(10)(12)(14)(23)(24)(25)(26)(28)(36)(37); §1003.4(a)(10)(i) + Appendix B + **FFIEC LAR data-fields doc** for `derived_race` (NOT (a)(5)); §1003.4(a)(21) interest_rate; §1003.3(d) partial exemption; Cmt 4(a)(12)-3/-4/-7/-8, 4(a)(26)-2/-3; 2017 CFR §203.4(a)(12)(i); Wooldridge §3.3; Greene §17; **Oster (2019), Cameron–Miller, Webb, Carter–Schnepel–Steigerwald, Belsley–Kuh–Welsch — verify each before the build adopts a threshold.** **Bartlett: cite the accepted manuscript's Table 10 for the analog (directly read); the 2019 WP (w25943) for the note-rate design; never a magnitude target.**
- **⚠ HIGH-2 — resolve OUTSIDE this doc:** the package tagline "the methodology federal examiners use" is **unsourced**. Either cite the FFIEC Interagency Fair Lending Examination Procedures for OLS-on-rate_spread-with-these-controls, or drop/soften the claim. **I have NOT verified what the exam procedures say — do not assert it from the tagline.** Jay's call; largest credibility exposure in the package.

## 15. Open items → Audit-5 / build-recon
- `[SET IN AUDIT-5 / verify]` G_eff floor & bootstrap staging; condition-number thresholds (on partialled design); Oster δ cutoff; plausibility ceiling — **and verify every statistics reference (Oster 2019, Cameron–Miller, Webb, CSS, BKW) before adoption.**
- `[BUILD-RECON]` per-LEI is_arm reportability test; `derived_msa-md` non-metro encoding; DTI bin labels; action-2 row share; each regressor's action-2 availability; `rate_spread` public-CSV dtype.
- **HIGH-2** brand-claim sourcing (Jay, outside methodology).

---
### Gate
v5 → **fifth fresh hostile audit** (attach the doc + the accepted-manuscript PDF + the WP PDF) → resolve → build. Authoring + audit don't break the waterfall-py settle window. Note: scoping lender-naming out has made v5 materially smaller than v4 — the audit surface is now a market-level screening signal, not an accusation engine.
