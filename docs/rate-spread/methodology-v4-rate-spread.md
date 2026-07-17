# Rate-Spread / Pricing Disparity Methodology — fair-lending-screener v0.3.0 (v4)

**Status:** Draft v4-final, resolving all Audit-3 findings. Supersedes v3. **§9 and §12 are now CLOSED** — Bartlett was read directly from the actual PDF (`BARTLETT-DIRECT-READ.md`); §9 is finalized uncalibrated on verified wedges, §12's CI-width is severed from Bartlett. Ready for Audit-4.

**On the anchor saga:** the calibration material fabricated in all three prior rounds because of a **two-versions problem** no one diagnosed — the drafting described the 2019 working paper while citing the published JFE; the audits mixed versions (Audit-3's CRIT-1 "excludes CRA/FHA is false" is itself false against the working paper, which excludes both). Resolved by reading the actual PDF. The uploaded file is NBER w25943 (2019 working paper); the published JFE differs ($450M, adds FHA) but the design wedges that make it non-anchorable are version-independent (§9).

**Scope (unchanged):** conventional-only; 2018+; continuous rate_spread; `{1}` primary + `{1,2}` reduced-control sensitivity; uncalibrated-and-disclosed (final justification pending §9 read).

---

## 1. Purpose & firewall placement
Regression-adjusted pricing disparity on continuous `rate_spread` (APR−APOR), reported as a **screening signal, never a finding of discrimination.** Inferential → belongs here, not hmda-analyzer. Screener never named in general-audience/Lara contexts. (Ruled clean all three audits.)

## 2. Scope
**In:** conventional (`loan_type == 1`), closed-end, 1–4 unit site-built non-business mortgages, 2018+; continuous rate_spread, protected-class coefficient in bps.
**Out:** government-backed (separate config later); HPML binary; Heckman; reverse/open-end; credit-score imputation; BISG; Section 1071; **loan-cost/points disparity as an outcome** (explicitly scoped out — see §7; a real analysis, deferred, with the limitation stated loudly).

## 3. Outcome variable
- Continuous `rate_spread` (APR−APOR; §1003.4(a)(12)). Do not recompute APOR.
- **OLS** with cluster-robust SEs (§8). Second regression path (not a Logit reuse).
- **Why rate_spread, not the note rate** (`interest_rate` IS in the LAR): no month/day date in the public LAR (only `activity_year`) → within-year rate environment not absorbable by time FE; rate_spread is APOR-matched at the rate-set date before that date was stripped. Keep. Residual limitation: within-year lock-timing variation remains (§13).
- **The points/fee channel is UNDER-captured, not netted out** (Audit-3 correction — the v3 "net-of-points" framing was backwards):
  - APOR is itself **points-inclusive** (§1026.35(a)(2)), and
  - the APR amortizes points over the full loan term while loans prepay in ~7 years,
  so `rate_spread` **dampens** the fee channel rather than capturing it. A group difference in points/fees (the cited literature finds minority borrowers pay more in points *conditional on rate*) is only partially reflected in the spread. This is a stated **limitation** (§13), not something the outcome resolves — and it is the reason costs-as-an-outcome is a real future analysis, scoped out of v0.3.0 explicitly rather than silently.

## 4. Population — primary + reduced-control sensitivity (measurement drift disclosed)
`rate_spread` reported for `action_taken` 1 **and** 2 (Cmt 4(a)(12)-7/-8).
- **Primary: `{1}` originated.**
- **Sensitivity: `{1,2}` reduced-control.** All §7 regressors are **application-side by CFR text**, so action-2 rows are usable and `{1,2}` does not collapse: `(a)(7)` "or the amount applied for"; `(a)(28)` "proposed to secure"; `(a)(26)` "proposed number of months in the case of an application"; `(a)(23)`/`(a)(24)` "relied on in making the credit decision" (an approved application has one). *(Closes the v3 BUILD-RECON with cites.)*
- **Non-degeneracy guard (restored — was dropped in v3):** if either group has < min per-group observations after exclusions, raise `InsufficientGroupSizeError`; never fit a degenerate design.
- **Interpretation rule (corrected — measurement drift):** action-2 `rate_spread` is computed from the **Loan Estimate** APR; action-1 from the **Closing Disclosure** APR (Cmt 4(a)(12)-8). A `{1}` vs `{1,2}` divergence therefore reflects **selection AND/OR LE-vs-CD APR measurement drift — it is NOT attributable to selection alone.** (v2 manufactured a false negative here; v3 a false positive with a causal label. This is the corrected framing.) Report both estimates; surface divergence with both possible causes; do not label it "selection is doing real work."

## 5. Sample filters
- `loan_type == 1` (conventional).
- **2018+ handling — row-level exclusion, reason-coded (NOT a silent filter, NOT a bare raise).** Pre-2018 `rate_spread` was reported only if the spread exceeded 1.5/3.5 pp (govinfo 2017 CFR §203.4(a)(12)(i), verbatim), so a pre-2018 blank is a real below-threshold value. Pre-2018 rows → **exclude-with-reason `pre_2018_excluded`**, counted and surfaced in the reconciliation and output (a large pre-2018 share triggers a summary note). This makes §5 and §11 consistent — the reason code exists because the exclusion is row-level and visible, not a silent drop. *(Resolves the §5-vs-§11 contradiction.)*
- 1–4 unit, `construction_method == 1`, `business_or_commercial_purpose == 2` (Exempt/1111/NaN → DROP), `occupancy_type == 1`.
- **`combined_loan_to_value_ratio ≤ 100`** — corrected field name; the public LAR has no bare `loan_to_value_ratio`, the CLTV field is `(a)(24)`. `[BUILD-RECON: confirm ≤100 is the intended bound on CLTV (values >100 occur legitimately); mirror the denial engine's choice.]`
- `loan_purpose` configurable (home purchase default; refi 31 / cash-out 32 separate).

## 6. Sentinel handling — per-field, EVERY regressor incl. the outcome-of-interest driver

Per-field, three states (real-value / NA=not-applicable / Exempt=partial-exemption), each sourced to the field's cite. **A field without a rule is a silent-imputation hazard.**

| Field | Cite | Handling |
|---|---|---|
| `derived_race` **(protected class — β_pc)** | (a)(5) | **Black or African American** → analyzed group (=1 default); **White** → reference (=0); **Race Not Available / Free Form Text Only** → exclude-with-reason `na_race` (**NEVER into the reference group** — silent White-reference assignment biases β_pc by construction); **Joint** → exclude-with-reason `joint_race`; **2+ minority races** → exclude-with-reason `multiminority_race`; other single minority races → outside the default Black-vs-White comparison (configurable). Ethnicity (Hispanic/Latino) analyzed separately, never blended. *(Resolves CRIT-3 — the coefficient of interest was ungoverned.)* |
| `rate_spread` | (a)(12) | blank/NA/Exempt → exclude-with-reason (`na_rate_spread`/`exempt_rate_spread`); **never 0** (0 = priced at APOR, real favorable) |
| `intro_rate_period` → `is_arm` | (a)(26) | real positive integer → ARM (`is_arm=1`); **Exempt** (à-la-carte partial exemption) → exclude-with-reason `exempt_intro_rate_period` (cannot determine); **NA (not-applicable)** → fixed (`is_arm=0`) ONLY IF `[BUILD-RECON]` confirms the public file encodes not-applicable **distinctly** from a partial-exemption omission. **If they are not distinguishable in the public file, `is_arm` cannot be derived and the ARM/fixed control is DROPPED — never default an ambiguous NA to fixed.** *(Resolves CRIT-2: §1003.3(d)(4) lets a lender report rate_spread but omit `(a)(26)`; NA→fixed would model an ARM as fixed.)* |
| `combined_loan_to_value_ratio` | (a)(24) | NA/Exempt → exclude-with-reason |
| `debt_to_income_ratio` | (a)(23) | **Public-file column is a binned Alphanumeric construct — treat as CATEGORICAL, forbid numeric coercion** (coercion silently deletes the >60% / <20% tail bins). NA/Exempt → exclude-with-reason. *(Restores the Audit-2 rule dropped in v3.)* |
| `property_value` | (a)(28) | NA/Exempt → exclude; log() domain guard |
| `income` | (a)(10) | thousands; **`1111` = real $1.111M, NOT a sentinel here**; NA → exclude; log() domain guard |
| `loan_amount` | (a)(7) | log() domain guard |
| `loan_term` | (a)(25) | NA/Exempt → exclude-with-reason |
| `lien_status` | **(a)(14)** | corrected from v3's (a)(33) — (a)(14) is the required field; (a)(33) is the optional application-channel field. |
| `derived_msa-md` (MSA FE) | (a)(9) | `[BUILD-RECON: confirm the public-file non-metropolitan / blank encoding before use as an FE regressor — no sentinel is documented on the FFIEC field page; do not assume one.]` |

- **log() domain guard:** income/loan_amount/property_value ≤ 0 or non-finite → exclude-with-reason `out_of_range_*`.
- **`1111` is never a global sentinel** — field-specific only.
- **Partial exemption (§1003.3(d)) — dedicated handling.** Two regimes: the **all-or-nothing** set covers only `(a)(15),(16),(17),(27),(33),(35)`; everything else is **à-la-carte** per `(d)(4)` — a partially-exempt lender may report any subset. Therefore **every optional field needs an `Exempt` → exclude-with-reason path**, and a row can pass one field's exempt filter while omitting another. This is a **durable portfolio gotcha** (same class as `1111` and the sentinel notes) — recorded for project knowledge, not just this doc.
- **TDD:** one sentinel mutation test per field per state; each bites.

## 7. Controls & exact equation (points remain out; language corrected)

```
rate_spread_i = β0 + β_pc·protected_class_i
              + β1·log(loan_amount_i) + β2·combined_LTV_i + Σβ·DTI_bin_i
              + β3·log(property_value_i) + β4·log(income_i)
              + Σβ·lien_status_i + β5·loan_term_i + β6·is_arm_i    # is_arm per §6; dropped if underivable
              + Σβ·MSA_i + ε_i
```
- **No `discount_points`/`lender_credits`** — finance charges inside the APR (§1026.4(b)(3)); controlling for them conditions the outcome on a component of its own construction. Correct for the primary estimate.
- **But points are NOT thereby handled** — per §3, rate_spread under-captures the fee channel; that is a stated limitation, and **loan-cost disparity as an outcome is explicitly scoped out of v0.3.0** (not silently resolved). `[AUDIT-4 to rule: is scope-out acceptable, or is costs-as-outcome mandatory for an honest pricing tool?]`
- No `loan_type` dummy (conventional-only). `n` in outputs = post-exclusion modeled n (MED-4). Equation == code exactly (MED-1).

## 8. Inference — cluster-robust SEs
- Default `cov_type='cluster'` on `lei`; single-lender → cluster on MSA.
- **Adequacy = effective cluster count**, not `n`; below floor `[SET IN AUDIT-4]` → wide-CI/low-power flag + name suppression (§12). Few-cluster policy (wild-cluster bootstrap vs hard-suppress) `[SET IN AUDIT-4]`.

## 9. Engine validation — UNCALIBRATED + DISCLOSED (finalized; Bartlett read directly)

**The tool asserts no expected coefficient magnitude.** This is now grounded in a direct read of the primary source (see `BARTLETT-DIRECT-READ.md`), not fragments.

**Why no external anchor is valid (directly-verified wedges).** The most-cited benchmark — Bartlett, Morse, Stanton, Wallace — estimates a *different quantity* on a *different population* than this tool, in every version:
- **Different outcome:** its dependent variable is the **note interest rate** (verbatim "Dependent Variable: Mortgage Interest Rate"), not APR−APOR. The tool's outcome is the APR-based rate spread.
- **Different identification the tool cannot replicate:** it controls credit risk via **72 GSE-grid fixed effects (credit score × LTV)** from a McDash-Equifax merge; **public HMDA has no individual credit score.** Its 7.88 bps (purchase) / 3.56 bps (refi) are credit-risk-controlled residuals; the tool's coefficient is an OVB-laden public-HMDA estimate. There is no valid mapping between them.
- **Different sample:** GSE-securitized, conventional (excludes FHA/VA/FSA/RHS), conforming, 30-yr fixed, **2009–2015**, and **excludes CRA-tract loans** (n = 3,577,010). The tool is pooled public HMDA, **2018+**, and **includes** CRA tracts.
- **Different group:** a **pooled Latinx-/African-American** indicator; the tool's default is **Black-only**, ethnicity separate.

These wedges are **version-independent** for the purpose at hand: even if the published JFE (which I have not read — the uploaded file is NBER w25943, the 2019 working paper) adds an FHA or a 2018/2019 public-HMDA analysis, the tool still differs in outcome, credit-score handicap, era, and default group. So the tool uses Bartlett **only to illustrate the mismatch, never as a magnitude target.** `[FOOTNOTE / open — non-blocking: the published JFE reportedly adds FHA analysis and reports $450M aggregate, and Audit-3 referenced a 2018/2019 public-HMDA points analysis. If that analysis exists it is a closer analog worth acknowledging — but it does not restore a magnitude target, because the tool still lacks credit scores and uses a different outcome. To be confirmed if/when the published typeset is read.]`

**What replaces calibration — synthetic-recovery engine validation:**
- **It is an ENGINE check, not calibration** (dropped the v3 "honest analogue of calibration" claim). It tests the estimator (unbiasedness, CI coverage), not real-world magnitude — disjoint failure classes.
- **The generator must be adversarial to §8:** plant a **lender random effect** + **Herfindahl-heavy lender imbalance**; verify the cluster-robust estimator recovers planted δ (incl. δ=0 at the nominal rate), AND include an **HC1 negative control that MUST over-reject** — so a build that silently drops `cov_type='cluster'` fails the check. (v3's iid-error δ=0 check would pass such a build trivially.)
- **The synthetic harness also sets the §12 CI-width bound** (see §12) — a power analysis on planted δ at realistic n and cluster structure, replacing the (invalid) port of Bartlett's SE.
- **Named non-detectable limitation:** synthetic recovery cannot catch omitted-variable bias — a real 15 bps driven by lower minority credit scores on a given lender passes every engine check and would get a lender named. Hard limitation of the whole approach; stated in §13.
- **Plausibility guard, not a band:** `|coefficient|` beyond a wide ceiling `[SET IN AUDIT-4]` flags a probable spec/data error — a sanity signal, never a fair-lending threshold, never a runtime gate on a named lender. (Note: this is not a substitute for a tight dev-time drift check; the synthetic harness is.)
- **Mandatory disclosure on every output:** "This estimate is not calibrated to an external benchmark; no published study shares this tool's data and design. Interpret sign and significance as a screening signal only, not a magnitude to compare against any published figure."

## 10. Outliers & sparse MSAs
- **No winsorizing** (rewrites values, attenuates toward lender-favorable). Extremes excluded-with-reason (threshold+count) or retained — never rewritten.
- **Sparse MSAs not silently collapsed to reference** — report reassigned count or exclude-with-reason `sparse_msa`.

## 11. Reconciliation identity
`classified + excluded + reassigned == universe`, exact. Vocabulary: `na_race`, `joint_race`, `multiminority_race`, `na_rate_spread`, `exempt_rate_spread`, `exempt_intro_rate_period`, `na_ltv`, `na_dti`, `na_property_value`, `na_income`, `na_loan_term`, `pre_2018_excluded`, `sparse_msa`, `out_of_range_*`, `action2_field_unavailable`, … No silent drops/reassignments.

## 12. Interpretation, language, suppression (CI-width bound severed from Bartlett)
- Coefficient in **bps**; "screening signal, not a finding." Never "discrimination"/"overcharging."
- **Three-location conditional disclaimer** + selection/measurement caveat (§4) + within-year caveat (§3) + points-under-capture caveat (§3/§7) + uncalibrated caveat (§9) — all metric-bound, non-strippable.
- **Lender-name suppression** unless ALL: effective cluster count ≥ §8 floor; protected-class CI excludes zero AND **CI width below a threshold derived from the §9 synthetic power analysis** — the width at which the tool has adequate power to distinguish a policy-relevant effect from noise at the run's n and cluster structure. **This is NOT ported from Bartlett** — the working paper's SE (≈0.31 bps at n≈1.5M, lender-clustered, note-rate/GSE-grid design) is a different estimand and precision context and does not transfer. Deriving the bound from the tool's own recovery harness removes the last Bartlett dependency. `[SET IN AUDIT-4: the exact width, as an output of the power analysis.]`
- Also required: every FFIEC control present; model well-conditioned (condition number < `[SET IN AUDIT-4]`); sample ≥ min. NOT pseudo-R² (doesn't transfer — MSA FE inflate R² via geography while the coefficient stays imprecise). Bare `p>0.05` untrustworthy until SEs cluster (§8).

## 13. Limitations (3+ places)
All denial-engine limitations, PLUS: uncalibrated — no published study shares the tool's estimand (§9); conditional on origination + LE-vs-CD measurement drift (§4); **fee/points channel under-captured** (§3/§7); within-year lock-timing (§3); 2018+ only (§5); OVB non-detectable by engine validation (§9). ~~"No note rate"~~ deleted (false).

## 14. Citations (verify verbatim; NO fabricated cells; Bartlett only from a direct read)
§1026.35 (HPML + points-inclusive APOR (a)(2)); §1026.4(b)(3) (points are finance charges); §1003.4(a)(5)(7)(9)(10)(12)(14)(23)(24)(25)(26)(28); §1003.4(a)(21) interest_rate; §1003.3(d) partial exemption (all-or-nothing set + (d)(4) à-la-carte); Cmt 4(a)(12)-7/-8, 4(a)(26)-3; govinfo 2017 CFR §203.4(a)(12)(i) (pre-2018 thresholds); Wooldridge §3.3; Greene §17. **Bartlett, Morse, Stanton & Wallace — cite specifically as the 2019 NBER working paper w25943 (Table 2: 7.88/3.56 bps, note-rate DV, GSE-grid ID, 2009–2015 conventional excl-CRA; read directly), NOT as JFE 143(1):30–56 unless the published typeset is read; used only to illustrate design mismatch, never as a magnitude target.**

## 15. Open items
- ✅ `[DIRECT READ]` DONE — §9/§12 closed from the actual PDF (`BARTLETT-DIRECT-READ.md`). Non-blocking footnote remains: confirm whether the published JFE's added FHA / 2018–2019 analysis is a closer analog (does not restore a magnitude target; §9).
- `[SET IN AUDIT-4]` effective-cluster floor; few-cluster policy; condition-number threshold; §12 CI-width from the synthetic power analysis; plausibility ceiling; ruling on costs-as-outcome scope-out (§7).
- `[BUILD-RECON]` `is_arm` NA-vs-Exempt distinguishability in the public file (§6 — gates whether the ARM control survives); `derived_msa-md` non-metro encoding; each §7 regressor's action-2 availability; `rate_spread` public-CSV dtype.

---
### Gate
v4-final ready → **fourth fresh hostile audit** → resolve → build. Authoring + reading + audit don't break the waterfall-py settle window.
