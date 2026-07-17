# AUDIT-3 — Hostile methodology audit of `methodology-v3-rate-spread.md`

**Auditor stance:** adversarial. Every citation and number treated as unverified until I fetched and read the primary source myself. Nothing accepted on Audit-1's, Audit-2's, or the triage docs' authority. Sources fetched with `curl`, text extracted locally, operative sentences quoted below. Where a source was not reached, it is stated.

---

## VERDICT: **NO-GO** — 3 CRIT, 6 HIGH open.

The 2018+ hard gate (reversal c) is **correct and now verified against the actual pre-2018 regulation** — stronger evidence than any prior round had. The `{1,2}` premise (reversal c's sibling) **verifies from the CFR and does not need build-recon**; the doc is more pessimistic than the reg text warrants. The points reversal (b) is **directionally right for the primary spec** but its disclosure half was silently dropped.

But the anchor reversal (a) is defended with a **description of the anchor paper that is false in three of four clauses**, drawn from the superseded 2019 working paper, **explicitly refuted by Audit-2's own verified extraction**, and re-asserted in the triage that ordered the reversal. That is the house's signature failure mode — WP-vs-published substitution in calibration material — for the **third consecutive round**, and this time it is not a stray number: it is the load-bearing justification for removing the tool's only external error check.

Separately, the §6 table's own completeness claim is false, and the field it omits is **β_pc itself**.

---

## CRIT

### CRIT-1 — §9's justification for dropping the anchor is false against the anchor. Third occurrence of the thread's signature fabrication, in calibration material, and this time it is load-bearing.

**What's wrong.** §9, verbatim:

> *"The most-cited benchmark (Bartlett et al.) uses the note-rate outcome, a GSE credit-score/LTV risk grid, conventional-conforming 30-yr fixed 2009–2015, and **excludes** CRA tracts — a fundamentally different estimand."*

I extracted the accepted manuscript (`faculty.haas.berkeley.edu/stanton/pdf/discrim.pdf`, May 4 2021, 76pp) myself. Clause by clause:

| §9 clause | Verdict | Primary-source evidence (my extraction) |
|---|---|---|
| "note-rate outcome" | ✅ **TRUE** | Table 10 DV row: *"VARIABLES Interest rate"*. `APOR` = **0 occurrences** in the paper. |
| "**excludes** CRA tracts" | ❌ **FALSE** | Table 6 is *"Interest-rate differentials by CRA status"*; FE row *"CRA FE Y Y Y Y"*; summary stats carry *"CRA census tract"* (mean .0926 all / .1782 GSE). The string *"eliminate from our sample"* — the WP's CRA-exclusion sentence — is **NOT FOUND** in the accepted MS. |
| "conventional-conforming" | ❌ **FALSE** | Abstract: *"risk-equivalent Latinx/African-American borrowers pay significantly higher interest rates on **both GSE-securitized and FHA-insured loans**"*. Tables 6 and 10 both carry co-equal **FHA Loans** columns (FHA purchase N = 655,261). |
| "2009–2015" | ❌ **INCOMPLETE, and the omission is the whole point** | Internet Appendix I1.4.2: *"the data for the pricing regressions are sourced from the merged HMDA, ATTOM, McDash/Equifax data from 2009 through 2015. As discussed in Section 6, **we extend our analysis of GSE and FHA mortgage pricing by including controls for the effects of loan points, total loan costs, and lender credits that are available in the recently released 2018 and 2019 HMDA data.**"* |

**Table 10, extracted verbatim by me** — *"2018/2019 HMDA data"*, lender-clustered:

```
                        GSE Purchase   GSE Refi
(a) no points/costs      7.377***       5.998***    R² 0.376 / 0.483
                        (0.472)        (0.392)
(b) controlling points   7.820***       6.900***    R² 0.386 / 0.493
                        (0.482)        (0.375)
(c) total loan costs     7.709***       6.806***
```
FE: Lender × year; Point decile × year; Cash-out × LTV decile × year; Cash-out × credit decile × year; Amount decile × year; Cash-out × income decile × year.
fn 31: *"We include controls for individual income here along with **census-tract-level credit scores, because the HMDA data do not include individual credit scores**."*

**Why it matters.** §9's premise is *"No published study shares this tool's design."* The paper it names to prove that contains a **2018/2019 public-HMDA specification with no individual credit scores** — the tool's exact data source, exact vintage, and exact credit-score handicap — which §9 does not mention while describing the paper as a 2009–2015 GSE-grid study. Three of the four clauses that make the anchor look unusable are false, and **every falsehood points the same way**: toward "no anchor exists, therefore drop it." A justification whose errors all favor the conclusion is not a clerical problem.

**The provenance is traceable and damning.** The false description is the **2019 NBER working paper's** design (w25943, which *does* say *"We additionally eliminate from our sample any loans made within a census tract covered by the Community Reinvestment Act of 1977 (CRA), given the potential bias these census tracts would introduce"*). The chain:
1. `AUDIT-1-TRIAGE.md` asserts *"the paper explicitly excludes FHA/VA/USDA, is 30-yr fixed only, 2009–2015, and excludes CRA tracts"* — the WP's design, stated as "the paper."
2. `AUDIT-2-HOSTILE-FINDINGS.md` **refutes it** at verification row 5c: *"✅ HELD for the 2019 WP — ❌ **refuted for the published paper, where FHA is co-equal and CRA tracts are included and analyzed**"*, and HIGH-3 proves disparities are **larger** in CRA tracts (6.431 vs 4.043, p = 0.0000 — which I re-extracted and confirm).
3. `AUDIT-2-TRIAGE.md` **accepts** HIGH-3 (*"CRA wedge is backwards"*) — and then, in Decision A, **re-asserts the refuted description** as the reason to drop the anchor: *"Bartlett's design (GSE-grid risk-equivalence, **excludes CRA tracts**, note-rate outcome) is fundamentally different… is Bartlett even the right anchor?"*
4. v3 §9 encodes it as settled fact.

So the description **survived the audit that refuted it**, inside the same document that accepted the refutation, and then became the premise for the reversal.

**It also violates the rule adopted one revision ago.** `AUDIT-2-TRIAGE.md`, verbatim: *"**Hard rule now (not a nicety): the calibration section may be drafted ONLY from the published JFE tables read directly. No working-paper numbers, no memory, no search snippets, no derived table cells. If the published tables aren't in hand, the calibration section stays explicitly UNRESOLVED.**"* §9 was drafted from neither the published tables nor the accepted MS — it reproduces the WP description. The rule was written for exactly this section and did not survive one revision.

**Ruling on the reversal — it partially survives, but not as written.** Steelmanning: real wedges remain even against Table 10(b) (note-rate DV vs APR−APOR; lender×year FE vs none; tract-credit-decile control vs none; GSE-only vs all-conventional; pooled Latinx+African-American vs Black-only). Audit-2 conceded the wedges are *"directional, not quantified"*. A 5–16 band built from five unquantified wedges is arguably false precision, and §9 is right that a dev-time band never protects a named lender at runtime. **So "uncalibrated-and-disclosed for the runtime estimate" is defensible.** What is **not** defensible:
- justifying it with false statements about the source — that is independent of the decision and must be fixed either way;
- **removing the dev-time national-pooled check with nothing that replaces its function.** Its job was never to gate a lender; it was to catch engine drift on the pooled run. Synthetic recovery cannot do that job (CRIT-2 of §9's logic — see HIGH-3). The ±100 bps ceiling nominally fills it and is ~10× too wide to fire (MED-8).

**Fix (required).**
1. Delete §9's Bartlett paragraph and rewrite it **only** from the accepted MS / published tables read directly. State: note-rate DV (true); FHA co-equal; CRA tracts **included and analyzed, with larger disparities**; base 2009–2015 **plus a 2018/2019 public-HMDA extension (Table 10) with tract-level credit proxies and no individual credit scores**.
2. Re-decide the anchor question **against the true description**. If the answer is still "uncalibrated," it must be argued from the *real* wedges (DV, lender FE, GSE-only, pooled group), not from invented ones.
3. Restore a **dev-time, national-pooled, engine-drift band** centered on Table 10(b) (~7.8 purchase / ~6.9 refi) at honest ±50% width — explicitly labeled drift detection, never a runtime gate, never in output. Keep "uncalibrated-and-disclosed" for the runtime estimate. These are not in conflict.
4. If the published tables are not in hand at write time, §9 stays **UNRESOLVED** — per the rule the thread already adopted.

---

### CRIT-2 — `is_arm`'s `NA → fixed (0)` fabricates a value for the Exempt state. The portfolio's signature failure, reproduced inside the field added to fix the last CRIT.

**What's wrong.** §6, verbatim: *"**derive `is_arm`**: real number → ARM (1); **NA → fixed (0)**."*

The `intro_rate_period` row is the **only** row in §6's table with two states. Every other row reads *"NA/Exempt → exclude-with-reason."* §6's own header demands *"three states (real-value / NA / Exempt)"*. The Exempt state is missing — and `NA → fixed (0)` is an **imputation**, not an exclusion.

**Reg C NA for (a)(26) has at least three causes, not one — verified:**
1. **Fixed rate** — Cmt 4(a)(26)-3, verbatim: *"A financial institution complies with § 1003.4(a)(26) by reporting that the requirement is not applicable for a covered loan with a fixed rate or an application for a covered loan with a fixed rate."* → `is_arm = 0` is **correct** here.
2. **Partial exemption** — Cmt 4(a)(26)-1 opens: *"**Except for partially exempt transactions under § 1003.3(d)**, § 1003.4(a)(26) requires…"* → reads `Exempt`, **not** fixed-rate.
3. **Preferred rates** — Cmt 4(a)(26)-2, verbatim: *"Section 1003.4(a)(26) does not require reporting of introductory interest rate periods based on preferred rates unless the terms of the legal obligation provide that the preferred rate will expire at a certain defined date. Preferred rates include terms… that provide that the initial underlying rate is fixed **but that it may increase or decrease upon the occurrence of some future event**…"* → NA on a loan whose rate **can change**.

**The escape hatch that makes cause 2 live — this is the part that matters.** The obvious objection is *"a partially exempt lender doesn't report `rate_spread` either ((a)(12) is optional data), so §6 excludes the row before `is_arm` ever runs."* That objection **fails**, and the CFR says why:

- §1003.3(d)(1)(iii), verbatim: *"**Optional data** means the data identified in § 1003.4(a)(1)(i), (a)(9)(i), and **(a)(12), (15) through (30), and (32) through (38)**."* → both `rate_spread` (a)(12) and `intro_rate_period` (a)(26) are optional data.
- §1003.3(d)(4), verbatim: *"A financial institution eligible for a partial exemption under paragraph (d)(2) or (3) of this section **may** collect, record, and report optional data… as though the institution were required to do so, **provided that**: … (ii) If the institution reports any data for the transaction pursuant to **§ 1003.4(a)(15), (16), (17), (27), (33), or (35)**, it reports all data that would be required by [those], respectively…"*

Voluntary reporting is **à la carte per data point**. The all-or-nothing constraint covers only (a)(15), (16), (17), (27), (33), (35). **(a)(12) and (a)(26) are not in that list.** So a partially exempt insured depository or credit union **may lawfully report `rate_spread` while omitting `intro_rate_period`.** That row:
- passes §6's `exempt_rate_spread` exclusion (rate_spread is real),
- hits `NA → fixed (0)`,
- **is modeled as a fixed-rate loan when it may be an ARM**,
- is counted in `classified`, so `classified + excluded + reassigned == universe` **holds exactly**.

That is silent substitution of a fabricated value on a sentinel, surviving the reconciliation identity — the portfolio's signature failure, in the pricing analogue, in the field v3 added and labeled *"(Resolves the CRIT.)"*

**Why it matters.** ARMs and fixed-rate loans are different pricing regimes; `is_arm` is the dummy separating them. Misclassification is non-random: it concentrates in small insured depositories and credit unions — **precisely the CDFI-adjacent lenders this tool exists to screen**. And the direction is uncontrolled.

**Fix.**
1. Three states, explicitly: **real number → ARM (1)**; **NA *for the fixed-rate reason* → fixed (0)**; **`Exempt` → exclude-with-reason (`exempt_intro_rate_period`)**. Never coerce; never let `Exempt` fall into the NA branch.
2. Add `exempt_intro_rate_period` to §11's vocabulary.
3. Mutation tests that **bite**: a fixed-rate NA must survive as `is_arm = 0`; an `Exempt` must **exclude**, not become 0; a real number must become 1.
4. Disclose the preferred-rate conflation (cause 3) in §13 — small volume, but it is a real NA cause that `is_arm` cannot distinguish.

---

### CRIT-3 — §6 claims every §7 regressor has a rule. The one it omits is the coefficient of interest.

**What's wrong.** §6, verbatim: *"**Every regressor in §7 has an explicit row** — a field without a rule is a silent-imputation/silent-drop hazard."*

Enumerating §7's equation against §6's table:

| §7 regressor | §6 row? |
|---|---|
| `β_pc · protected_class` | ❌ **ABSENT** |
| `log(loan_amount)` | ✅ |
| `combined_LTV` | ✅ |
| `Σ DTI_bin` | ✅ (but wrong source — HIGH-5) |
| `log(property_value)` | ✅ |
| `log(income)` | ✅ |
| `Σ lien_status` | ✅ (but wrong cite — HIGH-4) |
| `loan_term` | ✅ |
| `is_arm` | ✅ (but two-state — CRIT-2) |
| `Σ MSA` | ❌ **ABSENT** (MED-6) |

**`protected_class` is never defined anywhere in v3.** It appears exactly once, in the §7 equation, as `protected_class_i`. No field name, no cite, no reference category, no §6 row, and **no reason code in §11**. The doc's own stated hazard rule condemns it.

This is not academic. FFIEC public LAR `derived_race`, verbatim values: *"American Indian or Alaska Native | Asian | Black or African American | Native Hawaiian or Other Pacific Islander | White | **2 or more minority races** | **Joint** | **Free Form Text Only** | **Race Not Available**"*. `derived_ethnicity`: *"Hispanic or Latino | Not Hispanic or Latino | **Joint** | **Ethnicity Not Available** | **Free Form Text Only**"*. `applicant_race-1` carries codes **6** (*"Information not provided by applicant in mail, internet, or telephone application"*) and **7** (Not applicable).

So the outcome-defining variable has **four non-comparison states**, none governed. Whatever the code does with "Race Not Available" — drop it, or worse, coerce it into the reference category with White — happens **unspecified and unreason-keyed**. Race-not-available is a large, non-random share of HMDA (it varies by channel, by lender, and by whether the application was taken in person), and if it silently lands in the White reference group, `β_pc` is biased by construction with no trace in the identity.

**Why it matters.** §6 exists to prevent exactly this, asserts it has done so, and has not. A reviewer who checks the doc's central safety claim against the doc's central coefficient finds the claim false on the first try. Given that §12 will attach a **named lender** to `β_pc`, this is the least acceptable field in the model to leave unspecified.

**Fix.**
1. Add a §6 row for the protected-class field: name the exact field (`derived_race` / `derived_ethnicity`), enumerate **every** value, state the comparison group and the reference group explicitly, and give each residual state (`Race Not Available`, `Free Form Text Only`, `Joint`, `2 or more minority races`) an explicit rule — **exclude-with-reason, never fold into a reference category**.
2. Add `na_race` / `na_ethnicity` (and the Joint/FreeForm reasons) to §11's vocabulary.
3. State the v3 comparison in §2 (the denial engine's convention — Black or African American vs White, ethnicity analyzed separately, never blended — is presumably intended; the doc must say so rather than leave it inherited).
4. Add a §6 row for MSA (MED-6).
5. Mutation test per state.

---

## HIGH

### HIGH-1 — §5's "HARD GATE" and §11's `pre_2018_excluded` reason code are mutually exclusive. As written, CRIT-5 is reopened through the back door.

§5 says **`activity_year >= 2018` (HARD GATE)**. Audit-2's fix was explicit: *"**Hard-fail (raise) on any `activity_year < 2018`.** Not a warning, not a caveat."*

But §11's reconciliation vocabulary lists **`pre_2018_excluded`** as a routine reason code. A gate that raises produces no reason code — there is no surviving frame to reconcile. The presence of the code is the tell that this will be built as a **row filter**, and a row filter reopens the CRIT:

- §6's rule: blank/NA `rate_spread` → exclude as `na_rate_spread`.
- Pre-2018, a blank `rate_spread` means **priced below 1.5/3.5 pp = a real, normally-priced loan** (verified below).
- If the year filter runs *after* §6, or is missed on one path, every normally-priced pre-2018 loan exits as `na_rate_spread` and every pre-2018 **subprime-tail** loan (which has a real reported spread) is **classified and modeled**. The identity holds. The output is clean. The number is large, confident, and meaningless.

Worse in the ordinary case: hand the tool a pooled 2016–2019 file (the sibling `hmda-analyzer` is explicitly multi-year) and a filter silently drops half the request, reason-keyed, and never tells the user their analysis window was cut.

**Fix.** Raise at load, before any §6 rule runs: on `data_year < 2018` (the denial engine already raises `InvalidDataYearError` on this — reuse it) **and** on any row with `activity_year < 2018`, which indicates the data does not match the declared year. **Delete `pre_2018_excluded` from §11.** Its existence in the vocabulary is the defect.

---

### HIGH-2 — "Disclose, don't control" has no disclosure. Audit-2's other two required fixes were dropped without a stated reason, and the APR dampens the very channel §7 says it captures.

**Is the framing honest? The framing, yes. The implementation, no.**

The core reversal is sound and I confirm its premise: §1026.4(b)(3), verbatim — *"**Points, loan fees**, assumption fees, finder's fees, and similar charges"* are finance charges; §1026.4(a) — *"The finance charge is the cost of consumer credit as a dollar amount. It includes any charge payable directly or indirectly by the consumer and imposed directly or indirectly by the creditor as an incident to or a condition of the extension of credit."* Points are inside the APR; `rate_spread` is APR−APOR; conditioning on points decomposes the DV. **Removing them from the primary spec is right**, and it is better reasoned than Audit-2's with/without pair for an APR-based DV.

**But Audit-2's CRIT-1 required three things. v3 did one:**

| Audit-2 CRIT-1 fix | v3 |
|---|---|
| 1. Delete the attenuation claim | ✅ done |
| 2. Publish the model **with and without** points as a pair of bounds | ❌ dropped, silently |
| 3. Add the **costs-as-outcome** regression | ❌ dropped, silently |

Fix 2 is arguably *superseded* by the stronger argument (you cannot control for a component of your own DV, so there is no honest "with" arm). Fix 3 is **not** superseded — it is independent of the DV question, and it is the only thing that makes "disclose" mean anything. The anchor does exactly this; fn 33, verbatim (my extraction): *"As a robustness check, we also run these regressions with **total loan costs on the left hand side** and interest-rate deciles on the right. As in Panel (c) of Table 10, the estimated coefficient on the minority indicator is **significantly greater than zero in all regressions**."*

**What "disclose" currently means:** one sentence in §13 (*"a group difference in points-purchasing is part of the measured price, not removed"*). **That is a disclaimer, not a disclosure.** No output ever shows the reader the group difference in points. There is no number, no table, no artifact. A caveat that asserts a difference exists while never reporting it is the weakest possible form of the thing §7 promises.

**And the APR dampens the channel §7 claims captures it.** Two verified facts the doc misses:
- **APOR is itself points-inclusive.** §1026.35(a)(2), verbatim: *"'Average prime offer rate' means an annual percentage rate that is derived from average interest rates, **points**, and other loan pricing terms currently offered to consumers by a representative sample of creditors…"* (identically in the pre-2018 Reg C, §203.4(a)(12)(ii)). So `rate_spread` compares a points-inclusive APR to a **points-inclusive** benchmark.
- **The APR amortizes points over the full stated term.** That is the APR's design purpose: to be approximately invariant to the points/rate tradeoff. A lender steering minority borrowers into buying points therefore produces a **muted** `rate_spread` signal, and the muting is worst exactly where it matters — loans prepay in ~7 years while the APR assumes 30.

So §7's *"the tradeoff is part of the outcome, not a confound"* is true but **incomplete**: the outcome captures the fee channel **at APR-equivalence**, which understates realized borrower cost. This is not speculation — the anchor's own literature review, verbatim (my extraction): *"Courchane and Nickerson (1997) and Black, Boehm, and DeGennaro (2003) find that **black borrowers pay more in points, conditional on the loan interest rate**."* That is the exact channel, and it is the one `rate_spread` compresses.

**Answering the audit question both ways, directly:**
- **(a) Does removing points as a control let real disparity hide (under-count)?** *Partially, yes* — but **not** through the mechanism the question suggests. Removing the control is what lets steering *show*; keeping it would remove the mechanism entirely. The under-count comes from the **APR's amortization convention**, not from the control choice. Fixing the control choice does not fix the under-count. Only reporting the fee channel separately does.
- **(b) If points-purchasing differs by group for benign reasons, is "part of the price" defensible?** *Yes* — for a **screening** tool measuring what the borrower pays, benign-cause price differences are still price differences, and the tool never claims causation. The framing is legitimate. It is the missing artifact that is not.

**Fix.**
1. Restore the **costs-as-outcome** regression (Audit-2 CRIT-1 fix 3) as a published secondary: `discount_points` (and `total_loan_costs`) on the LHS. Note it runs on `{1}` only — the cost fields are Closing-Disclosure-conditioned and NA for action-2 rows (Audit-2 CRIT-3's finding, which remains true and now becomes a scope note rather than a bug).
2. Report **group means/medians of `discount_points` and `lender_credits`** beside the coefficient. This is the disclosure §7 and §13 promise and do not deliver.
3. Add to §13: the APR amortizes points over the stated term while loans prepay earlier, so `rate_spread` **compresses** the fee channel; a null pricing coefficient does not rule out a fee disparity.
4. State that either fix crosses the descriptive/inferential firewall only in appearance: these are diagnostics bound to an inferential result, so they stay in the screener and do **not** belong in `hmda-analyzer`. Say so explicitly, or the next audit will flag it.

---

### HIGH-3 — Synthetic recovery is not "the honest analogue of calibration," and the δ=0 check does not test cluster-robust inference unless the generator plants cluster correlation — which §9 does not require.

**Is it real validation or theater? Real, but for a risk the tool does not have.**

§9, verbatim: *"This validates the estimator's unbiasedness and CI coverage **without asserting any real-world magnitude.** This is **the honest analogue of calibration**: it tests the machine, not the world."*

The last clause refutes the claim in the sentence before it. **Calibration tests the world. Synthetic recovery tests the machine. They are not analogues** — they are checks on disjoint failure classes. §9 half-knows this and then uses the word "replaces" anyway (*"What replaces calibration"*). Nothing in v3 replaces calibration. The honest statement is: **the external check has been removed and not replaced**, and the tool now relies entirely on disclosure. That may be an acceptable posture; presenting it as an equivalent substitute is not.

**Does a planted-δ generator test anything the real data would? Largely no — by construction.** Generate data from a linear, additive model with a planted constant δ on a protected-class dummy, then fit OLS with that exact specification, and OLS recovers δ. That is not a test; it is a restatement of the Gauss–Markov theorem. It cannot detect:
- **Omitted-variable bias** — the dominant risk (no credit score, no AUS, no assets). The generator has no unobserved confounder correlated with both race and price *unless one is deliberately planted*, and §9 does not require that.
- **Specification error** — nonlinearity, unmodeled interactions, the MSA-FE/segregation substitution.
- **Data-side failures** — every CRIT and HIGH in this audit. A synthetic frame has no `Exempt`, no `Race Not Available`, no string-binned DTI, no pre-2018 censoring. **It cannot fail the way the real data will.**

What it *does* validate: the wiring — that the design matrix is built correctly, dummies are coded in the right direction, and the estimator is called properly. That is worth having. It is not calibration.

**The δ=0 check specifically — it tests the wrong null.** §9: *"including δ = 0, which must NOT produce significance above the nominal rate."*

§8's entire claim is: *"Prices come off lender rate sheets → within-lender residual correlation; HC1/HC3 don't touch it and on 10⁵–10⁶ rows manufacture significance."* If the generator draws **iid errors**, then cluster-robust SEs ≈ HC1 ≈ OLS SEs, the δ=0 check passes at exactly the nominal rate, and **the failure §8 exists to prevent is never exercised**. §9 specifies *"realistic covariate structure"* and says **nothing about the error structure**. The check as written would pass a build in which `cov_type='cluster'` was silently dropped.

**Fix.** The generator must plant, and the δ=0 test must be run against:
1. a **lender random effect** (within-cluster residual correlation) — without it the δ=0 check is vacuous;
2. **realistic cluster-size imbalance** (Herfindahl-heavy: a few lenders holding most rows), which is what makes `G_eff ≪ G` and is the actual regime — see the §8 ruling;
3. a **negative control**: the same δ=0 frame fit with `cov_type='HC1'` **must** over-reject. If it doesn't, the generator is not exercising the risk and the whole §9 suite is decorative.
4. Add a fourth check with an explicit **planted unobserved confounder** correlated with both race and price, and assert that recovery **fails** — demonstrating, in the test suite, the OVB the tool cannot fix. That is the honest version of "it tests the machine, not the world."

**What real failure passes all three of §9's checks?** The one that matters: **omitted-variable bias.** The tool reports 15 bps on a named lender whose minority applicants have systematically lower credit scores. Synthetic recovery passes (no credit score in the generator). The plausibility ceiling passes (15 ≪ 100). The disclosure fires — and a disclaimer does not unpublish a number. The cluster and CI gates pass on a large lender. **The lender is named.** Under v2 a grossly drifted engine would have blown a 4–15 band; under v3 nothing above ±100 bps exists to catch it. That is the cost of CRIT-1's reversal, and it is why the dev-time drift band should be restored rather than deleted.

---

### HIGH-4 — §6 cites `lien_status` to §1003.4(a)(33). That is the application-channel data point. A new error, introduced by the fix.

**Verified against Cornell LII, 12 CFR §1003.4(a):**
- **(a)(14)**, verbatim: *"**The lien status** (first or subordinate lien) of the property identified under paragraph (a)(9) of this section."*
- **(a)(33)**, verbatim: *"Except for purchased covered loans, the following information about the **application channel** of the covered loan or application…"*

§6's table row reads `lien_status | (a)(33)`. §14's citation list repeats it: *"§1003.4(a)(7)(10)(23)(24)(25)(26)(28)(33) regressor fields."* Both wrong; the correct cite is **(a)(14)**.

**This is a regression, not an inheritance.** Audit-2's HIGH-6 table had it **right** (*"`lien_status` | (a)(14) | codes 1/2, no NA — **clean**"*). v3 introduced the error while extending §6 "to EVERY regressor." The reversal that was supposed to close the gap opened a new one.

**Why it matters beyond the clerical.** The two cites have **opposite exemption behavior**, so the wrong cite implies the wrong rule:
- **(a)(14) is NOT optional data** → lien status is reported by **everyone**, including partially exempt institutions → §6's *"present for the covered set"* is correct **only under the correct cite**.
- **(a)(33) IS optional data** (§1003.3(d)(1)(iii): *"(a)(12), (15) through (30), and **(32) through (38)**"*) → under the doc's own cite, `lien_status` would be `Exempt`-able, and §6's "present" claim would be false.

So the row is right for a reason the doc does not state, cited to a field for which the row would be wrong. This is precisely the *"the author didn't read the sources"* exhibit MED-1 warned about — in a package branded *"the methodology federal examiners use."*

**Fix.** `lien_status` → **(a)(14)** in §6 and §14. Then re-verify **every** cite in §6 and §14 against the CFR, not against the previous draft. (I checked the rest: `loan_amount | (a)(7)` is **correct** — *"The amount of the covered loan or the amount applied for, as applicable"*; (a)(10)(iii) income, (a)(12), (a)(23), (a)(24), (a)(25), (a)(26), (a)(28) all hold. (a)(33) is the only broken one.)

---

### HIGH-5 — DTI: §6 cites the CFR for a binning the CFR does not contain, and the mixed-type coercion hazard Audit-2 named is still unhandled.

**What's wrong.** §6: *"`debt_to_income_ratio` | (a)(23) | … use HMDA bin encoding."* §7: *"`Σ β · DTI_bin_i` # categorical, (a)(23)."*

**§1003.4(a)(23), verbatim (my extraction):** *"Except for purchased covered loans, **the ratio** of the applicant's or borrower's total monthly debt to the total monthly income relied on in making the credit decision."*

The CFR requires a **continuous ratio**. It specifies **no bins**. The binning is a **CFPB public-file modification**.

**FFIEC public LAR `debt_to_income_ratio`, verbatim — values:** *"`<20%`  `20%-<30%`  `30%-<36%`  `36%`  `37%`  `38%`  `39%`  `40%`  `41%`  `42%`  `43%`  `44%`  `45%`  `46%`  `47%`  `48%`  `49%`  `50%-60%`  `>60%`  `NA`  `Exempt`"*
**Public LAR schema, verbatim:** *"`debt_to_income_ratio` Alphanumeric"* (as are `income`, `rate_spread`, `combined_loan_to_value_ratio`).

**The hazard, unchanged from Audit-2's MED-8 and still ungoverned:** `pd.to_numeric(..., errors='coerce')` turns `<20%`, `20%-<30%`, `30%-<36%`, `50%-60%`, `>60%`, `NA`, `Exempt` into `NaN` — **silently deleting the low and high DTI tails, the best and worst credits**. The deletion is monotone in a price driver, correlated with the outcome, and correlated with race. The rows die inside the design matrix, **after** §11's identity has run. This is the same class as CRIT-2 and it is the single most likely way this engine actually breaks in code.

Audit-2 prescribed: *"Cite the public LAR data-fields documentation; specify the exact 8-level categorical + NA/Exempt handling; **forbid numeric coercion**; mutation test per level."* v3 carried **none** of the four — only the word "categorical" survives, attached to the wrong cite.

**And it is the same attribution error §6 claims to have fixed.** §6's own bullet: *"**Attribution fix (Audit-2):** the 'leave blank if none' wording for `discount_points`/`lender_credits` is **FFIEC FIG/reporting-form language, not CFR text** — cite it as FIG, not §1003.4."* The doc learned the lesson for the fields it removed and not for the field it kept.

**Fix.**
1. Re-cite: **CFR (a)(23) for the field definition; the FFIEC public LAR data-fields documentation for the bin encoding.** Head the §6 column **"Source"**, not "Reg C cite."
2. Enumerate all levels explicitly, with `NA` and `Exempt` → exclude-with-reason.
3. **Forbid numeric coercion on this column** as a stated rule with a test that bites.
4. `[BUILD-RECON]` — resolve whether the individual values ship as `36` or `36%` in the CSV (the FFIEC page renders `%`; Audit-2 reported bare integers). Either way the column is Alphanumeric and coercion is forbidden; this only affects the parser, not the rule.

---

### HIGH-6 — The partial-exemption scope boundary is absent from v3. Sub-500 banks and credit unions are unscreenable, and those are this tool's users.

**Verified.** Cmt 4(a)(12)-7, verbatim (CFPB Official Interpretations): *"…**For partially exempt transactions under § 1003.3(d), an insured depository institution or insured credit union is not required to report the rate spread.** See § 1003.3(d) and related commentary."*

§1003.3(d)(2), verbatim: *"an insured depository institution or insured credit union that, in each of the two preceding calendar years, **originated fewer than 500 closed-end mortgage loans**… is not required to collect, record, or report optional data."* Optional data = *"(a)(12), (15) through (30), and (32) through (38)"* — the **outcome** plus DTI, CLTV, loan term, intro rate, and property value. (Non-depository mortgage companies are not eligible and always report in full.)

Audit-2 raised this as HIGH-8. **v3 addresses it nowhere.** The string "partial" appears once, in §6's 1111 bullet. §2's Out list, §13's limitations, and §12's suppression gate are all silent.

**Three consequences, all unstated:**
1. A partially exempt lender is **unscreenable** — every row exits as `exempt_rate_spread`, and the user is told nothing about *why*. For a tool serving community advocates and CDFI-adjacent analysts, "we cannot screen community banks and credit unions under 500 originations" is a **headline scope boundary**, not a footnote.
2. §1003.3(d)(4) permits voluntary reporting, so sub-500 lenders that *do* appear are a **self-selected subset** — biasing any national pooled run (including the dev-time drift band CRIT-1 asks to restore).
3. It interacts with §8's cluster floor perversely: these lenders don't **fail** the floor, they **never appear**. Suppression never fires because there is nothing to suppress. The tool reports a clean result on a silently truncated lender universe.

**Fix.** State the ≥500 boundary in §2 (Out) and §13. On a single-lender screen of a partially exempt LEI, raise a **distinct, explicit error** — "this lender is partially exempt under §1003.3(d); pricing screening is not possible" — never `n ≈ 0`, never a voluntary-subset estimate. Add `exempt_partial_1003_3d` to §11.

---

## MED

### MED-1 — §9 drops the sourced anchor and keeps an **unsourced** claim of the same kind. That is a downgrade, not a fix.

§9, verbatim: *"**For directional context only** (NOT a target, NOT in any output as a comparator): **the peer literature finds small adjusted rate disparities (single-digit to low-double-digit basis points).** Cited to orient the developer, never to calibrate…"*

An uncited generalization over "the peer literature," in calibration material, in a thread whose stated failure mode is asserting anchor magnitudes without reading the source. Audit-2 killed a **miscited** number; v3 replaced it with an **uncited** one. A miscited claim can at least be checked and refuted — that is how HIGH-1 was caught. An uncited claim cannot be. **The fix removed the citation and kept the claim.**

**And §14 forbids exactly this**, verbatim: *"Bartlett et al. is cited, if at all, only as directional context **with an explicit 'not a calibration target and design-mismatched' note**…"* §9's directional-context sentence carries **no cite and no such note**. §14's own rule is violated by §9, in the same document.

**In fairness — the claim is roughly true, but that is my sourcing, not the doc's.** From my extraction: Bartlett's coefficients span **1.2–7.8 bps** (single-digit); the paper's literature review reports *"Ghent, Hernández-Murillo, and Owyang (2014) examine subprime loans originated in 2005, and find that for 30-year, adjustable-rate mortgages, African-American and Latinx borrowers face interest rates **12 and 29 basis points**, respectively, higher"* — so "low-double-digit" has a source, and 29 exceeds the doc's range. The doc must cite it or delete it.

**Fix.** Either cite it properly (named papers, specific figures, read directly) with §14's required mismatch note, or delete the sentence. It cannot stay as an anonymous appeal to "the literature."

### MED-2 — "Net-of-points" is backwards, and it is a headline limitation.

§3: *"**rate_spread is a net-of-points price.**"* §13 makes *"**Net-of-points outcome**"* a headline limitation.

Points are **inside** the APR (§1026.4(b)(3), verified) — and APOR is **also** points-inclusive (§1026.35(a)(2), verified: *"derived from average interest rates, **points**, and other loan pricing terms"*). Both sides of `APR − APOR` include points. The correct term is **points-inclusive**, or "net **of the rate/points tradeoff**" at best.

"Net of X" in ordinary finance usage means **X has been removed**. A limitation headed *"Net-of-points outcome"* tells a reader — and a lender's counsel — the exact opposite of what §7 decided. This is the single sentence most likely to be quoted back in an adversarial proceeding as proof the author misunderstood their own outcome variable. The term originates in `AUDIT-2-TRIAGE.md`'s disposition and propagated unchallenged.

**Fix.** Replace with **"points-inclusive outcome"** throughout §3, §7, §13. State both sides: the borrower's APR includes points, and the APOR benchmark reflects average points.

### MED-3 — §5 still filters a field that does not exist. Audit-2's MED-4, unresolved.

§5, verbatim: *"`loan_to_value_ratio ≤ 100`."*

**Verified:** the CFR's only LTV data point is **(a)(24) Combined Loan-to-Value Ratio**. The FFIEC public LAR schema contains exactly one matching field — I enumerated every `*loan_to_value*` token in the schema and got `['combined_loan_to_value_ratio']`. There is **no** `loan_to_value_ratio`. §7 correctly uses `combined_LTV`; §5 does not. **§5 as written does not run** — it is either a `KeyError` or, worse, a silently skipped filter.

**Fix.** §5 → `combined_loan_to_value_ratio ≤ 100`, and reconcile with MED-7 (the filter removes much of the subordinate-lien population by construction).

### MED-4 — The reportable set is {1, 2, **8**}. §4's factual claim is wrong as written. Audit-2's MED-6, unresolved.

§4, verbatim: *"`rate_spread` is reported for `action_taken == 1` (originated) **and `== 2`**… per Reg C commentary 4(a)(12)-7/-8."*

**Cmt 4(a)(12)-8, verbatim (my extraction):** *"In the case of an application **or preapproval request** that was approved but not accepted, § 1003.4(a)(12) requires a financial institution to report the applicable rate spread."*
**FFIEC `action_taken`, verbatim:** *"**8 - Preapproval request approved but not accepted**."*

Action 8 is the **purest instance of §4's own logic** — a price the lender offered, uncontaminated by the borrower's accept/decline decision — and it is silently absent. Volume is small (purchase-only, preapproval programs only), so this is a correctness defect, not a power issue. But §4's stated fact is wrong, and it is wrong in the doc's own citation.

**Fix.** State the set as **{1, 2, 8}** and either include 8 or exclude it on its own stated terms.

### MED-5 — §4 still calls `{1,2}` a *selection* sensitivity and still fires the divergence rule. Two of Audit-2 MED-7's three confounds are unaddressed.

v3 **did** fix confound 1: with cost controls gone, `{1}` and `{1,2}` now share one control set, so population and controls no longer move together. Audit-2 CRIT-3's fix 2 (control-matched comparison) is satisfied structurally. Credit where due.

**Confound 2 — the outcome instrument changes — is untouched, and it is verified.** Cmt 4(a)(12)-8, verbatim: *"…the financial institution would provide **early disclosures** under Regulation Z, 12 CFR 1026.18 or 1026.37 (for closed-end mortgage loans)… but might never provide any subsequent disclosures. In such cases where no subsequent disclosures are provided, a financial institution complies… **by relying on the annual percentage rate for the application or preapproval request, as calculated and disclosed pursuant to Regulation Z, 12 CFR 1026.18 or 1026.37**…"*

Action-2 `rate_spread` comes from the **Loan Estimate** APR. Action-1 `rate_spread` comes from the final **Closing Disclosure** APR. Pooling them puts **two different measurement instruments in the same `Y`**, and LE APRs systematically differ from final APRs.

**Confound 3 — `{2}` is itself a selected population** (borrowers who shop and walk are not random; the action-2 pool skews toward those who got a better offer elsewhere, which correlates with shopping intensity, which correlates with race in the literature) — also untouched.

**Why it matters now more than in v2.** §4's interpretation rule, verbatim: *"**Material divergence between the two ⇒ selection is doing real work** and must be surfaced, not buried under a disclaimer."* In v2 the sensitivity was a guaranteed no-op reporting false reassurance. In v3 it **runs** — and its divergence is **unidentified**. LE-vs-CD measurement drift will produce divergence, and §4's rule will report it as *selection*. v2 manufactured a false negative; **v3 manufactures a false positive with a causal label attached.** That is not obviously an improvement.

**Fix.** Rename to **"alternative-population bound"** (Audit-2's ruling, not adopted). State all three confounds in §4 and §13. Replace the interpretation rule: divergence is **uninterpretable as selection** — report both estimates as a bound, attribute nothing. Note the NA hole inside `{2}` (rate_spread is NA for approved-not-accepted applications where no Reg Z disclosures are required — a non-random hole).

### MED-6 — MSA has no §6 row, and the non-MSA encoding is undocumented where the doc says to look.

`Σ β · MSA_i` is in §7. §6 has no row for it. §10 governs **sparse** MSAs; nothing governs **non-MSA** (rural) rows.

FFIEC `derived_msa-md`, verbatim: *"The 5 digit derived MSA (metropolitan statistical area) or MD (metropolitan division) code. An MSA/MD is an area that has at least one urbanized area of 50,000 or more population. **Values: Varying values**."* Schema: *"`derived_msa_md` 5 Alphanumeric."*

**I could not verify the non-MSA sentinel from the FFIEC field documentation — it enumerates no sentinel at all.** I decline to assert one from memory; that is the failure mode this audit exists to catch. But rural rows must carry *some* value, and the hazard is the exact 1111-analogue the doc congratulates itself on catching: **a code that looks like a sentinel but is a real category.** Drop it as missing and the tool silently excludes every rural loan — non-random, and the CDFI-relevant population. Treat it as an MSA and every rural loan in the country pools into one giant "MSA" dummy.

**Fix.** `[BUILD-RECON — load-bearing, resolve before code]` the non-MSA encoding from the actual CSV. Add a §6 row stating it, and a §10 rule: non-MSA is a **real category**, not a sentinel — either its own dummy or excluded-with-reason `non_msa`, never silently pooled or dropped.

### MED-7 — First-lien-only: the anchor rationale died with the anchor, but the regulator's own rationale survives, and §5 is now incoherent with §2.

Audit-2's MED-5 rested on two legs: (i) the anchor is first-lien-only, (ii) HPML thresholds differ by lien. Dropping the anchor kills leg (i). **Leg (ii) survives and I verified it** — §1026.35(a)(1), verbatim: *"(i) By **1.5** or more percentage points for loans secured by a **first lien**… (ii) By **2.5** or more percentage points for [first-lien jumbo]… (iii) By **3.5** or more percentage points for loans secured by a **subordinate lien**."*

The regulator sets a threshold **2 pp higher** for subordinate liens because subordinate-lien spreads are structurally higher. That is a different pricing regime. §7 controls for it with a **lien dummy** — a pure level shift, no interaction — which is exactly the *"weak control"* the doc rejects for `loan_type` when excluding FHA/VA. **The doc applies its own principle to `loan_type` and not to `lien_status`.**

Compounding: §5's `LTV ≤ 100` filter (MED-3) removes much of the subordinate-lien population **by construction** — subordinate liens are where CLTV runs high — so §2's admitted population and §5's filters already disagree.

**Fix.** **First-lien only for v0.3.0**, matching the doc's own stated principle; subordinate-lien as a separately-scoped config, identical treatment to FHA/VA. If subordinate liens stay, the lien dummy must become a **lien interaction** and §13 must carry the mixed-regime caveat.

### MED-8 — The ±100 bps plausibility ceiling is inert. It is ~10× any magnitude the doc itself considers plausible.

§9: *"A `|coefficient|` beyond a wide ceiling `[SET IN AUDIT-3: e.g. ±100 bps]` is flagged as a probable spec/data error."*

§9's own directional context says the plausible range is *"single-digit to low-double-digit basis points."* A ceiling at **±100** is roughly **10×** that. It catches a sign flip or a units error (pp vs bps) and nothing else. Every defect in this audit — DTI tail deletion, `is_arm` fabrication, race folded into the reference group, OVB — produces a plausible-looking number **well inside ±100**. The guard fires on failures the type system would catch and sleeps through the failures that ship. See the ruling below.

---

## LOW

- **LOW-1 — §14 carries a dangling HPML citation.** *"12 CFR §1026.35 (HPML, verified current)"* sits in §14's list, but §2 invokes HPML **only** to say the binary cut is out of scope. A "verified current" citation for a rule the tool does not apply is residue from v2's HPML debate. (The thresholds do hold — verified above — so this is hygiene, not error.) **Fix:** drop from §14 or mark it as scope-exclusion support only.
- **LOW-2 — §12's suppression gate is still strippable.** Audit-2's LOW-3 asked for a statement that no public parameter may relax suppression. §12 says the **disclaimers** are *"bound to the metric/table, non-strippable"* but says nothing of the kind about the **suppression gate** itself. An advocate — or a defendant's expert — flips a kwarg. **Fix:** state that no public parameter may relax suppression; add a test asserting it. (Note: the disclaimer stack itself is coherent and well-placed; this is about the gate.)
- **LOW-3 — §3's strongest reasoning survives intact, again.** The rate_spread-over-note-rate argument (public LAR carries `activity_year` only; APOR was matched at the rate-set date before that date was stripped) is correct and remains the best thinking in the document. §1003.4(a)(12)(i), verified: *"…as of the **date the interest rate is set**."*

---

## Firewall ruling

**Clean.** §1 correctly places regression-adjusted pricing on the inferential side. §12 never says "discrimination" or "overcharging" in user-facing output. Nothing leaks toward a finding of discrimination. Nothing belongs in `hmda-analyzer`.

**Two notes, neither a breach:**
1. HIGH-2's fix (group means of points; costs-as-outcome) introduces **descriptive** statistics into the screener. This is *not* a firewall breach — they are diagnostics bound to an inferential result and are meaningless outside it — but the doc must **say so explicitly**, or the next audit will flag it as leakage.
2. §13's *"Net-of-points outcome"* (MED-2) is a user-facing limitation that misstates the outcome. Not a firewall issue; a correctness issue in firewall-adjacent language.

**On the suppression gate and the manufactured-significance path (audit task 4):** the gate closes the path **better** than v2's, because the gate never depended on the anchor — it runs on cluster count, CI width, control completeness, and conditioning. Dropping the anchor therefore does **not** open a new named-lender path, and §9's *"never a runtime gate on a named lender"* was correct in v2 and remains correct. **But the gate now carries weight it was not designed for:** with the dev-time band gone, the suppression gate is the *only* thing standing between a drifted engine and a named lender, and it tests **precision**, not **correctness**. A precisely-estimated wrong number passes every limb. That is HIGH-3's failure, and it is why the drift band belongs back in §9 — not at runtime, but at dev time where it always was.

---

## Cross-section consistency check (audit task 4)

| Check | Result |
|---|---|
| §2 scope ↔ §5 filters | ❌ §2 admits subordinate liens; §5's LTV filter removes them by construction (MED-7). §5 filters a nonexistent field (MED-3). |
| §2 scope ↔ §7 equation | ❌ §2 says conventional-only and §7 correctly drops the `loan_type` dummy — **consistent**. But §2 is silent on the ≥500 partial-exemption boundary (HIGH-6) and on first-lien (MED-7). |
| §3 outcome ↔ §4 population | ⚠️ §3 defines one outcome; §4 pools two instruments (LE APR vs CD APR) into it without saying so (MED-5). |
| §5 gate ↔ §11 vocabulary | ❌ **Direct contradiction** — "HARD GATE" vs `pre_2018_excluded` reason code (HIGH-1). |
| §6 table ↔ §7 equation | ❌ `protected_class` and MSA missing (CRIT-3, MED-6); `lien_status` miscited (HIGH-4). |
| §7 ↔ §11 identity | ❌ DTI coercion and `is_arm` imputation both survive the identity (CRIT-2, HIGH-5). |
| §9 ↔ §14 | ❌ §14 requires a "not a calibration target and design-mismatched" note on any Bartlett reference; §9's directional-context sentence carries no cite at all (MED-1). |
| §9 ↔ §12 | ❌ **Dangling dependency the anchor drop created.** The `[SET IN AUDIT-3]` CI-width bound can only be calibrated from an external study's SEs at known n (Audit-2 derived its 5 bps precisely that way: *"the matched anchor's SEs run ~0.4–0.5 bps on ~1.3M loans"*). §9 says no published study is comparable enough to inform a magnitude — **but §12 needs one to set its threshold.** Either the anchor is close enough to inform an expectation or it is not; v3 wants it both ways. |
| §9 ↔ §13 | ✅ Consistent — "Uncalibrated" is carried as the headline limitation. |
| §14 citation list | ❌ `(a)(33)` for lien_status (HIGH-4); dangling §1026.35 (LOW-1). |

---

## Independent verification log

Every row below was fetched by me with `curl`, extracted locally, and read. Nothing accepted on the doc's, the triages', or Audit-2's authority. Nothing delegated.

| # | Claim under test | Source I actually read | Operative quote | Held? |
|---|---|---|---|---|
| 1 | **Points are finance charges inside the APR** (§7's entire basis) | Cornell LII, 12 CFR §1026.4 | §1026.4(b): *"The finance charge includes the following types of charges… **(3) Points, loan fees, assumption fees, finder's fees, and similar charges.**"* §1026.4(a): *"The finance charge is the cost of consumer credit as a dollar amount. It includes any charge payable directly or indirectly by the consumer and imposed directly or indirectly by the creditor as an incident to or a condition of the extension of credit."* | ✅ **HELD** — §7's premise is sound |
| 2 | **`intro_rate_period` is NA for fixed-rate** (§6's `is_arm` basis) | CFPB Official Interpretations, Reg C, Paragraph 4(a)(26) | Cmt **4(a)(26)-3**: *"A financial institution complies with § 1003.4(a)(26) by reporting that the requirement is not applicable for a covered loan with a fixed rate or an application for a covered loan with a fixed rate."* | ✅ **HELD** |
| 2b | **Can (a)(26) NA arise for reasons OTHER than fixed-rate?** (does `is_arm` conflate?) | Same | Cmt **4(a)(26)-1**: *"**Except for partially exempt transactions under § 1003.3(d)**, § 1003.4(a)(26) requires…"* — Cmt **4(a)(26)-2**: *"…does not require reporting of introductory interest rate periods based on preferred rates unless the terms… provide that the preferred rate will expire at a certain defined date. Preferred rates include terms… that provide that the initial underlying rate is fixed **but that it may increase or decrease upon the occurrence of some future event**…"* — Cmt **4(a)(26)-4**: purchased fixed-rate loan | 🔴 **YES — 3 causes. `is_arm` CONFLATES them (CRIT-2)** |
| 2c | **Is the Exempt path reachable, or does the rate_spread exclusion catch it first?** (the load-bearing test for CRIT-2) | Cornell LII, 12 CFR §1003.3(d) | §1003.3(d)(1)(iii): *"**Optional data** means the data identified in § 1003.4(a)(1)(i), (a)(9)(i), and **(a)(12), (15) through (30), and (32) through (38)**."* §1003.3(d)(4): *"A financial institution eligible for a partial exemption… **may** collect, record, and report optional data… **provided that**… (ii) If the institution reports any data for the transaction pursuant to **§ 1003.4(a)(15), (16), (17), (27), (33), or (35)**, it reports all data that would be required by [those], respectively…"* | 🔴 **REACHABLE.** Voluntary reporting is **à la carte**; (a)(12) and (a)(26) are **not** in the all-or-nothing list → a lender may report `rate_spread` and omit `intro_rate_period` → **CRIT-2 confirmed** |
| 3 | **`rate_spread` reported for action 1 AND 2** | Cornell LII §1003.4(a)(12); CFPB Interp-4 | §1003.4(a)(12)(i): *"For covered loans **and applications that are approved but not accepted**, and that are subject to Regulation Z… other than assumptions, purchased covered loans, and reverse mortgages, the difference between the covered loan's annual percentage rate and the average prime offer rate for a comparable transaction **as of the date the interest rate is set**."* | ✅ **HELD** — but **incomplete**: also action **8** (MED-4) |
| 3b | Cmt 4(a)(12)-7 scope | CFPB Interp-4 | *"If the covered loan is an assumption, reverse mortgage, a purchased loan, or is not subject to Regulation Z… not applicable. If the application did not result in an origination **for a reason other than the application was approved but not accepted** by the applicant… not applicable. **For partially exempt transactions under § 1003.3(d), an insured depository institution or insured credit union is not required to report the rate spread.**"* | ✅ HELD — doc **still misses** the partial-exemption sentence (HIGH-6) |
| 3c | Cmt 4(a)(12)-8 — which APR for action 2 | CFPB Interp-4 | *"In the case of an application **or preapproval request** that was approved but not accepted… the financial institution would provide **early disclosures** under Regulation Z, 12 CFR 1026.18 or 1026.37… but might never provide any subsequent disclosures. In such cases… complies… **by relying on the annual percentage rate for the application or preapproval request, as calculated and disclosed pursuant to Regulation Z, 12 CFR 1026.18 or 1026.37**…"* | ✅ HELD — doc **misses** action 8 (MED-4) **and** the LE-vs-CD instrument change (MED-5) |
| 4 | **Pre-2018 threshold reporting 1.5/3.5** (§5's entire basis) | **govinfo, CFR-2017-title12-vol2-sec203-4 (the actual pre-2018 Regulation C)** | §203.4(a)(12)(i): *"For **originated loans** subject to Regulation Z, 12 CFR part 226, the difference between the loan's annual percentage rate (APR) and the average prime offer rate… **if that difference is equal to or greater than 1.5 percentage points for loans secured by a first lien on a dwelling, or equal to or greater than 3.5 percentage points for loans secured by a subordinate lien on a dwelling.**"* | ✅ **HELD — both figures, from the operative regulation itself.** A pre-2018 blank **is** a real below-threshold value. §5's gate is **sound**. (Bonus: *"For originated loans"* — pre-2018 there was no action-2 reporting either.) |
| 5 | **`income` 1111 = real $1.111M, not an exemption** | FFIEC public LAR data fields | `income`: *"The gross annual income, **in thousands of dollars**, relied on in making the credit decision… **Values: Varying values**"* — **no 1111 sentinel**. I enumerated all 14 occurrences of `1111` on the page: **every one is `1111 - Exempt` on an enumerated/coded field** (`reverse_mortgage`, `open-end_line_of_credit`, `business_or_commercial_purpose`, `balloon_payment`, `interest_only_payment`, `negative_amortization`, `other_nonamortizing_features`…). | ✅ **HELD** — and §6's *"1111 is never a global sentinel"* rule **HELD** |
| 6 | **HPML thresholds §1026.35, current** | Cornell LII, 12 CFR §1026.35 | §1026.35(a)(1): *"…**(i) By 1.5 or more percentage points for loans secured by a first lien** with a principal obligation at consummation that does not exceed [the Freddie Mac conforming limit]; **(ii) By 2.5 or more percentage points for [first-lien jumbo]**; or **(iii) By 3.5 or more percentage points for loans secured by a subordinate lien.**"* | ✅ **HELD** — but now a **dangling** citation (LOW-1) |
| 6b | *(not claimed by doc — found by me)* **APOR is itself points-inclusive** | Cornell LII §1026.35(a)(2); govinfo §203.4(a)(12)(ii) | §1026.35(a)(2): *"'Average prime offer rate' means an annual percentage rate that is **derived from average interest rates, points, and other loan pricing terms** currently offered to consumers by a representative sample of creditors for mortgage transactions that have low-risk pricing characteristics."* | 🔴 **Refutes §3's "net-of-points" label (MED-2)** |
| 7a | **§6 field cites** — `loan_amount` (a)(7) | Cornell LII §1003.4(a) | (a)(7): *"The amount of the covered loan **or the amount applied for**, as applicable."* | ✅ **HELD** (doc is right; my own prior expectation was wrong — verified rather than asserted) |
| 7b | **§6 field cite** — `lien_status` (a)(33) | Cornell LII §1003.4(a) | **(a)(14)**: *"**The lien status** (first or subordinate lien) of the property identified under paragraph (a)(9)."* — **(a)(33)**: *"Except for purchased covered loans, the following information about the **application channel**…"* | 🔴 **BROKEN — doc cites (a)(33); correct cite is (a)(14) (HIGH-4)** |
| 7c | Remaining §6/§14 cites: (a)(10)(iii) income, (a)(12), (a)(23), (a)(24), (a)(25), (a)(26), (a)(28) | Cornell LII §1003.4(a) | (a)(10)(iii): *"Except for covered loans or applications for which the credit decision did not consider or would not have considered income, the gross annual income relied on in making the credit decision…"*; (a)(23) DTI; (a)(24) CLTV; (a)(25) loan term; (a)(26) intro rate; (a)(28) property value | ✅ **ALL HELD** — (a)(33) is the only broken cite |
| 8 | **`{1,2}` viability — are §7's regressors populated for action_taken == 2?** *(the doc defers this to BUILD-RECON; it is answerable now)* | Cornell LII §1003.4(a) | (a)(7): *"or **the amount applied for**"* • (a)(10)(iii): *"or **if a credit decision was not made**, the gross annual income relied on in **processing the application**"* • (a)(23)/(a)(24): *"…**relied on in making the credit decision**"* (an approved application **has** one) • (a)(25): *"or **would have matured or terminated**"* • (a)(26): *"or **proposed number of months in the case of an application**"* • (a)(28): *"or, **in the case of an application, proposed to secure** the covered loan relied on in making the credit decision"* • (a)(14): lien status of the property under (a)(9) | ✅ **PREMISE HOLDS — every §7 regressor is application-side by the text of the reg. `{1,2}` does NOT collapse.** See ruling. |
| 9 | **DTI encoding — is the binning in Reg C?** | Cornell LII §1003.4(a)(23); FFIEC public LAR data fields + schema | **CFR (a)(23)**: *"Except for purchased covered loans, **the ratio** of the applicant's or borrower's total monthly debt to the total monthly income relied on in making the credit decision"* — **no bins**. **FFIEC**: *"Ratios binned are: `<20%` `20%-<30%` `30%-<36%` `36%` `37%` … `49%` `50%-60%` `>60%` `NA` `Exempt`"*. **Schema**: *"`debt_to_income_ratio` Alphanumeric"* | 🔴 **Doc cites CFR for a public-file construct; mixed-type coercion hazard live (HIGH-5)** |
| 10 | **Public LAR dtypes** *(the doc's open BUILD-RECON item — resolved)* | FFIEC public LAR schema | *"`rate_spread` **Alphanumeric**"*; *"`income` **Alphanumeric**"*; *"`combined_loan_to_value_ratio` **Alphanumeric**"*; *"`debt_to_income_ratio` **Alphanumeric**"*; *"`loan_amount` **Integer**"*; *"`derived_msa_md` 5 **Alphanumeric**"* | ✅ **RESOLVED — `rate_spread` is a string column. Close the BUILD-RECON item.** |
| 11 | **Is there a bare `loan_to_value_ratio` field?** | FFIEC public LAR schema (enumerated every `*loan_to_value*` token) | Result: `['combined_loan_to_value_ratio']` — **one match only** | 🔴 **§5 filters a nonexistent field (MED-3)** |
| 12 | **`derived_race` / `derived_ethnicity` states** | FFIEC public LAR data fields | `derived_race`: *"American Indian or Alaska Native \| Asian \| Black or African American \| Native Hawaiian or Other Pacific Islander \| White \| **2 or more minority races** \| **Joint** \| **Free Form Text Only** \| **Race Not Available**"*; `applicant_race-1` code **6** = *"Information not provided by applicant in mail, internet, or telephone application"* | 🔴 **Four ungoverned states on the coefficient of interest (CRIT-3)** |
| 13 | **`action_taken` codes** | FFIEC public LAR data fields | *"1 - Loan originated \| 2 - Application approved but not accepted \| … \| **8 - Preapproval request approved but not accepted**"* | 🔴 **Confirms the {1,2,8} set (MED-4)** |
| 14 | **`derived_msa-md` non-MSA sentinel** | FFIEC public LAR data fields | *"The 5 digit derived MSA… **Values: Varying values**"* — **no sentinel enumerated** | ⚠️ **NOT VERIFIED — I decline to assert an encoding from memory. See MED-6; resolve from the CSV.** |
| 15a | **Bartlett — do `7.88` / `6.95` / "Panel A" exist in the published paper?** | **Accepted MS (May 4 2021), `faculty.haas.berkeley.edu/stanton/pdf/discrim.pdf`, 76pp — extracted by me with pypdf** | String counts: `7.88` → **0**; `6.95` → **0**; `Panel A` → **0**; `APOR` → **0**; `4.674` → **3** | ✅ **Audit-2's HIGH-1 independently CONFIRMED** |
| 15b | **§9: "Bartlett excludes CRA tracts"** | Same | Table 6: *"Interest-rate differentials **by CRA status**"* — *"Non-CRA tract × Minority **4.043**\*\*\* (0.248) / CRA tract × Minority **6.431**\*\*\* (0.334) … **p-value for test of equality 0.0000**"*; FE row *"CRA FE Y Y Y Y"*; summary stats *"CRA census tract"* mean .0926 (all) / .1782 (GSE). *"eliminate from our sample"* → **NOT FOUND** | 🔴 **FALSE. CRA tracts are included, analyzed, and show LARGER disparities (CRIT-1)** |
| 15c | **§9: "conventional-conforming"** | Same | Abstract: *"Using an identification under this rule afforded by the **GSEs' and FHA's** pricing of mortgage credit risk, we show that risk-equivalent Latinx/African-American borrowers pay significantly higher interest rates on **both GSE-securitized and FHA-insured loans**… we estimate that these rate differences cost minority borrowers over **$450 million** yearly."* Tables 6 & 10 carry co-equal **FHA Loans** columns | 🔴 **FALSE. FHA is co-equal (CRIT-1)** |
| 15d | **§9: "2009–2015"** | Same, Internet Appendix I1.4.2 | *"the data for the pricing regressions are sourced from the merged HMDA, ATTOM, McDash/Equifax data from 2009 through 2015. As discussed in Section 6, **we extend our analysis of GSE and FHA mortgage pricing by including controls for the effects of loan points, total loan costs, and lender credits that are available in the recently released 2018 and 2019 HMDA data.**"* | 🔴 **INCOMPLETE — and the omitted half is the tool's exact data (CRIT-1)** |
| 15e | **Table 10 cell values** *(Audit-2 flagged these as un-recertified against print)* | Same — extracted by me | *"(a) No controls for points or costs"*: GSE Purchase **7.377**\*\*\* (0.472), GSE Refi **5.998**\*\*\* (0.392), FHA Purchase 5.529, FHA Refi 1.632; R² 0.376/0.483 — *"(b) Controlling for points paid"*: GSE Purchase **7.820**\*\*\* (0.482), GSE Refi **6.900**\*\*\* (0.375); R² 0.386/0.493 — *"(c)"*: 7.709 / 6.806. FE: *"Lender x year FE Y"*, *"Point decile x year FE Y"*, *"Cash-out x credit decile x year FE Y"* | ✅ **Audit-2's extraction CONFIRMED exactly.** The 2018/2019 HMDA spec **exists** and §9 does not mention it |
| 15f | **fn 31 — why tract-level credit scores** | Same | *"We include controls for individual income here along with **census-tract-level credit scores, because the HMDA data do not include individual credit scores**."* | ✅ **HELD — the paper shares the tool's credit-score handicap in Table 10** |
| 15g | **fn 33 — costs-as-outcome** | Same | *"As a robustness check, we also run these regressions with **total loan costs on the left hand side** and interest-rate deciles on the right. As in Panel (c) of Table 10, the estimated coefficient on the minority indicator is **significantly greater than zero in all regressions**."* | ✅ **HELD — the fix v3 dropped (HIGH-2)** |
| 15h | *(context for §9's uncited "peer literature" claim)* | Same, literature review | *"Courchane and Nickerson (1997) and Black, Boehm, and DeGennaro (2003) find that **black borrowers pay more in points, conditional on the loan interest rate**."* — *"Ghent, Hernández-Murillo, and Owyang (2014) examine subprime loans originated in 2005, and find that for 30-year, adjustable-rate mortgages, African-American and Latinx borrowers face interest rates **12 and 29 basis points**, respectively, higher than other borrowers."* | ⚠️ §9's range is **roughly** supportable — **but by my sourcing, not the doc's** (MED-1) |

**Sources not reached — stated explicitly, nothing fabricated:**
- **eCFR (`ecfr.gov`)** — not attempted this round; Audit-2 reported a bot-block. Regulatory text taken from **Cornell LII** (current CFR), **govinfo** (2017 CFR, XML — authoritative for the pre-2018 rule), and **CFPB's own Official Interpretations**. All agree where they overlap.
- **ScienceDirect final typeset JFE 143(1):30–56** — not reached (paywall/403, consistent with Audit-2). **My Bartlett evidence is the May 4 2021 accepted manuscript**, extracted by me. Table 6/10 cell values are **accepted-MS values, not certified against print.** This does not weaken CRIT-1: the CRA/FHA/2018-19 facts are structural (whole tables and the abstract), not marginal cell readings, and they refute §9's description in **both** the accepted MS and — a fortiori — any later revision, since revision after May 2021 could only have moved *toward* the published text §9 purports to describe.
- **NBER w25943 (2019 WP)** — not re-fetched this round. I rely on Audit-2's extraction **only** for the WP's CRA-exclusion sentence, and only to *explain the provenance* of §9's error. CRIT-1 does not depend on it: the accepted MS's own contents refute §9 without reference to the WP.
- **`derived_msa-md` non-MSA encoding** — **not verified** (MED-6). No assertion made.
- **FFIEC FIG PDF** — not fetched; the FFIEC public LAR data-fields page and schema were fetched and quoted instead.

---

## [SET IN AUDIT-3] rulings

### 1. Effective-cluster floor (§8) — doc: `~30–50`
**Ruling: adopt the conservative end, and fix the dimension the doc left open.**
**Propose: `G_eff ≥ 30` AND raw `G ≥ 30`**, where `G_eff = 1 / Σ_g (n_g/n)²` (inverse-Herfindahl of cluster shares).
**Reasoning.** ~30–50 is the conventional cluster-asymptotics band, so the doc's provisional value is not arbitrary — it is the standard. Take 30 as a **floor, not a target**, because this tool publishes names. The addition that matters is `G_eff`: mortgage markets are Herfindahl-heavy, and a single-MSA screen with 45 lenders where the top 3 hold 70% of originations has `G_eff ≈ 6` while raw `G = 45` sails through. A raw-count-only floor passes exactly the case that breaks cluster asymptotics.
**Also:** §8's single-lender fallback (cluster on MSA) is presented as equivalent. **It is not** — rate sheets are national, so lender×MSA residual correlation is not removed by clustering one lender's loans on MSA. Apply the same `G_eff` test to MSAs **and state that the fallback is weaker.**
**And:** per HIGH-3, `G_eff` imbalance must be **planted in the synthetic generator**, or the δ=0 check never exercises the regime this floor exists to police.

### 2. Few-cluster policy — bootstrap vs hard-suppress
**Ruling: hard-suppress. No wild-cluster bootstrap.**
**Reasoning.** Wild-cluster bootstrap (Cameron–Gelbach–Miller) is the right tool for **inference under few clusters** — it rescues **power**. That is the wrong thing to rescue here. This deliverable's risk is not "we failed to name a lender we could have named"; it is "we named a lender we should not have." A bootstrap converts *"can't tell"* into a publishable p-value — it manufactures precisely the confidence the floor exists to withhold. And it does nothing about **cluster imbalance**, which is the actual failure mode: a bootstrap on a sample where one lender is 60% of the rows is still a bootstrap on one lender. Hard-suppress, and report the `G_eff` that caused it so the user knows *why* rather than seeing a blank.
**Offer instead (non-blocking):** the bootstrap may be exposed as a **dev-time diagnostic**, never wired to the suppression gate.

### 3. Plausibility ceiling (§9) — doc: `e.g. ±100 bps`
**Ruling: reject as a single number. It is inert (MED-8). Split it by context — the two regimes have genuinely different plausible ranges.**
**Propose:**
- **Dev-time national pooled run: `|coef| > 25 bps` → fail the build.** The pooled national estimand is the one the literature actually speaks to (Bartlett: 1.2–7.8 bps note-rate; even generous OVB/no-lender-FE/fee wedges do not plausibly reach 25). A pooled run outside ±25 is a specification or data error — DTI tails deleted, race folded into the reference group, a sign flip — not a discovery. **This is the engine-drift check that CRIT-1 removed**, restated as a bound rather than a band, and it is the minimum viable replacement.
- **Runtime single-lender screen: `|coef| > 100 bps` → flag as probable spec/data error, never suppress on it alone.** Keep the doc's number **here only**. A single worst-actor lender can legitimately sit far above a national pooled average; a tight runtime ceiling would flag the true positives this tool exists to find. §9's *"never a runtime gate on a named lender"* is correct and must survive.
**Reasoning for the asymmetry.** §9 currently applies one number to two estimands with different plausible supports. The pooled estimand is anchored (by literature the doc itself invokes as "directional context"); the single-lender estimand is not. One ceiling cannot serve both: at 100 it never fires on the pooled run; at 25 it would silence real lenders. **Note the dependency:** the 25 bps bound requires §9 to state a magnitude expectation — which §9 currently refuses to do (*"The tool therefore asserts no expected coefficient magnitude"*) while simultaneously asserting one (*"single-digit to low-double-digit"*) and setting a magnitude-based ceiling. That contradiction must be resolved in §9's favor of honesty: **the tool does hold a soft magnitude expectation for the pooled dev-time run; it holds none for a named lender.** Say that, and both bounds become defensible.

### 4. CI-width suppression threshold (§12) — doc: unset
**Ruling: two limbs, both required — and §9 must supply the derivation it currently disclaims.**
**Propose: suppress the name unless 95% CI half-width `≤ 5 bps` **AND** `≤ 1.0 × |point estimate|`.**
**Reasoning.** The **absolute** limb stops the tool naming a lender on "12 bps ± 11" — technically CI-excludes-zero, consistent with anything from 1 to 23. The **relative** limb stops a large-but-imprecise estimate qualifying purely because it is large. Calibration for the 5 bps figure: the matched anchor's SEs run ~0.4–0.5 bps on ~1.3M loans **with** lender FE (Table 10, verified above); a single-lender screen at 10³–10⁴ loans with clustered SEs runs an order of magnitude wider. So a 5 bps half-width is **achievable for a large lender and correctly unachievable for a small one** — the intended sorting, and it makes the threshold a real constraint rather than a formality.
**⚠️ Dependency the anchor drop created (see cross-section table).** That derivation **comes from Bartlett's SEs**. If §9 maintains that no published study is comparable enough to inform an expectation, then §12 has **no principled basis for 5 bps** and the number is arbitrary — which is the same defect §9 dropped the anchor to avoid. **v3 cannot have it both ways.** Resolution: §9 concedes the anchor is close enough to inform **precision expectations and a dev-time drift bound**, while remaining too design-mismatched to calibrate a **published magnitude**. That is a defensible, honest, and internally consistent position. It is also, not coincidentally, the position the true description of the paper supports.

### 5. Condition-number threshold (§12) — doc: unset
**Ruling: keep it, but demote it. The doc's framing invites a mistake.**
**Propose: VIF > 10 on the protected-class column → suppress (primary). κ > 30 on the *column-standardized* design matrix → suppress (secondary sanity check).**
**Reasoning.** The conventional κ > 30 threshold (Belsley–Kuh–Welsch) is defined on a **standardized** matrix. `statsmodels`' `cond_no` on a raw design carrying MSA dummies and `log(loan_amount)` will be enormous for reasons having nothing to do with `β_pc` — so a naive κ gate either suppresses everything or gets tuned into meaninglessness. The quantity that matters is collinearity **of the protected-class regressor**, which is what its VIF measures.
**And §12 must state the tension it currently hides.** With MSA FE in a segregated market, geography and the protected-class indicator are **substitutes**: the more geography you absorb, the more of the disparity you absorb with it. That is a **limitation to disclose**, not a diagnostic to pass. A low `β_pc` VIF is reassuring; a **high** one may reflect **segregation rather than a modeling error** — and suppressing on it silently drops the most segregated markets, the ones this tool's users care about most. Suppress, but **log the reason distinctly** (`suppressed_pc_collinearity`) so a dropped screen is visible as a *finding about the market*, not a silent null. Add to §13.

### 6. `{1,2}` — may the doc assert the sensitivity works before build-recon? *(tagged BUILD-RECON; ruled here because it is load-bearing)*
**Ruling: the premise is VERIFIED from the CFR and needs no build-recon. Close the item. But the doc may NOT assert what §4 currently asserts.**
**What holds.** Every §7 regressor is application-side **by the text of the reg** (verification row 8): (a)(7) *"or the amount applied for"*; (a)(10)(iii) *"or if a credit decision was not made… in processing the application"*; (a)(23)/(a)(24) *"relied on in making the credit decision"* — an approved application **has** one; (a)(25) *"or would have matured or terminated"*; (a)(26) *"or proposed number of months in the case of an application"*; (a)(28) *"or, in the case of an application, proposed to secure"*; (a)(14) lien status. **`{1,2}` does not collapse. The doc is more pessimistic than the reg text warrants** — the v2 no-op was caused entirely by the four Closing-Disclosure-conditioned **cost** fields, and those are gone.
**What does not hold — three things the doc must add before asserting anything:**
1. **The non-degeneracy assertion (Audit-2 CRIT-3 fix 3, dropped).** *"The `{1,2}` run must raise if the action-2 count in the modeled sample is 0."* The regressors verify **today**; a future filter, a new control, or an `Exempt` sweep could silently re-collapse it, and §4's interpretation rule **converts a collapse into a false reassurance**. This is a two-line guard on a permanent PyPI release. Not optional.
2. **The rename and the confounds (MED-5).** It is not a selection diagnostic. LE-APR-vs-CD-APR and `{2}`'s own selection are unresolved and unmentioned.
3. **The `{2}` NA hole.** `rate_spread` is NA for approved-not-accepted applications where no Reg Z disclosures are required — a non-random hole *inside* `{2}` — plus partial exemption (HIGH-6).
**So:** replace `[BUILD-RECON: confirm each §7 regressor is populated for action_taken == 2…]` with the **cites above**, and keep `action2_field_unavailable` in §11 as a defensive reason code that should never fire — with the assertion that raises if it does.

---

## Strongest single objection

**Rewrite §9's description of Bartlett from the paper as it actually exists, and re-take the anchor decision against the true description — before any code.**

§9 discards the tool's only external error check on the strength of four claims about the anchor paper. I extracted the paper and checked all four. **One is true.** CRA tracts are not excluded — they are analyzed in their own table, with disparities **significantly larger** inside them (6.431 vs 4.043, p = 0.0000). FHA is not excluded — it is co-equal in the abstract and carries its own columns in every relevant table. And the paper is not confined to 2009–2015: **Table 10 is a 2018/2019 public-HMDA specification, with points controlled, lender-clustered, and — per its own footnote 31 — using tract-level credit deciles precisely because *"the HMDA data do not include individual credit scores."*** That is the tool's data source, the tool's vintage, the tool's fee posture, and the tool's exact credit-score handicap. §9 asserts *"No published study shares this tool's design"* while omitting the specification that shares four of its defining features.

**Every one of the three errors points the same direction: toward "no anchor exists, so drop it."** An argument whose mistakes are unanimous in favor of its conclusion is not a clerical problem — it is a motivated one. And this is not new information the doc lacked: **Audit-2's verification row 5c refuted this exact description in writing**, Audit-2's HIGH-3 proved the CRA claim backwards, `AUDIT-2-TRIAGE.md` **accepted both** — and then, in the same file, re-asserted *"excludes CRA tracts"* as a reason to drop the anchor. v3 shipped the refuted half. The false description **survived the audit that killed it** and became the premise of the reversal it justified.

This is the third consecutive round in which the thread's calibration material has asserted something false about this paper, and the second in which the error is a **2019-working-paper description substituted for the published work**. The corrective adopted one revision ago — *"the calibration section may be drafted ONLY from the published JFE tables read directly… If the published tables aren't in hand, the calibration section stays explicitly UNRESOLVED"* — was written for this section and did not survive to the next draft. **The house's worst failure mode is not merely still live; it has been load-bearing since Audit-1 and has never once been caught by the process that follows it.** It was caught only by re-reading the paper — which is the only thing that has ever caught it.

**What I am not saying.** I am not saying the anchor must be restored as a runtime band. §9 is right that a dev-time band never protects a named lender; it is right that a band built from five unquantified wedges risks false precision; and *"uncalibrated-and-disclosed"* for the runtime estimate is a defensible, arguably admirable posture for a tool that publishes names. **The objection is narrower and harder to escape:** you may not reach that conclusion through false statements about the source, and you may not delete the **dev-time drift check** while claiming synthetic recovery replaces it — because synthetic recovery cannot detect the failure the band existed to catch (HIGH-3), and the ±100 bps ceiling that nominally replaces it is ten times too wide to ever fire (MED-8). With the band gone, **nothing in v3 would catch a pooled national engine reading 40 bps** because the DTI tails were coerced away.

**The fix is bounded and cheap.** Rewrite §9's Bartlett paragraph from the accepted MS / published tables read directly. Re-take the decision. If the answer is still "uncalibrated" — argued from the **real** wedges (note-rate DV vs APR−APOR; lender×year FE vs none; GSE-only; pooled Latinx+African-American vs Black-only) — that survives, and I would sign it. Then restore the **dev-time national-pooled drift bound** (ruling 3: fail the build outside ±25 bps), which is the piece that actually protects users and costs nothing at runtime.

Do this before code. Everything else in this audit is a defect to fix; this is the one that decides whether the document's central reversal is a judgment or a rationalization — and right now it is supported by a description of a paper that does not exist.

---

### Gate
**NO-GO.** 3 CRIT, 6 HIGH open. Resolve CRIT-1/2/3 and HIGH-1–6 → v4 → this audit re-run against v4's §9 with the paper in hand → build.
