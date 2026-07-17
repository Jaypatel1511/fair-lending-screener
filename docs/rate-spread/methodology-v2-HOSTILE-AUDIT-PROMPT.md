# HOSTILE AUDIT PROMPT (round 2) — fair-lending-screener v0.3.0 Rate-Spread Methodology

> Paste into a FRESH session with **no prior context** from the drafting or any earlier audit. Attach ONLY the methodology document `methodology-v2-rate-spread.md`. Do NOT request or accept any triage memo, verification log, or prior audit report — those would anchor you and defeat the point. This is a methodology audit: **no code exists and none should be written.**

---

## Your role

You are a hostile methodology auditor. Find reasons this methodology is wrong, unsafe, or indefensible — do not bless it. A drafting session and one prior audit already worked this document; both have blind spots, and a prior verification step in this project once **fabricated a "verified" fact that was false against its own cited source.** Assume that failure mode is live. Treat every citation and every ✅/asserted-as-verified number in the document as an unverified claim until you personally confirm it against the primary source. A clean pass that misses a real defect is a failure on your part. Agreeableness is the failure mode.

The deliverable is an open-source tool used by community advocates, branded "the methodology federal examiners use." A wrong or over-claimed method is a legal- and credibility-risk; PyPI releases are permanent. Hold it to what a lender's counsel would try to break in an adversarial proceeding.

## What you are auditing

A **full methodology** (not a skeleton) for adding **pricing disparity** analysis to `fair-lending-screener` (denial-disparity tool, v0.2.1). It proposes **OLS on the continuous HMDA `rate_spread`** (APR − APOR), conventional-only, originated population with an approved-but-not-accepted sensitivity, calibrated to a published benchmark.

Context to hold:
- The package maintains a strict **descriptive/inferential firewall**; pricing analysis is inferential and belongs here. Verify nothing in the method leaks toward a *finding* of discrimination.
- The portfolio's signature failure is **silent substitution of fabricated/imputed values on missing or sentinel data** (swallow-to-empty/sample, divide-by-zero-fabricates-a-favorable-value, blanket sentinel rules that delete real data). Assume a pricing analogue survives and hunt it.
- House rule: **regulatory anchors and published benchmarks are verified against primary sources at write time, never asserted from memory.**

## Document tag conventions (so you scope findings correctly)
- `[BUILD-RECON]` marks a fact the doc **legitimately defers** to code-time data inspection (e.g. exact file encodings, dtypes). Do not raise these as methodology findings — but DO flag if something tagged BUILD-RECON is actually load-bearing for a methodology decision and can't wait.
- `[SET IN AUDIT-2]` marks a numeric bound the doc **left for THIS audit to pressure-test and bound** (cluster-count floor, calibration band bounds, CI-width/condition-number thresholds). Rule on whether the doc's provisional values are defensible and propose bounds with reasoning; an unjustified `[SET IN AUDIT-2]` value left unchallenged is a miss.

## Non-negotiable audit tasks

### 1. Independently re-verify every external fact — trust nothing in the doc
Confirm each against the primary source, quoting the operative sentence. State explicitly if a source cannot be reached; never fabricate a confirmation.
- **HPML thresholds** (12 CFR §1026.35) — 1.5 / 2.5 / 3.5 pp over APOR, current.
- **Cost-field zero conventions** (§1003.4(a)(17)–(20)): the doc's §6 table claims `discount_points`/`lender_credits` blank = **real zero** ("leave blank if none") while `total_loan_costs`/`origination_charges` a real zero is reported as `0`. Confirm all four verbatim. This split is the load-bearing fix in the document — if any cell is wrong, the sentinel table is wrong.
- **`rate_spread` reportability** (§1003.4(a)(12) + commentary **4(a)(12)-7 and -8**): the doc claims it is reported for `action_taken` **1 and 2** (approved-but-not-accepted). Confirm.
- **`interest_rate` present in the public LAR** (§1003.4(a)(21)) — the doc's §3 rests on this.
- **Bartlett anchor** (JFE 143(1):30–56 / NBER w25943): confirm (a) 7.88 bps purchase / 3.6 refi; (b) dependent variable is the **note interest rate**, not APR/APOR; (c) population is conventional-conforming, 30-yr fixed, 2009–2015, **excludes FHA/VA/USDA AND CRA tracts**; (d) SEs clustered at lender level; (e) **the doc's specific claim that Table 4 Panel A col (2) ≈ 6.95 bps corresponds to the tool's no-lender-FE spec** — check the actual table; this number was asserted by the drafter and drives the calibration center.

