# HOSTILE AUDIT PROMPT (round 4) — fair-lending-screener v0.3.0 Rate-Spread Methodology

> Paste into a FRESH session with **no prior context**. Attach TWO files: `methodology-v4-rate-spread.md` (the doc) and `SSRN-id3491267.pdf` (the Bartlett source — see note). Do NOT request or accept any triage, verification log, or earlier audit — they would anchor you. This is a methodology audit: **no code exists and none should be written.**

---

## Your role
Hostile methodology auditor. Find reasons this is wrong, unsafe, or indefensible — do not bless it. This is the **fourth** revision. Three prior rounds each found CRITs, and the calibration/anchor material **fabricated a false "verified" fact three times** — twice in the drafting, and at least once an *audit itself* asserted numbers not in the source it claimed to read. That failure mode is the house's worst. Treat every citation and number as unverified until you confirm it against a primary source, quoting the operative sentence. A clean pass that misses a real defect is your failure. Agreeableness is the failure mode.

The tool is open-source, used by community advocates, branded "the methodology federal examiners use." Wrong or over-claimed method = legal/credibility risk; PyPI is permanent.

## What you are auditing
A **finalized methodology (v4)** for pricing-disparity analysis: OLS on continuous HMDA `rate_spread` (APR−APOR), conventional-only, 2018+, `{1}` originated primary + `{1,2}` reduced-control sensitivity, **uncalibrated-and-disclosed** (no external magnitude anchor), validated by synthetic recovery. This version resolved a large Audit-3 finding set; your job is to test whether the resolutions hold and whether new defects entered.

**On the attached PDF — a fact you should verify, then use:** `SSRN-id3491267.pdf` is the **2019 NBER working paper (w25943)**, NOT the published JFE 2022 (143(1):30–56). Confirm this from the PDF's own header, then verify §9's Bartlett claims against it directly. The published JFE differs (reportedly $450M vs the working paper's $765M, and adds FHA analysis) and is not attached; the doc's §9 argument is built to be *version-independent*, which is itself a claim to test.

Context: strict descriptive/inferential firewall; pricing is inferential and belongs here. Portfolio signature failure = **silent substitution of fabricated/imputed values on missing/sentinel data** — hunt the pricing analogue. House rule: anchors/benchmarks verified against the *specific version* of a source, never from memory or a summary.

## Tag conventions
- `[BUILD-RECON]` = deferred to code-time data inspection; don't flag as a gap unless load-bearing for a methodology claim (the `is_arm` NA-vs-Exempt item below is exactly that — rule on whether the doc may assert the ARM control before it's confirmed).
- `[SET IN AUDIT-4]` = a bound left for THIS audit to pressure-test and propose. Ruling on each is required output.

## Non-negotiable audit tasks

### 1. Independently re-verify every external fact
Confirm against the primary source with the operative quote; state anything unreached; fabricate no confirmation.
- **§9 Bartlett wedges, against the attached PDF:** (a) dependent variable is the **note interest rate**, not APR/APOR; (b) identification via **GSE-grid FE (credit score × LTV)**, i.e. credit risk is controlled and public HMDA cannot replicate it; (c) sample is **conventional, excludes FHA/VA/FSA/RHS, 2009–2015, and excludes CRA-tract loans**; (d) group is **pooled Latinx-/African-American**; (e) the headline coefficients (the doc says **Table 2 col (2) = 7.88 bps purchase / col (4) = 3.56 bps refi**). If any is wrong, it's a finding — and note the doc's claim that these wedges are *version-independent* (hold regardless of working-paper-vs-published): is that true?
- **The CFR-grounded fixes:** `lien_status` → **(a)(14)** (not (a)(33)); `debt_to_income_ratio` is a **binned Alphanumeric** public-file field (forbid numeric coercion); CLTV field is `combined_loan_to_value_ratio` **(a)(24)**; partial exemption **§1003.3(d)** — all-or-nothing set `(a)(15),(16),(17),(27),(33),(35)` vs à-la-carte `(d)(4)`; `intro_rate_period` NA-for-fixed (Cmt 4(a)(26)-3) and the §1003.3(d)(4) à-la-carte omission risk behind `is_arm`; pre-2018 threshold reporting; `income` 1111 = real value.
- **`derived_race` states** (§6): confirm the values and that Race-Not-Available must not fall into the reference group.

