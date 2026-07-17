# Audit-2 Triage — v0.3.0 Rate-Spread Methodology (planning-chat disposition)

**Verdict: CONCUR with NO-GO (5 CRIT, 8 HIGH).** This is a deeper NO-GO than Audit-1 — several defects are conceptual, not clerical, and two of them mean the methodology was reasoning from the wrong source material. I independently corroborated the load-bearing findings before accepting them (log below). The methodology-first discipline is doing exactly its job: catching this *before* any code.

## Owning the calibration fabrication (mine, in the doc)

methodology-v2 §9 stated: anchor "verified: 7.88 bps purchase (Table 4 Panel A col (1))," and centered calibration on an invented "col (2) ≈ 6.95 bps." Re-checked against sources:
- **$450M is the published JFE figure; $765M and 7.88 bps are the 2019 NBER working-paper figures.** The doc cited JFE 143(1):30–56 while using working-paper numbers.
- **"Table 4 Panel A col (2) ≈ 6.95" was manufactured.** I asserted a table structure and derived a number I never read from any version of the paper. The published Table 4 is a FinTech-vs-non-FinTech table with no panels.
- This is the **second calibration fabrication of the thread** (first was the verification log). Both times: I asserted anchor numbers/structure from search snippets or the working paper instead of reading the actual published tables.

**Hard rule now (not a nicety): the calibration section may be drafted ONLY from the published JFE tables read directly. No working-paper numbers, no memory, no search snippets, no derived table cells. If the published tables aren't in hand, the calibration section stays explicitly UNRESOLVED — it does not get a provisional number.**

## Finding disposition (load-bearing items)

| Finding | Disposition | Notes |
|---|---|---|
| **CRIT — calibration citation ≠ calibration numbers** | **ACCEPT** (corroborated: $450M published vs $765M WP) | Rebuild §9 from the published tables read directly, or drop the tight anchor entirely (see Decision A). |
| **CRIT — §7 include-points is refuted** | **ACCEPT → REVERSE.** Exclude points/credits as controls | Points are finance charges *inside* the APR (§1026.4(b)(3)); conditioning an APR-based outcome on a component of its own construction is unsound. The anchor's own 2018/2019 experiment shows the coefficient *rose* controlling for points. Do not control for points; disclose that rate_spread is net-of-points price and the points/rate tradeoff is part of the outcome, not a confound to remove. |
| **CRIT — {1,2} selection sensitivity is a guaranteed no-op** | **ACCEPT** (confirmed: cost fields are Closing-Disclosure-only → NA for unclosed action-2 rows) | **Interaction:** reversing §7 (drop cost controls) *unblocks* this — once points/credits aren't required regressors, action-2 rows with their application-side controls (LTV, DTI, income, loan_amount, property_value) can survive. Redesign {1,2} as a genuine reduced-control model, or drop it from v0.3.0. See Decision C. |
| **CRIT — no `activity_year >= 2018` guard** | **ACCEPT** (confirmed: pre-2018 rate_spread threshold-reported; blank = below-threshold = real low value) | Hard-gate the tool to 2018+. Pre-2018 blank ≠ missing; mixing eras + §6 blank→exclude fits the subprime tail. |
| **CRIT — fabrication analogue survives (intro_rate_period)** | **ACCEPT** | `intro_rate_period` is NA for every fixed-rate loan (Cmt 4(a)(26)-3); §7 makes it a continuous regressor, §6 has no rule → generic NA-drop silently models ARMs only. §6 sentinel table must cover EVERY regressor, not just the 5 cost/spread fields. |
| **HIGH — §9 ledger wedge signs wrong (3 of 5)** | **ACCEPT** | CRA wedge is backwards (anchor's own Table 6: CRA tracts 6.431 vs 4.043, disparities *larger*); vintage ↓ unsourced; fee wedge contradicts the corrected §7. Rebuild the ledger from the published paper — folds into Decision A. |
| **HIGH — refi band center** | **ACCEPT** | Auditor: matched figure ~6.900, so 3.6 center would bless an attenuated engine. Folds into the §9 rebuild. |
| Other HIGHs (per-field sentinel completeness, cluster on effective clusters, etc.) | **ACCEPT** | Detailed in the audit file; roll into v3. |

## What held up (keep)
- §6 cost-field split is substantively correct (all four cells confirmed verbatim). Fix the attribution only: "leave blank" is FIG/reporting language, not CFR text.
- §3 rate_spread-over-note-rate argument (no month/day date in public LAR) — the strongest reasoning in the doc; keep.
- §12 R²→precision swap — correct; corroborated by the published R² gap.
- Firewall placement and language guardrails — clean.

## Independent corroboration log (what I checked myself this round)
- **Published figure $450M, not $765M** — multiple JFE-linked sources; confirms WP-vs-published divergence. `[Could not read the ScienceDirect typeset tables directly — paywalled; the exact published coefficients need direct access, see Decision A.]`
- **Pre-2018 threshold reporting** — confirmed (regulatorysol / FFIEC): 2009–2017 reported only if spread > 1.5/3.5 pp; 2018+ all originations, negative or positive.
- **Points inside APR + 2018/2019 points test** — confirmed points are finance charges in APR; confirmed Bartlett used 2018–2019 HMDA to examine points and the minority differential "remains positive and significant when controlling for other factors."
- **Cost fields Closing-Disclosure-only** — logically confirms NA for unclosed action-2 rows → the {1,2} no-op.
- Not independently reached: the exact published JFE table cells (paywall), and the verbatim Table 10 points figures — accepted on the auditor's extraction + corroborating narrative; to be confirmed against the published tables in the v3 calibration rebuild.

## Decisions needed before v3 (these are genuine forks, not clerical)
- **A — Calibration anchor.** Given (1) I've fabricated anchor specifics twice, (2) the published numbers differ from the working paper, (3) Bartlett's design (GSE-grid risk-equivalence, excludes CRA tracts, note-rate outcome) is fundamentally different from this tool's pooled-public-HMDA APR-spread design — is Bartlett even the right anchor? Options in the chat question.
- **B — Points:** reverse to exclude (my strong rec; auditor-forced; theoretically clear). Likely no need to debate.
- **C — {1,2} sensitivity:** redesign as reduced-control (now viable post-§7-fix) vs drop for v0.3.0.

## Meta
Three fabrication-class or theory errors across two audits, all in calibration/anchor material I asserted without reading the primary table. That is a pattern, not bad luck. The rule above (calibration only from tables read directly, else unresolved) is the corrective, and I'm holding to it before drafting any v3 calibration.