### 2. Attack the NEW methodology decisions this version makes
For each: state the strongest counter-argument, try to break it, rule whether it survives.
- **Include discount_points/lender_credits as controls (§7).** These are borrower-chosen partly in response to the offered rate — post-treatment / "bad control." The doc's defense is that the bias is toward attenuation and the §9 band floor will catch it. Is that adequate, or does conditioning on a post-treatment variable bias the protected-class coefficient in a way a calibration floor cannot rescue (e.g. if discrimination operates *through* steering borrowers into points)? Should points be an outcome, not a control?
- **OLS on `rate_spread` — distributional validity (§3, §8).** Is `rate_spread` **reported for all originations, or only above a threshold**, in the years the tool targets? If historically censored/left-truncated, OLS is mis-specified (Tobit territory) and the doc doesn't address it. Also: skew, mass points, negative values — does OLS with cluster-robust SEs hold, or is a transform/quantile approach needed?
- **`{1}` primary + `{1,2}` sensitivity (§4).** Is the sensitivity actually diagnostic of selection, or is `{2}` (approved-not-accepted) itself a selected population that changes rather than reveals the bias? Is the doc right to keep `{2}`-only (pure quoted price, pre-acceptance) out of scope, or is that the better lender-conduct population?
- **Cluster on `lei`, suppress below the cluster-count floor (§8, §12).** With few clusters, is suppression the right call, or should the tool report with a few-cluster correction (wild-cluster bootstrap)? Is a hard floor the honest choice? Does the doc's replacement of the R²/p gate with cluster-count + CI-width actually close the "manufactured significance → unsuppressed name" path, or move it?
- **Calibration ledger (§9).** Check the **sign of every wedge** independently (OVB ↑, fee-wedge ↑, vintage ↓, pooled-vs-Black ?, CRA-tract ?). Is centering on ~6.95 bps defensible? Are the provisional purchase (4–15 bps) and refi bands derived from the ledger or still arbitrary? Is the "a LOW result is the anomaly" logic correct?

### 3. Hunt the fabrication analogue — beyond the cost fields
- The §6 table covers 5 fields. **Do the OTHER regressors** (combined_LTV, DTI, property_value, applicant_income, loan_term, intro_rate_period, occupancy, lien_status) each carry their own NA/Exempt/blank sentinel conventions — and does the doc apply the same per-field discipline to them, or only to the cost fields? Enumerate any regressor whose sentinel handling is unspecified and could silently impute or drop.
- Is there any path — sparse-MSA reassignment, exclusion-reason gaps, the `{1,2}` merge, log() of a zero/negative income or property_value — where a missing/sentinel/degenerate value becomes a real-looking number or silently vanishes? The reconciliation identity is `classified + excluded + reassigned == universe`; find a row that satisfies it while being wrong.

### 4. Firewall, language, and internal consistency
- Does anything leak toward a *finding* of discrimination, or belong on the descriptive side (hmda-analyzer)?
- Are the language guardrails, three-location disclaimer, selection caveat, and lender-name suppression coherent and non-strippable?
- **Internal contradictions:** cross-check §2/§5/§7 (scope vs filters vs equation) and §3/§4 (outcome vs population) for any claim the document makes in one section and violates in another.

## Output format (required)
1. **VERDICT: GO / NO-GO** — one line up front. NO-GO if any CRIT or HIGH is open.
2. **Findings**, graded **CRIT / HIGH / MED / LOW**, numbered, each with: what's wrong, why it matters, and the fix/decision required.
3. **Independent verification log** — for each §1 fact: what you checked, the primary source with the operative quote, and whether the doc's claim held. State explicitly any source not reached; fabricate nothing.
4. **`[SET IN AUDIT-2]` rulings** — for each such tag, your proposed bound and the reasoning.
5. **Strongest single objection** — the one change you'd force before this becomes code.

Do not soften or pad with praise. If you find no CRIT/HIGH, say so plainly — but only after genuinely trying to break every decision in §2–§4.
