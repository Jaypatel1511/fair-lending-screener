# HOSTILE AUDIT PROMPT (round 5) — fair-lending-screener v0.3.0 Rate-Channel Disparity

> Paste into a FRESH session with **no prior context**. Attach THREE files: `methodology-v5-rate-spread.md` (the doc), `SSRN-id3491267.pdf` (Bartlett 2019 **working paper**, w25943, 44pp), and the Bartlett **accepted manuscript** (76pp, from faculty.haas.berkeley.edu/stanton/pdf/discrim.pdf — the version containing **Table 10**). Do NOT request or accept any triage, verification log, or earlier audit — they would anchor you. Methodology audit only: **no code exists and none should be written.**

---

## Your role
Hostile methodology auditor. Find reasons this is wrong, unsafe, or **not worth shipping** — do not bless it. This is the **fifth** revision. The calibration/anchor material has fabricated in every prior round — including, once, an author dismissing a *retrievable* source as "unverifiable" and an audit asserting numbers from a version it hadn't read. Treat every citation and number as unverified until you confirm it against a primary source, quoting the operative sentence. **When the doc names a retrievable source (e.g. Bartlett Table 10), you must open the attached PDF and check it — dismissing a source you were handed is itself the failure mode.** A clean pass that misses a real defect is your failure. Agreeableness is the failure mode.

The tool is open-source, used by community advocates, on permanent PyPI. Wrong or over-claimed method = legal/credibility risk.

## What you are auditing
A **finalized methodology (v5)** with a **deliberately narrowed scope: it reports ONE market-level adjusted rate-channel (APR-spread) disparity coefficient and NAMES NO LENDER.** Lender-level identification was scoped out. OLS on continuous HMDA `rate_spread`, conventional-only, 2018+, `{1}` primary + `{1,2}` inclusion diagnostic, **uncalibrated-and-disclosed**, synthetic-recovery validation, Oster-δ OVB sensitivity reported (not gated).

**On the two attached Bartlett PDFs:** the **working paper** (SSRN-id3491267 = w25943, 2019) has the note-rate GSE-grid 2009–2015 design; the **accepted manuscript** (76pp) additionally contains **Table 10** — a 2018/2019 public-HMDA analysis using census-tract credit-score deciles because (fn31) "the HMDA data do not include individual credit scores." §9 claims Table 10 is a *close analog* but that uncalibrated survives on the *outcome* wedge (note rate vs APR-spread). **Verify both the analog claim and the surviving-wedge claim against the accepted-manuscript PDF directly.**

Context: strict descriptive/inferential firewall; pricing is inferential. Portfolio signature failure = **silent substitution of fabricated/imputed values on missing/sentinel data** — hunt the analogue. House rule: cite only the *specific version* of a source you have read.

## Tag conventions
- `[BUILD-RECON]` = deferred to code-time data inspection; flag only if load-bearing for a methodology claim.
- `[SET IN AUDIT-5 / verify]` = a bound or a statistics reference the doc left for THIS audit to pressure-test. **Several thresholds rest on references cited from memory (Oster 2019, Cameron–Miller, Webb, Carter–Schnepel–Steigerwald, Belsley–Kuh–Welsch) — verify each exists and says what the doc uses it for, or flag it.** Ruling on each is required output.

## Non-negotiable audit tasks

