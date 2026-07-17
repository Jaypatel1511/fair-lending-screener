# Audit-4 Triage — v0.3.0 Rate-Spread Methodology (planning-chat disposition)

**Verdict: CONCUR with NO-GO (4 CRIT, 3 HIGH).** This is the strongest audit of the four. I verified its central claim (CRIT-1) myself by fetching and reading the accepted manuscript — it holds. Two CRITs are mine; one (CRIT-4) is a genuine core-identification problem that reframes the whole feature. This triage owns the failures precisely, accepts the findings, and surfaces the one strategic decision that gates v5.

## CRIT-1 & CRIT-2 — mine, owned, verified against the source this time

I fetched `faculty.haas.berkeley.edu/stanton/pdf/discrim.pdf` (accepted manuscript) and confirmed directly:
- **Table 10**: "Interest-rate differentials: **2018/2019 HMDA data** controlling for points paid/total loan costs."
- **fn31, verbatim**: "We include controls for individual income here along with census-tract-level credit scores, because the **HMDA data do not include individual credit scores.**"
- **Abstract**: "**$450 million** yearly," "both GSE-securitized and **FHA-insured** loans."

**Therefore §9's "version-independent" claim is FALSE.** Two of the four wedges break: identification (Table 10 has the tool's exact no-individual-credit-scores handicap) and era (2018/2019 = the tool's era, same data source). Surviving wedges: outcome (Table 10 DV = note rate in bps, tool = APR-spread) and group (pooled vs Black-only, a config difference) — plus Table 10 controls for points and uses lender×year FE (ties to CRIT-4).

**This is the fourth occurrence of the signature failure, and the worst form: a fabricated *confirmation*.** I asserted version-independence about a document I stated I had not read, when Audit-3 had supplied the URL in plain text and my own earlier searches this session already surfaced the 2018/2019 points analysis. Last round I compounded it by writing that "Audit-3's CRIT-1 is wrong against this document" — I had read the *working paper* and dismissed the *accepted manuscript's* verified numbers as "may be unreliable; I will not use them."

**Retraction (CRIT-2 fix):** `BARTLETT-DIRECT-READ.md` is corrected at its head — the "not verifiable" dismissal is withdrawn, Audit-3's CRIT-1 is restored as UPHELD, and Audit-3's numbers (Table 10 7.377→7.820; Table 6 CRA 4.043 vs 6.431; the summary stats) are acknowledged as verified in the accepted manuscript. Also the two locator errors: lender FE is **Table 4** (not Table 5); the working paper has an **Appendix Table 1** beyond Tables 1–8.

## CRIT-3 — derived_race miscited to (a)(5) [construction method]. ACCEPT.
Verified structure: (a)(5) = construction method (and it *collides* with the tool's own `construction_method == 1` filter — a builder could mis-wire); (a)(10)(i) = ethnicity/race/sex. **`derived_race` is not a CFR data point at all** — it is an FFIEC public-file *derived* field (from (a)(10)(i) + Appendix B), nine FFIEC-defined values. Fix in §6 and §14: cite it as the FFIEC derived field, not a CFR paragraph. The coefficient of interest was miscited — exactly the field §6's premise says can't be left ungoverned.

## CRIT-4 — no defined estimand; §12 names a lender off a market-level coefficient. ACCEPT — this is the real one.
§7 fits one pooled β_pc, MSA FE, **no lender FE, no lender interaction**; §8 clusters on `lei`; §12 names a lender when the pooled CI excludes zero. **A market-average coefficient cannot identify a firm.** Bartlett proves it with its own specs: WP Table 4 adding lender FE moves 7.88 → 5.45 bps (~31% is between-lender sorting); the accepted-MS 2018/2019 analysis uses lender×year FE throughout. The auditor's worked failure is correct: Lender A prices identically by race (δ_A=0) but is a high-cost channel with a disproportionately Black book → pooled β_pc = +12 bps, every §9/§12 gate passes, Lender A is named. And §9's generator *cannot* surface it, because a random lender effect is orthogonal to protected-class share by construction, while real sorting is exactly that correlation. **This is not a text fix — it changes the tool's core.**

## HIGH-1/2/3 — ACCEPT
- **HIGH-1 multiplicity:** per-comparison α=0.05 across a market of N lenders names ~5%·N innocents by construction. No multiple-testing control anywhere. Needs family definition + Benjamini–Hochberg FDR; suppress unless adjusted q<0.05; disclose the number of hypotheses. Independent of CRIT-4.
- **HIGH-2 "examiner methodology" brand claim unsourced:** §14 cites zero supervisory sources. Flagged unsourced, not false. For a permanent-PyPI advocacy tool this is the largest credibility exposure. Cite the FFIEC Interagency Fair Lending Examination Procedures for the specific method, or drop the claim. `[I have NOT verified what the exam procedures actually say — must confirm before citing, not assert from the tagline.]`
- **HIGH-3 CI-width is a variance gate on a bias problem:** larger n → tighter CI → gate opens → bias unchanged. It controls the error the design doesn't have (variance) and ignores the one it does (OVB, which §9 concedes is undetectable). The auditor's replacement (Oster δ-style OVB sensitivity) is the right *kind* of gate. Accept.

## MED/LOW — ACCEPT (all verified by the auditor)
MED-1 (open-end HELOC has no §5 filter and carries a real comparable-transaction rate_spread — the pricing analogue of the signature failure; add `open_end_line_of_credit==2` + `reverse_mortgage==2` filters, Exempt paths); MED-2 (no reason-code precedence → partial-exemption row gets 6 codes, breaks the identity; add deterministic first-wins precedence + exclusivity assert); MED-3 (lien_status row has a provenance note, not a rule; state always-required, no Exempt); MED-4 (is_arm NA is 3-way — add Cmt 4(a)(26)-2 preferred-rate); MED-5 (§9 wedge (c) misattributes the accept/reject FHA filter to the pricing sample — same conflation that started the whole fight; state it as implication, not quoted filter). LOW-1/2/3 accepted.

## The [SET IN AUDIT-4] rulings are an excellent build spec — adopt (verify the memory-cited stats refs)
G_eff = inverse-Herfindahl effective clusters, floor ~30; wild-cluster bootstrap-t (Webb, null-imposed) for 10≤G_eff<30, hard-suppress <10; condition number on the **partialled-out** design (not raw, or the MSA-FE block fires it mechanically); **replace the CI-width gate** with within-lender estimand + FDR + per-lender G_eff + **Oster δ OVB sensitivity (suppress if δ<1)**; anchor-free plausibility ceiling (|β|>100bps OR >IQR(rate_spread)); **costs-as-outcome scope-out ACCEPTABLE but forces relabeling the output from "pricing disparity" to "rate-channel (APR-spread) disparity"**; per-LEI reportability test for is_arm (if an LEI ever reports non-NA intro_rate_period its NA rows are genuine → is_arm=0 safe; 100%-NA LEI → exclude). Statistics refs (Cameron–Miller, Oster 2019, Belsley–Kuh–Welsch, Carter–Schnepel–Steigerwald) are the auditor's from memory — **verify before the build adopts thresholds.**

## The strategic decision that gates v5
CRIT-4 + HIGH-1 + HIGH-3 all cluster on **one feature: naming a lender.** That feature is the single highest-risk surface in the package (a public accusation, permanent PyPI, advocate users). Two coherent paths — this is Jay's call (chat):
- **A — Redesign to a within-lender estimand** (lender FE + protected_class×lender interaction, or per-lender runs) + FDR multiplicity + Oster OVB gate. Keeps lender-naming, defensibly. Substantial new methodology; each piece earns its own audit.
- **B — Scope lender-naming OUT of v0.3.0.** Ship a market-level adjusted rate-channel disparity as a screening signal that **names no lender**. CRIT-4, HIGH-1, and most of HIGH-3 dissolve (nothing is named). Smaller, honest, faster; lender-level identification defers to a later version. Matches the tool's conservative "screening signal, not a finding" posture.

## Process rule (added to working principles)
**When a prior round names a retrievable source, retrieving it is mandatory before contradicting it.** Round four fabricated a confirmation because I applied "read the actual PDF" to the wrong PDF and dismissed the right one — whose URL was in hand. `curl` took four seconds.
