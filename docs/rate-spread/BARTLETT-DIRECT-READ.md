> # ⚠ RETRACTION (Audit-4, verified) — read this first
> This memo's dismissal of Audit-3's numbers was WRONG. It said the accepted-manuscript figures "are NOT verifiable … may be unreliable; I will not use them." They are verifiable, and I have now confirmed them by fetching `faculty.haas.berkeley.edu/stanton/pdf/discrim.pdf` directly:
> - **Table 10 exists** — "Interest-rate differentials: 2018/2019 HMDA data controlling for points paid/total loan costs" (Audit-3's 7.377→7.820 points result and 4.043/6.431 CRA figures are in this document).
> - **fn31, verbatim:** "we include controls for individual income here along with census-tract-level credit scores, because the **HMDA data do not include individual credit scores**" — the tool's exact handicap.
> - **Abstract:** "$450 million yearly," "both GSE-securitized and FHA-insured loans."
>
> **Audit-3's CRIT-1 is UPHELD.** The §9 "version-independent" claim built on this memo is false (see `AUDIT-4-TRIAGE.md`). The error below was reading the WORKING PAPER and dismissing the accepted manuscript whose URL was already supplied. Two locator errors also corrected: lender FE is **Table 4** (not Table 5); the WP also has an **Appendix Table 1**. The working-paper facts below remain accurate *for the working paper* — the failure was extrapolating "version-independent" to a document I had not read.

# Bartlett et al. — Direct Read (from the actual PDF)

**Read July 14 2026 from `SSRN-id3491267.pdf` (44pp) — this is the 2019 WORKING PAPER (w25943). The accepted manuscript (76pp, $450M, adds Table 10 / FHA) is the DIFFERENT version that contains the close analog — see retraction above.**

## The finding that dissolves the three-round problem: this file is the 2019 WORKING PAPER, not the published JFE.

Page 2 header, verbatim: **"Consumer-Lending Discrimination in the FinTech Era … NBER Working Paper No. 25943, June 2019."** `SSRN-id3491267` is a re-host of NBER w25943 — the exact version I warned not to use as authoritative. The published JFE 2022 (143(1):30–56) is a *different, revised* document I still do not have.

This is why every round tangled: **there are two substantially different versions, and neither the drafting nor the audits kept them straight.**

## What the working paper ACTUALLY says (directly read, no fragments)

**Pricing analysis — Table 2 (this is the real table; "Table 4 Panel A" was a mislabel):**
| | (1) raw purchase | (2) full model purchase | (3) raw refi | (4) full model refi |
|---|---|---|---|---|
| Latinx-/African-American | 0.000903*** | **0.000788*** (7.88 bps)** | 0.000298*** | **0.000356*** (3.56 bps)** |
| SE (lender-clustered) | [0.000102] | **[3.11e-05]** | [7.98e-05] | [2.92e-05] |
| Obs | 1,495,021 | 1,495,021 | 2,081,989 | 2,081,807 |
| Month-Year FE / GSE Grid FE | N | Y | N | Y |

- **DV = mortgage interest rate (note rate)**, verbatim "Dependent Variable: Mortgage Interest Rate" — NOT APR, NOT rate_spread.
- **Sample:** GSE-securitized, 30-yr fixed, **conventional (excludes FHA/VA/FSA/RHS)**, conforming, **2009–2015**, and **"eliminate … any loans made within a census tract covered by the** Community Reinvestment Act." Pricing N = 3,577,010.
- **Identification:** 72 GSE-grid FE (credit score × LTV) + month-year FE. Credit score & LTV observed via McDash-Equifax merge, controlled by grid.
- **Group:** pooled Latinx-/African-American indicator (mean 11.0%).
- **Aggregate: $765.47M** (Table 2 Panel B). Lender FE is a *robustness* check (Table 5 col 3/4), not the headline spec.
- **Tables 1–8 only. No Table 10. No 2018/2019 public-HMDA points analysis in this version.**

## Corrected record — what was actually wrong, on all sides

**My real errors (owned, precisely):**
1. **The fabricated number stands as fabricated:** I wrote "Table 4 Panel A col (2) ≈ 6.95 bps." The real figure is **Table 2 col (2) = 7.88 bps**; 6.95 appears nowhere in any version. That was invention. Confirmed.
2. **The citation was the error, not the description:** my v2/v3 anchor *description* (note-rate DV, GSE grid/credit-score control, conventional excl-FHA, 2009–2015, excludes CRA tracts, pooled group) is **correct — for the working paper.** My mistake was citing it to "JFE 143(1):30–56," a version that differs ($450M, adds FHA). Citing the published version while using working-paper facts is what made it fabrication-class.

**What the audits got wrong (version conflation, stated fairly):**
- **Audit-3's CRIT-1 is wrong against this document.** It declared "excludes CRA tracts" and "excludes FHA" *false*; the working paper explicitly does **both** (quoted above). Audit-3 was evidently reading the *published* version (which adds FHA per its abstract, and reports $450M) and presented that as refuting a working-paper description — conflating the two.
- **Audit-3's specific numbers — Table 10, 6.431/4.043 (CRA), 7.377→7.820 (points) — are NOT verifiable.** None appear in the working paper. They may be from the published version or may be unreliable; **I will not use them.**
- Audit-2 and Audit-3 contradict each other on FHA precisely because they read different versions.

**Net:** the three-round "anchor keeps fabricating" problem was, at root, a **two-versions problem** no one diagnosed until the PDF was read directly. The lesson holds exactly as stated — read the actual source — it simply also revealed the audits were mixing versions.

## Consequence for the methodology (verified basis for §9 / §12)

**Uncalibrated remains correct, and is now backed by directly-read text.** The tool cannot replicate Bartlett's estimand in ANY version: the tool is APR-spread, pooled public HMDA, **2018+**, **Black-only default**, with **no individual credit scores** and **no GSE grid**. Bartlett's 7.88 bps is a credit-risk-controlled residual on the *note rate* within GSE grid cells — a different quantity. There is no valid mapping from the tool's coefficient to 7.88 bps. So §9 asserts **no magnitude target**, and cites Bartlett only to *illustrate* the mismatch, with these verified wedges.

**§12 CI-width bound — sever from Bartlett.** The working paper's SE (3.11e-05 ≈ 0.31 bps at n≈1.5M, lender-clustered) is a note-rate/GSE-grid precision context, not portable to the tool's design. Derive the CI-width suppression threshold from the tool's **own synthetic power analysis** (§9 recovery harness) instead — this removes the last Bartlett dependency entirely.

## The one genuinely open question (needs the PUBLISHED typeset)
Independent sources say the **published JFE** added FHA analysis and reports **$450M**; Audit-3 referenced a 2018/2019 public-HMDA points analysis ("Table 10"). **If** the published version contains a 2018/2019 pooled public-HMDA analysis, that would be a *closer* analog and worth acknowledging (though still credit-score-proxied and possibly note-rate). This cannot be resolved from the working paper. Options: (a) get the ScienceDirect typeset and I read it; (b) proceed with uncalibrated §9 as written — it holds against any version because the tool's core mismatches (2018+, Black-only, no credit scores) are version-independent — and footnote the published 2018/2019 analysis as an unverified potential-analog.
