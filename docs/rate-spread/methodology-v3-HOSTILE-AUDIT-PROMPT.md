# HOSTILE AUDIT PROMPT (round 3) — fair-lending-screener v0.3.0 Rate-Spread Methodology

> Paste into a FRESH session with **no prior context**. Attach ONLY `methodology-v3-rate-spread.md`. Do NOT request or accept any triage memo, verification log, or earlier audit — they would anchor you. This is a methodology audit: **no code exists and none should be written.**

---

## Your role
You are a hostile methodology auditor. Find reasons this is wrong, unsafe, or indefensible — do not bless it. This document is on its **third** revision; two prior audits found CRITs, and **two prior verification steps fabricated a "verified" fact that was false against its own cited primary source — both times in the calibration/anchor material.** That failure mode is the house's worst; assume it is still live somewhere. Treat every citation and every number as unverified until you personally confirm it against the primary source, quoting the operative sentence. A clean pass that misses a real defect is your failure. Agreeableness is the failure mode.

The tool is open-source, used by community advocates, branded "the methodology federal examiners use." Wrong or over-claimed method = legal/credibility risk; PyPI is permanent. Hold it to what a lender's counsel would break in an adversarial proceeding.

## What you are auditing
A **full methodology (v3)** for pricing-disparity analysis: OLS on continuous HMDA `rate_spread` (APR−APOR), conventional-only, 2018+, originated `{1}` primary with an approved-but-not-accepted `{1,2}` reduced-control sensitivity. This version made three deliberate reversals from v2: (a) it **dropped the external calibration anchor** and validates the engine with synthetic-recovery tests instead; (b) it **removed discount_points/lender_credits as controls**; (c) it **added a 2018+ hard gate**. Your job is to test whether those reversals are sound and whether new defects entered with them.

Context: strict descriptive/inferential firewall (pricing is inferential, belongs here). Portfolio signature failure = **silent substitution of fabricated/imputed values on missing/sentinel data**; hunt the pricing analogue. House rule: regulatory anchors and benchmarks verified against primary sources at write time, never from memory.

## Tag conventions
- `[BUILD-RECON]` = legitimately deferred to code-time data inspection; don't flag as a gap UNLESS it's load-bearing for a methodology decision and can't wait (e.g. the `{1,2}` viability question below may be exactly that).
- `[SET IN AUDIT-3]` = a numeric bound left for THIS audit to pressure-test and propose. Ruling on each is required output.

## Non-negotiable audit tasks

### 1. Independently re-verify every external fact — trust nothing in the doc
Confirm against the primary source with the operative quote; state explicitly anything you cannot reach; fabricate no confirmation.
- **Points are finance charges inside the APR** (12 CFR §1026.4(b)(3)) — this is the entire basis for removing points as controls (§7). Confirm points are in the finance charge / APR.
- **`intro_rate_period` is NA for fixed-rate loans** (Reg C commentary 4(a)(26)-3) — the basis for the `is_arm` derivation (§6). Confirm; and check whether NA can arise for reasons OTHER than fixed-rate (exempt, missing) — if so, `is_arm` conflates them.
- **rate_spread reported for `action_taken` 1 AND 2** (commentary 4(a)(12)-7/-8).
- **Pre-2018 threshold reporting** — that pre-2018 `rate_spread` was reported only above 1.5/3.5 pp, so a pre-2018 blank is a real below-threshold value (basis for the 2018+ gate, §5).
- **`income` value 1111 = a real $1.111M applicant, not an exemption** (§6).
- **HPML thresholds** (§1026.35), if still cited.
- For any regressor in §7, spot-check the §6 sentinel convention against the field's Reg C cite — the v2 audit found a whole class of fields the table got wrong.

### 2. Attack the THREE reversals and the new machinery
State the strongest counter-argument for each; try to break it; rule whether it survives.
- **Uncalibrated + synthetic-recovery validation (§9).** Is dropping the external anchor defensible, or does it leave a tool branded "examiner methodology" too unmoored — a bare regression with no external check? Is synthetic-recovery a real validation or theater: does a planted-δ generator with the doc's covariate structure actually test anything the real data would, or does it just confirm OLS is OLS? Does the δ=0 false-positive check test the thing that matters (cluster-robust inference at scale)? What real failure could pass all three of §9's checks?
- **Points removed as controls (§7).** Is "disclose, don't control" honest? Push BOTH ways: (a) if lenders discriminate partly by **steering** minority borrowers into buying points, does removing points as a control now let real disparity hide in the outcome (under-count)? (b) if points-purchasing differs by group for benign reasons, is calling it "part of the price" defensible? Is the net-of-points framing a genuine resolution or a relabeling of an unresolved confound?
- **`{1,2}` reduced-control sensitivity (§4).** The doc claims removing cost controls makes action-2 rows usable. **Verify the premise:** are `combined_LTV`, `DTI`, `property_value`, `loan_term`, `lien_status` actually populated for `action_taken == 2`, or are any origination-only? If any core regressor is NA for action-2, `{1,2}` partially or fully collapses again — the same no-op the doc thinks it fixed. This is tagged `[BUILD-RECON]` but it is load-bearing for a methodology claim — rule on whether the doc may assert the sensitivity works before this is confirmed.

### 3. Hunt the fabrication analogue — is the §6 table COMPLETE and CORRECT now?
- Enumerate every regressor in the §7 equation and confirm each has a §6 rule. Any field without one is a silent-imputation/drop hazard.
- Check each stated convention against the field's actual Reg C cite (don't trust the table). Specifically stress `is_arm` (NA-conflation), the log() domain guards, and the DTI-bin handling.
- Find any path — sparse-MSA reassignment, the `{1,2}` merge, a log of a degenerate value, an unhandled Exempt — where a missing/sentinel/degenerate value becomes a real-looking number or silently vanishes while `classified + excluded + reassigned == universe` still holds.

### 4. Firewall, language, internal consistency
- Anything leaking toward a *finding* of discrimination, or belonging in hmda-analyzer?
- Are the disclaimer stack, selection caveat, uncalibrated caveat, and lender-name suppression coherent and non-strippable? Does the suppression gate (§12) actually close the "manufactured significance → named lender" path now that the anchor is gone?
- **Cross-section contradictions:** did dropping the anchor leave dangling references (§13 limitations, §9 directional-context wording, citations)? Cross-check §2/§5/§7 (scope/filters/equation) and §3/§4 (outcome/population).

## Output format (required)
1. **VERDICT: GO / NO-GO** — one line up front. NO-GO if any CRIT or HIGH is open.
2. **Findings**, graded CRIT/HIGH/MED/LOW, numbered, each with what's wrong, why it matters, fix/decision required.
3. **Independent verification log** — per §1 fact: source, operative quote, held/broken; state anything unreached, fabricate nothing.
4. **`[SET IN AUDIT-3]` rulings** — proposed bound + reasoning for each.
5. **Strongest single objection** — the one change you'd force before code.

Do not soften or pad. If you find no CRIT/HIGH, say so plainly — but only after genuinely trying to break every decision in §2–§4.
