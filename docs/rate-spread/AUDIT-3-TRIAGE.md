# Audit-3 Triage — v0.3.0 Rate-Spread Methodology (planning-chat disposition)

**Verdict: CONCUR with NO-GO (3 CRIT, 6 HIGH).** The audit is correct on the findings I can ground, and CRIT-1 is a repeat of my own failure. This triage does two things: names the pattern and quarantines its cause, then dispositions the findings — splitting them into "fixable now" and "blocked on a direct read of the paper."

## The pattern (owned, not minimized)

Three rounds, the calibration/anchor material has fabricated three times, all mine, all the same mechanism: **characterizing a complex, heterogeneous paper (Bartlett et al.) from fragments — working-paper numbers, memory, or audit summaries — instead of the published tables read directly.**
- Round 1: verification log invented "col (2) ≈ 6.95 / Table 4 Panel A."
- Round 2: §9 used working-paper 7.88/$765M under a JFE cite.
- Round 3 (this one): §9's premise for dropping the anchor — "excludes CRA tracts, excludes FHA, note-rate, GSE-grid" — is the **2019 working paper's description**. Audit-2 already refuted the CRA half in writing; my AUDIT-2-TRIAGE accepted the refutation and then **re-asserted "excludes CRA tracts" in Decision A**; v3 shipped it. The false description survived the audit that killed it and became the reversal's premise.

**This will not be fixed by me rewriting the Bartlett paragraph from memory again — that action IS the bug.** Structural fix below.

**Compounding evidence it can't be done from fragments:** Audit-2 and Audit-3 **contradict each other on FHA** — Audit-2 (reading the accept/reject sample-construction text) said Bartlett *excludes* FHA; Audit-3 (reading the abstract + Table 10) said it *includes* FHA. Both quoted the paper. The resolution is that the paper runs multiple samples across multiple tables, and no single-clause characterization is true. Even the two hostile audits can't settle it from their respective fragments. Only a comprehensive direct read resolves it.

## Structural fix — quarantine Bartlett from memory-based drafting

**No specific claim about Bartlett's design, samples, tables, footnotes, coefficients, or SEs enters v4 from memory, from a working paper, or from an audit summary.** It enters only from the **published paper's relevant sections read directly** — the data/design section, Table 6 (CRA tracts), Table 10 (the 2018/2019 public-HMDA, points-controlled, lender-clustered, tract-credit-decile spec the auditor identifies as the tool's closest analog), and footnotes 31 and 33 — with the Audit-2/Audit-3 FHA contradiction explicitly reconciled. Until that read happens, §9 and §12 carry an explicit **`OPEN — BLOCKED ON DIRECT READ`** marker and no Bartlett-derived number.

This is the two-place dependency the audit surfaces: **§9** (anchor/uncalibrated justification) and **§12** (the CI-width precision bound can only be set from an external study's SEs at known n — the audit is right that v3 wants Bartlett "too mismatched for magnitude but close enough for precision," which is incoherent as stated and only resolvable against the true tables). Both wait on the read.

## Finding disposition

### CRITs
| # | Finding | Disposition |
|---|---|---|
| CRIT-1 | §9's drop-the-anchor premise is false against the paper (CRA tracts analyzed not excluded; FHA disputed; the description is the WP's) | **ACCEPT.** Quarantine (above). §9 anchor justification → `OPEN — BLOCKED ON DIRECT READ`. The uncalibrated decision may still be *right*, but it must be reached from the true wedges, not false ones. |
| CRIT-2 | `is_arm` "NA → fixed (0)" fabricates: §1003.3(d)(4) à-la-carte partial exemption lets a lender report rate_spread but omit intro_rate_period ((a)(26) not on the all-or-nothing list), so the row passes the exempt filter and an ARM is modeled as fixed | **ACCEPT — fixable now.** `intro_rate_period` NA is **unresolvable** (no other clean fixed/ARM signal in the public LAR) → **exclude-with-reason `na_intro_rate_period`**, never default to fixed. Do not derive certainty from an ambiguous NA. |
| CRIT-3 | `protected_class` (β_pc, the coefficient of interest) has NO §6 rule; `derived_race` has four ungoverned states; Race-Not-Available silently into the White reference biases β_pc with no trace, and §12 names a lender on it | **ACCEPT — fixable now.** Add a full §6 row + §11 reason for the protected-class construction: Race-Not-Available / Free-Form-Only → exclude-with-reason `na_race` (NEVER into reference); reference category explicit; "Joint" and "2+ minority races" → explicit documented policy; ethnicity separate. This is the coefficient of interest — it was ungoverned. |

### The three reversals (audit rulings — accept)
- **Uncalibrated + synthetic recovery — does NOT survive as written.** Accept. Two fixes, both **fixable now** (not Bartlett-dependent): (1) synthetic recovery is not "the honest analogue of calibration" — drop that claim; it tests the estimator, not the world, and the two are disjoint. (2) The δ=0 check must actually test §8's clustering: the generator **must plant a lender random effect + Herfindahl-heavy imbalance**, plus an **HC1 negative control that must over-reject** (so a silently-dropped `cov_type='cluster'` fails the check). The real failure that passes all of v3's checks — OVB producing 15 bps on a lender whose minority applicants have lower scores — must be named as an explicit non-detectable-by-this-tool limitation. And the ±100 bps plausibility ceiling is ~10× too wide to ever fire — the dev-time drift check the anchor provided is NOT replaced by synthetic recovery (couples to §9/§12).
- **Points removed — right for the primary, disclosure half dropped.** Accept. Premise verifies (§1026.4(b)(3)). Fixes **fixable now**: (a) "net-of-points" language is **backwards** — APOR is itself points-inclusive (§1026.35(a)(2)) and APR amortizes points over full term while loans prepay ~7yr, so rate_spread *dampens* the fee channel, it doesn't capture it. Correct the language. (b) The points channel being under-captured is a **real limitation** (Bartlett's cited lit: Black borrowers pay more in points conditional on rate — exactly what rate_spread compresses), not something "disclose" resolves. State it as a limitation; decide costs-as-secondary-outcome vs explicit honest scope-out.
- **2018+ gate — sound, verified (govinfo 2017 CFR §203.4(a)(12)(i)).** Accept. Fix **fixable now**: §5 "HARD GATE" (raises, no reason code) contradicts §11's `pre_2018_excluded` reason code. Pick one: pre-flight validation raise on any pre-2018 data (like `data_year` validation — remove `pre_2018_excluded` from §11), OR row-level reason-coded exclusion if mixed years allowed. Decide and make them consistent.

