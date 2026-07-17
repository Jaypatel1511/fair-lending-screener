# Audit-1 Triage — v0.3.0 Rate-Spread Methodology (planning-chat disposition)

**Verdict: CONCUR with NO-GO.** The audit is high-quality and substantially correct. I independently re-verified its two CRITs and the key HIGHs against primary sources before accepting them (log below). This was an audit of a self-labeled *pre-audit skeleton* with open ⚠ DECISIONs, so NO-GO was partly definitional — but the findings that survive that caveat are real defects, not nitpicks, and two of them are in facts I had marked ✅ VERIFIED.

## Owning the verification-log failure (stated plainly, not minimized)

`v0.3.0-methodology-VERIFICATION-LOG.md` certified three §1 facts as HELD. Re-checked:
- **HPML thresholds — genuinely held.** Correct.
- **Bartlett 7.9/3.6 bps, pooled group, credit-score-via-grid — the three things I explicitly tested held.** Confirmed again (coeff 0.000788 = 7.88 bps).
- **BUT I failed on scope and introduced one manufactured claim:**
  1. I endorsed the skeleton's "Bartlett = GSE + FHA" population. **False** — the paper explicitly excludes FHA/VA/USDA, is 30-yr fixed only, 2009–2015, and excludes CRA tracts. I certified a population description I never actually checked against the paper.
  2. I never tested the **outcome variable** — Bartlett's DV is the note interest rate, not APR/APOR. Anchoring rate_spread to it without flagging the wedge is a category error I waved through.
  3. Worst: I **manufactured** the "NA is definitionally a non-origination marker" refinement, marked it ✅ VERIFIED, and edited it into the doc's §3/§4. It is **false** — rate_spread is reported for `action_taken` 1 **and** 2 (approved-but-not-accepted), per Reg C commentary 4(a)(12)-7/-8. That is the CBLR-from-memory failure reproduced *inside the control built to prevent it*.

The audit's remedy — don't let that log travel forward as authority — is correct. I am **superseding** the log with the audit's verification table (more thorough and correct) and stubbing the old file so no future reader mistakes it for verified truth.

**Process change (real, not cosmetic):** a verification claim must be checked against the *specific primary-source sentence being asserted*, not a search summary, and the marker must name the exact quote. "Field only exists for originations" should have required reading commentary 4(a)(12)-7 verbatim — which says the opposite.

## Finding-by-finding disposition