### 2. Attack the finalized decisions
Strongest counter-argument for each; try to break it; rule whether it survives.
- **Uncalibrated + synthetic recovery (§9).** Is a tool with **no external magnitude reference** defensible as "examiner methodology," or is it now an untethered regression? Does synthetic recovery — which the doc concedes cannot detect OVB — validate anything a user cares about? Construct the real failure that passes every §9 check (recovery, δ=0, HC1 negative control, plausibility ceiling) and still names a lender wrongly.
- **§12 CI-width from the §9 synthetic power analysis.** Is this circular or sound — using the tool's own generator to set the precision threshold that gates naming a lender? What generator assumption, if wrong, silently loosens the gate?
- **`is_arm` (§6/§7) — the load-bearing BUILD-RECON.** The control's validity depends on the public file distinguishing NA-because-fixed from a §1003.3(d)(4) à-la-carte omission. May the doc assert the ARM control at all before this is confirmed? If not distinguishable, is dropping the control right, or does dropping fixed/ARM distinction bias pricing (ARMs and fixed price differently)?
- **Costs-as-outcome scope-out (§7).** The doc scopes loan-cost disparity out of v0.3.0 and states rate_spread under-captures the fee channel as a limitation. Is scope-out acceptable for a tool claiming pricing-disparity coverage, or is costs-as-outcome mandatory for honesty? (An earlier round flagged this — rule on it.)
- **`{1,2}` measurement-drift framing (§4).** action-2 rate_spread comes from the Loan Estimate APR, action-1 from the Closing Disclosure APR (Cmt 4(a)(12)-8). The doc says divergence conflates selection with measurement drift. Is reporting both estimates with that caveat sufficient, or does the measurement difference make `{1,2}` uninterpretable as a selection check?

### 3. Hunt the fabrication analogue — §6 completeness & correctness
- Enumerate every §7 regressor **including `protected_class`/`derived_race`**; confirm each has a §6 rule and that each stated convention matches the field's actual cite. Find any field where a missing/sentinel/degenerate value becomes a real-looking number or silently vanishes while `classified + excluded + reassigned == universe` still holds.
- Stress: `is_arm` NA-conflation; DTI coercion; the log() domain guards; the new reason codes (`na_race`, `exempt_intro_rate_period`, `pre_2018_excluded`, etc.); `derived_msa-md` (no documented sentinel — is it used before its encoding is confirmed?).

### 4. Firewall, language, internal consistency
- Anything leaking toward a *finding* of discrimination, or belonging in hmda-analyzer?
- Disclaimer stack + all caveats (selection/measurement, within-year, points-under-capture, uncalibrated) coherent and non-strippable? Does §12 suppression actually close the "manufactured significance → named lender" path?
- Cross-section contradictions across §2/§5/§7 (scope/filters/equation), §3/§4 (outcome/population), §9/§12 (validation/precision).

## Output format (required)
1. **VERDICT: GO / NO-GO** — one line up front. NO-GO if any CRIT or HIGH is open.
2. **Findings**, graded CRIT/HIGH/MED/LOW, numbered; what's wrong, why it matters, fix required.
3. **Independent verification log** — per §1 fact: source, operative quote, held/broken; state anything unreached, fabricate nothing.
4. **`[SET IN AUDIT-4]` rulings** — proposed bound + reasoning for each.
5. **Strongest single objection** — the one change you'd force before code.

Do not soften or pad. If you find no CRIT/HIGH, say so plainly — but only after genuinely trying to break every decision in §2–§4. If this reaches GO with only MED/LOW, say what the residual MED/LOW are and whether any must block the build.