### `{1,2}` — the flagged maybe-not-deferrable question: RESOLVED favorably
The audit closed it against the CFR text: every §7 regressor is application-side — (a)(7) "or the amount applied for", (a)(28) "proposed to secure", (a)(26) "proposed number of months", (a)(23)/(a)(24) "relied on in making the credit decision." **`{1,2}` does NOT collapse.** Accept; close the BUILD-RECON with those cites. **But** two fixes **fixable now**: (1) restore the dropped non-degeneracy guard (Audit-2 CRIT-3 fix 3). (2) action-2 rate_spread comes from the **Loan Estimate** APR, action-1 from the **Closing Disclosure** APR (Cmt 4(a)(12)-8) — a **measurement difference**. §4's interpretation rule ("divergence ⇒ selection is doing real work") is wrong as stated: divergence conflates selection with LE-vs-CD measurement drift. Rewrite the interpretation to separate the two; v3 replaced v2's false-negative with a false-positive carrying a causal label.

### Other verified defects (all fixable now)
- `lien_status` cited to (a)(33) — wrong; correct is **(a)(14)**. (a)(33) is the application-channel/optional field; (a)(14) is required. New defect introduced by the §6 extension. Fix the cite.
- `debt_to_income_ratio` bins cited to (a)(23) which requires a *continuous* ratio; the public-file column is a **binned Alphanumeric construct** — Audit-2's "forbid numeric coercion" was dropped and must be restored (coercion silently deletes the tails).
- `loan_to_value_ratio ≤ 100` filters **a field that doesn't exist** in the public LAR — the CLTV field is `combined_loan_to_value_ratio` (a)(24). Fix the field name or remove the filter.
- **Partial exemption (§1003.3(d)) is absent entirely** — add à-la-carte handling. **This is a durable portfolio gotcha** (same class as the `1111` and sentinel notes): a partially-exempt lender can report any subset of non-core fields, so EVERY optional field needs an exempt path. Belongs in project knowledge / working principles, not just this doc.
- `derived_msa-md` non-MSA encoding: the auditor could not verify a sentinel and left it unasserted (correct behavior). MSA also has no §6 row. `[BUILD-RECON: confirm the public-file non-metro/blank encoding for derived_msa-md before it becomes an MSA-FE regressor.]`

## Plan
1. **v4 now** — fix everything marked *fixable now* (CRIT-2, CRIT-3, both reversal-fixes that aren't Bartlett-dependent, `{1,2}` measurement-drift, the CFR-citation cluster, partial-exemption). §9 anchor-justification and §12 CI-width → `OPEN — BLOCKED ON DIRECT READ`, no Bartlett number.
2. **Direct read of Bartlett** (the gate before §9/§12 finalize and before Audit-4): data/design section + Table 6 + Table 10 + fns 31/33, FHA contradiction reconciled. See the decision I need from Jay.
3. Then finalize §9/§12 from the true description → Audit-4.

## Decision needed from Jay
How to do the direct read (see chat) — provide the PDF so I read it in-repo, or have the Claude Code session (which already has it extracted with pypdf) produce a verified design description I incorporate. Either way, **I do not write Bartlett from memory again.**