### 1. Independently re-verify the load-bearing facts
Quote the operative sentence; state anything unreached; fabricate nothing.
- **§9 vs the accepted-manuscript PDF:** (a) Table 10 is 2018/2019 public HMDA with tract-credit-decile controls and no individual credit scores (fn31); (b) its DV is the **note interest rate in bps** (this is §9's surviving "outcome" wedge — confirm it, because the whole uncalibrated argument now rests on it); (c) Table 10 controls for points and uses lender×year FE. If any is wrong, §9 is wrong again.
- **`derived_race` is an FFIEC-*derived* field from §1003.4(a)(10)(i)** (race) — NOT §1003.4(a)(5) (construction method). Confirm (a)(5) is construction method and (a)(10)(i) is ethnicity/race/sex, and that `derived_race`'s nine values are FFIEC-defined, not CFR.
- **Sentinel/CFR facts:** `open_end_line_of_credit`/`reverse_mortgage` are (a)(36)/(a)(37) and HELOCs carry a real comparable-transaction rate_spread (Cmt 4(a)(12)-3/-4); `lien_status` (a)(14) always-required; `income`/`loan_amount` always-required (not in (d)(1)(iii)); Cmt 4(a)(26)-2 preferred-rate NA; the LE-vs-CD APR split (Cmt 4(a)(12)-8 vs -3); points inside APR (§1026.4(b)(3)); APOR points-inclusive (§1026.35(a)(2)).
- **Every `[verify]` statistics reference.**

### 2. Attack the narrowed design — and rule whether it is worth shipping
Strongest counter-argument for each; try to break it.
- **Is a market-level, uncalibrated, OVB-undetectable, names-no-one coefficient USEFUL, or is it so hedged it says nothing an advocate can act on?** This is the central question. §1 concedes the coefficient conflates within-lender pricing with between-lender sorting and identifies no firm; §9 concedes no magnitude reference and undetectable OVB; §13 stacks caveats. Rule explicitly: does the output support any defensible user action, or should the feature be deferred and only the denial-engine improvements ship? A methodology that is *safe by being vacuous* is a NO-GO of a different kind — say so if that's what this is.
- **Between-lender sorting (§1/§13).** Is disclosing it as a limitation enough, or does it make the market-level number *uninterpretable* (a positive coefficient could be 100% sorting — Black borrowers using higher-cost lenders — with zero within-lender discrimination anywhere)? Does the label "rate-channel disparity" adequately prevent an advocate from reading market sorting as lender pricing?
- **Oster-δ reported-not-gated (§9/§12).** OVB is the error the design has and §9 concedes synthetic recovery can't catch it. Is *reporting* a δ sensitivity (vs gating on it) adequate for an advocacy tool, or will users ignore a δ they don't understand and act on the point estimate?
- **Uncalibrated on the outcome wedge alone (§9).** With era, data, and credit-score handicap now shared with Table 10, the *only* thing separating the tool from a published analog is the APR-spread-vs-note-rate outcome. Is that one wedge enough to justify "no magnitude reference," or does Table 10's existence mean the tool could and should report *some* directional benchmark?
- **`{1,2}` inclusion diagnostic (§4).** Renamed from sensitivity because no decision follows. If no decision follows and its power may be tiny (small action-2 share), why is it in the methodology at all? Keep or cut?

### 3. Hunt the fabrication analogue
- §6 completeness across EVERY §7 regressor incl. `derived_race`; each convention vs its actual source. The **reason-code precedence** (§6/§11): does first-wins actually guarantee exactly one code, and is the ordering defensible (could it mask a more informative exclusion)? The **per-LEI `is_arm` test** (§6): construct an LEI where it silently misclassifies (e.g. a small all-fixed lender, or a lender that reports one ARM and 10,000 fixed). The **HELOC/reverse filters**: any path where an out-of-scope row still enters?
- Any path where a missing/sentinel/degenerate value becomes real-looking or vanishes while `classified + excluded + reassigned == universe` (exactly one code each) still holds.

### 4. Firewall, language, consistency, over-claim
- Anything leaking toward a *finding* of discrimination or a lender attribution the scope forbids?
- **HIGH-2 carryover:** the doc flags the "examiner methodology" tagline as unsourced and defers it. Is anything *inside* the methodology over-claiming supervisory provenance? Rule on whether the doc may ship while the tagline is unsourced.
- Cross-section contradictions across §1/§2 (scope), §7 (equation), §9/§12 (validation/output), §13 (limitations).

## Output format (required)
1. **VERDICT: GO / NO-GO** — one line up front. NO-GO if any CRIT/HIGH is open OR if the feature is judged not worth shipping in this form (state which kind of NO-GO).
2. **Findings**, graded CRIT/HIGH/MED/LOW, numbered; what's wrong, why, fix.
3. **Independent verification log** — per §1 fact: source, operative quote, held/broken; state anything unreached, fabricate nothing.
4. **`[SET IN AUDIT-5 / verify]` rulings** — proposed bound + reasoning; and a verified/unverified verdict on each statistics reference.
5. **Is-it-worth-shipping ruling** — a direct yes/no with reasoning, separate from the finding count.
6. **Strongest single objection.**

Do not soften or pad. If GO with only MED/LOW, say what they are and whether any must block the build. If the honest answer is "defer the feature," say that plainly.