| # | Finding | Disposition | Notes |
|---|---|---|---|
| CRIT-1 | rate_spread exists for action_taken 1 **and** 2; §3 keystone claim false | **ACCEPT** (re-verified) | Delete false claim. Population choice becomes real. Adopt: **{1} primary + {1,2} published selection sensitivity.** Cheap, no exclusion restriction, directly answers "is a disclaimer enough" — currently it isn't. |
| CRIT-2 | Cost-field sentinel bug: discount_points/lender_credits blank = **real 0**; §4 blanket "blank→exclude, never 0" deletes the modal borrower | **ACCEPT — best catch** (re-verified: "if no discount points paid, leave blank"; total_loan_costs "enter 0") | §4 rewritten from a blanket rule to a **per-field sentinel table** sourced to each Reg C cite, three states (real-0 / NA / Exempt), different action each. TDD: one mutation test per field per state. |
| HIGH-3 | SEs must cluster on lei; HC1/HC3 manufacture significance on 10⁶ rows → unsuppresses lender names | **ACCEPT — strongest objection** | Econometrically sound regardless of the anchor: lenders share rate sheets → within-lender error correlation. Default `cov_type='cluster'` on lei; single-lender → cluster on MSA. Adequacy rule becomes **cluster count**, not n. |
| HIGH-4 | Anchor DV is note rate, not APR−APOR; fee wedge is a 2nd upward bias, unstated | **ACCEPT** | State the wedge and its sign. |
| HIGH-5 | "Bartlett = GSE+FHA" false; excludes FHA/VA/USDA, 30-yr fixed, 2009–2015, **and CRA tracts** | **ACCEPT** (re-verified) | CRA-tract exclusion is the sharpest mismatch for an advocacy tool — disclose it. Build the signed-wedge ledger (see MED-10). |
| HIGH-6 | §3 "same filters as denial" (conventional-only, loan_type==1) contradicts §5 FHA/VA/USDA dummies | **ACCEPT** | Ruling: **conventional-only for v0.3.0** (matches denial engine + anchor). Government-backed pricing = separately-scoped, separately-calibrated config. Also restore the omitted occupancy==1 and LTV≤100 filters. |
| HIGH-7 | §9 "No note rate" false; interest_rate is in the public LAR | **ACCEPT** (re-verified) | Delete false limitation. Replace §2 justification with the real one: **no month/day date in public LAR → rate environment not absorbable by time FE → rate_spread is the only date-normalized outcome.** Add honest residual: year-level granularity leaves within-year lock-timing variation. |
| MED-8 | Winsorizing offered as an option = fabrication, biased toward the lender | **ACCEPT** | Rule out. Extremes excluded-with-reason (counted, reconciled) or retained — never rewritten. |
| MED-9 | <30-obs MSA → reference is silent **reassignment**; reconciliation identity doesn't catch it | **ACCEPT** | Extend identity to `classified + excluded + reassigned == universe`; report reassigned count, or exclude-with-reason `sparse_msa`. |
| MED-10 | 2–25 bps band arbitrary, wrong-direction asymmetric, one band can't serve purchase+refi | **ACCEPT** | Every wedge pushes the tool's coeff **above** the anchor, so a **low** result is the anomaly — a 2 bps floor waves through the exact attenuation CRIT-2/MED-8 introduce. Center on Bartlett Table 4 col (2) ≈ 6.95 bps (matches the tool's pooled-national/MSA-FE/no-lender-FE spec), separate purchase/refi bands, **dev-time calibration only — never a runtime gate on a named lender.** |
| MED-11 | §3 population and §5 points fork are one joint decision (cost fields are NA for non-originations) | **ACCEPT** | Merge into a single population+controls decision. |
| MED-12 | 1111 used as generic sentinel; it's field-specific — income 1111 = $1.111M (real) | **ACCEPT** | Folds into CRIT-2 per-field table. 1111 is never a global constant. (This is the same 1111 hazard the hmda-analyzer CRA-proxy cycle already caught — portfolio-recurring.) |
| LOW-13 | HOEPA parked correctly; don't ship HPML binary | **ACCEPT** | **Continuous-only for v0.3.0.** HPML cut discards the continuous variation that is the point. |

**Over-reach check:** I looked for auditor over-reach and found essentially none. The only calibration: the process finding's "delete the log" is right in spirit; I'm superseding rather than silently deleting so the correction is visible. Everything else is accepted on the merits.

## Also accept (from the audit's firewall/language section)
- OLS suppression gate: replace pseudo-R² with **cluster count + coefficient CI width**, NOT adjusted R² (a pricing OLS with MSA FE shows high R² from geography/rate-environment while the protected-class coeff is imprecise — fit isn't the risk, precision is). The `p>0.05` limb is untrustworthy until SEs cluster (HIGH-3).
- Firewall placement (§0), "screening signal not a finding" language, and the three-location disclaimer stack: ruled clean by the auditor. No change.

## Decisions I need from Jay before I write methodology-v2 (full doc)
1. **Scope: conventional-only for v0.3.0?** (My rec: yes. Government-backed pricing ships later as its own calibrated config.)
2. **Population: {1} primary + {1,2} selection sensitivity?** (My rec: yes.)
3. **Continuous-only, no HPML binary this version?** (My rec: yes.)

All three are the audit's recommendations and I concur. If you agree, I fill the skeleton into a full `methodology.md` resolving every finding above — which then goes back out for a **second** fresh hostile pass (the filled doc has substantial new decisions and earns its own audit; this portfolio has gone seven rounds before, and that's the system working).
