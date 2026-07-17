# AUDIT-2 — Hostile methodology audit of `methodology-v2-rate-spread.md`

**Auditor stance:** adversarial. Every citation and every ✅/"Verified" number treated as an unverified claim until confirmed against primary source. Sources fetched and quoted below; where a source could not be reached, that is stated.

---

## VERDICT: **NO-GO** — 5 CRIT, 8 HIGH open.

The §6 cost-field split (the version's load-bearing fix) is **substantively correct and confirmed**. The §3 rate_spread-over-note-rate argument is correct and confirmed. The §12 move from an R²/p gate to cluster-count + precision is correct and is *directly supported* by the anchor paper's own numbers.

But the calibration anchor is cited to a paper that does not contain the cited numbers; the version's headline new decision (§7 include-points) rests on a bias direction the anchor paper refutes on the tool's own data vintage; and the §4 selection sensitivity is structurally guaranteed to return a false reassurance while passing the reconciliation identity.

---

## CRIT

### CRIT-1 — §7's bad-control bias direction is refuted by the doc's own anchor, on the doc's own data vintage. The §9 safeguard points the wrong way.

**What's wrong.** §7: *"the direction is toward **attenuation** of the protected-class coefficient, which is why the calibration band's *lower* bound must catch it (§9)."*

Bartlett et al., accepted manuscript, **Table 10 — "Interest-rate differentials: 2018/2019 HMDA data controlling for points paid/total loan costs"** (GSE loans, lender-clustered SEs), extracted directly from the PDF:

| Panel | GSE Purchase | GSE Refi |
|---|---|---|
| (a) No controls for points or costs | 7.377*** (0.472) | 5.998*** (0.392) |
| (b) **Controlling for points paid** | **7.820*** (0.482) | **6.900*** (0.375) |
| (c) Controlling for total loan costs | 7.709*** (0.520) | 6.806*** (0.354) |

Adding points controls moved the minority coefficient **up** — +0.44 bps purchase, +0.90 bps refi. Anti-attenuation, on 2018/19 HMDA, which is the tool's exact data.

**Why it matters.** The *only* stated safeguard for a knowingly-included bad control is a calibration band **floor**. If the bias inflates rather than attenuates, a floor catches nothing. The tool would ship an unsignedly-biased coefficient with no guard, and it publishes lender names.

Theory agrees. Points are post-treatment and a **collider**: race → points ← borrower liquidity/wealth → spread. Conditioning on points induces a spurious race–wealth association of indeterminate sign. "Bias toward attenuation" is a property of classical measurement error, not of bad controls generally. If discrimination operates *through* steering borrowers into points — the doc's own §7 hypothesis — conditioning on points removes the mechanism from the coefficient entirely.

**Sharper still (see also CRIT-1b):** Table 10's DV is the **note rate**. The tool's DV is **APR − APOR**, and discount points are *inside* the APR (§1026.4(b)(3), verbatim: *"Points, loan fees, assumption fees, finder's fees, and similar charges"* are finance charges; §1026.4(a): the finance charge *"includes any charge payable directly or indirectly by the consumer and imposed directly or indirectly by the creditor as an incident to or a condition of the extension of credit"*). So §7 regresses an APR-based outcome on a **component of the APR that constructs that outcome**. The note-rate evidence therefore does *not* transfer cleanly to sign the tool's bias — which makes §7's confident signed claim *less* defensible, not more. The honest position is **sign unknown**.

**Fix (required).**
1. Delete the attenuation claim. It is unsupported and the nearest evidence contradicts it.
2. Report the pricing model **with and without** points/credits as a published pair of bounds. Never a single point estimate that silently embeds a bad control.
3. Add the **costs-as-outcome** regression. The anchor does exactly this — fn 33, verbatim: *"As a robustness check, we also run these regressions with total loan costs on the left hand side and interest-rate deciles on the right. As in Panel (c) of Table 10, the estimated coefficient on the minority indicator is significantly greater than zero in all regressions."*
4. Remove "the §9 band will catch it" entirely — see CRIT-2.

**Answering the audit's question directly — should points be an outcome, not a control?** *Both.* §7's stated worry (omitting points confounds the comparison with the points/rate tradeoff) is real — which is exactly why you publish the pair rather than pick a side.

---

### CRIT-2 — §7's justification invokes a mechanism §9 explicitly forbids.

**What's wrong.** §7 defends include-points with: *"the calibration band's lower bound must catch it (§9)."*
§9 states: *"Band is DEV-TIME engine calibration only, on a national pooled run. **It is NEVER a runtime gate on a named lender**."*

At runtime — the only moment a named lender is screened — nothing catches it. A dev-time national pooled check cannot see a per-lender bad-control bias.

**Why it matters.** The single most consequential new decision in v0.3.0 is defended by a safeguard the document elsewhere prohibits from operating in the relevant place. This is a flat contradiction, and §9's "NEVER" is the correct half (a national band wired to a per-lender check would silence true positives on the worst actors — §9's own MED-10 reasoning is sound).

**Fix.** §7 loses its defense. It must be replaced by CRIT-1's with/without pair, which *is* a runtime artifact.

---

### CRIT-3 — The §4 selection sensitivity is structurally guaranteed to be a no-op that reports a false reassurance — and the reconciliation identity passes.

**What's wrong.** CFPB *Reportable HMDA Data: A Regulatory and Reporting Overview Reference Chart* (2024, v1), verbatim:

- **Discount Points §1003.4(a)(19):** *"Enter "NA" for: **Applications**, Comment 4(a)(19)-1; Covered loans not subject to Regulation Z, § 1026.19(f)..."*
- **Lender Credits §1003.4(a)(20):** *"Enter "NA" for: **Applications**, Comment 4(a)(20)-1..."*
- **Origination Charges §1003.4(a)(18):** *"Enter "NA" for: **Applications**, Comment 4(a)(18)-1..."*
- **Total Loan Costs §1003.4(a)(17):** *"Enter "NA" for: TOTAL LOAN COSTS. **Applications**, Comment 4(a)(17)(i)-1..."*

`action_taken == 2` is an **application**. No Closing Disclosure exists, so all four cost fields are `NA` on **every** action-2 row.

Now compose the document's own rules:
- §6: `discount_points` — *"NA → exclude-with-reason"*
- §7: *"write the code to build **exactly** these regressors — no more, no less"*, including `β7 · discount_points_i` and `β8 · lender_credits_i`

⇒ The `{1,2}` run excludes **100%** of action-2 rows via `na_discount_points`. `{1,2}` silently collapses to `{1}`. The two estimates are identical **by construction**.

§4's interpretation rule then fires: *"if `{1}` and `{1,2}` diverge materially, selection is doing real work."* It reads zero divergence and concludes selection is **not** doing real work — a fabricated favorable finding, produced by a sensitivity that never ran.

**And the §11 identity passes.** `classified + excluded + reassigned == universe` holds exactly, because every dropped row is reason-keyed. This is the requested *"row that satisfies the identity while being wrong"* — and it is the portfolio's signature failure precisely: **a safety check that silently returns the reassuring answer.**

§4 half-sees this (*"cost fields are NA for non-originations, so `{2}` loses them"*) but never reconciles it with §7's "no more, no less," so the contradiction ships as code.

**Fix.**
1. `{1,2}` must be a **separately specified** model that drops all four CD-conditioned cost fields.
2. The comparison must run against a **control-matched `{1}`** that also drops them — otherwise population and control set change simultaneously and divergence is uninterpretable.
3. Hard assertion: the `{1,2}` run **must raise** if the action-2 count in the modeled sample is 0. A sensitivity that can silently become its own baseline is worse than no sensitivity.
4. See MED-7 — even correctly built, this is not a selection diagnostic.

---

### CRIT-4 — `intro_rate_period` is "NA" for every fixed-rate loan. §7 makes it a regressor; §6 has no rule for it. A generic NA-drop silently restricts the model to ARMs.

**What's wrong.** CFPB reference chart, **Introductory Rate Period §1003.4(a)(26)**, verbatim:

> *"Enter "NA" for: **Covered loan or application with a fixed rate**, Comment 4(a)(26)-3; Purchased covered loan with a fixed rate, Comment 4(a)(26)-4."*

Fixed-rate is the modal purchase origination. §7 lists `β6 · intro_rate_period_i` as a plain continuous regressor with a `# / rate_type where applicable` hand-wave. §6's per-field table covers 5 fields and does not include it.

**Why it matters.** Apply §6's discipline as written (NA → exclude-with-reason) and the tool drops the overwhelming majority of the population and estimates a pricing disparity on **adjustable-rate loans only** — a different market, a different pricing regime, a different borrower. The reconciliation identity passes. §7's `n` is reported as "post-exclusion modeled n," so the output looks clean and internally consistent. Nothing in the document catches it.

**Fix.** `intro_rate_period` is not a continuous control. Encode as: **fixed-rate indicator** (NA ⇒ fixed) **+ ARM intro period** (0 or NaN-in-interaction for fixed). Never numeric-coerce. Mutation test: a fixed-rate `NA` must survive as fixed-rate, not vanish.

---

### CRIT-5 — No minimum-year guard. Pre-2018 `rate_spread` is threshold-censored, and §6's blank rule **inverts** on it.

**What's wrong.** CFPB, *Data Point: 2018 HMDA — an updated review of the new and revised data points*:

> Previous: *"Rate spread was reported only when the APR exceeded the average prime offer rate by 1.5 percentage points or more."*
> Current: *"Institutions must now report rate spread for all covered loans and applications, regardless of whether the rate spread exceeds any particular threshold."*

For 2018+ there is **no censoring** — OLS is fine (see the distributional ruling below). But §5's filter list contains **no `activity_year >= 2018` filter**, and the sibling package (hmda-analyzer) is explicitly multi-year.

Point this at 2017 or earlier and two things happen:
1. `rate_spread` is left-censored at 1.5pp → OLS is mis-specified (genuinely Tobit territory), and
2. **worse** — blank now means *"priced below the threshold"*, a **real, favorable value**. §6 says *"blank/NA/Exempt → exclude-with-reason ... never 0"*. The tool drops every normally-priced loan and fits the model on the **subprime tail only**, producing a large, confident, meaningless number.

The identity passes. The output looks clean. This is the same class as CRIT-3.

**Fix.** **Hard-fail (raise) on any `activity_year < 2018`.** Not a warning, not a caveat. A permanent PyPI release must not contain a silently-wrong path this cheap to close.

---

## HIGH

### HIGH-1 — §9 cites JFE 143(1):30–56 (2022) for numbers that exist only in the superseded 2019 NBER working paper. The "Verified:" flag is false against its own citation.

**Verified by direct PDF extraction (my own, not delegated):**

| String | NBER w25943 (Jun 2019) | Accepted MS (May 4 2021, near-final JFE) |
|---|---|---|
| `7.88` | **2 occurrences** | **0** |
| `0.000788` | **2** | **0** |
| `0.000695` | **1** | **0** |
| `Panel A` | 15 | **0 anywhere in the paper** |
| `4.674` | 0 | **3** |
| `APOR` | **0** | **0** |

- **w25943 abstract, verbatim:** *"We find that lenders charge Latinx/African-American borrowers **7.9 and 3.6 basis points** more for purchase and refinance mortgages respectively, costing them **$765M** in aggregate per year in extra interest."*
- **Accepted-MS abstract, verbatim:** *"...we estimate that these rate differences cost minority borrowers over **$450 million** yearly."* No 7.9/3.6.
- **Published baseline, Table 3** (GSE/FHA, lender×year/month FE): GSE purchase **4.674*** (0.255), GSE refi **1.632*** (0.227).

§9 states: *"**Verified**: pooled Latinx/African-American coefficient 7.88 bps purchase (Table 4 Panel A col (1)) / 3.6 bps refi."* The numbers are real — **in w25943 Table 4**. The **citation is wrong**, and wrong in the direction of over-claiming: a peer-reviewed JFE article versus an unrefereed 2019 working paper whose headline results **did not survive review**.

This is exactly the failure mode this audit was told to assume is live: an asserted-as-verified fact that is false against its own cited source.

**Why it matters.** A lender's counsel pulls JFE 143(1), does not find 7.88, and the tool's entire calibration provenance collapses on cross-examination — along with the credibility of every other "verified" claim in the package.

**Fix.** Re-anchor to the published paper (see HIGH-2). If any WP number is retained, cite **NBER w25943 (2019)** explicitly and label it a working paper superseded on these numbers.

---

### HIGH-2 — The doc anchors to the wrong specification. The published paper contains a **2018/2019 HMDA** specification — the tool's exact data — and the doc doesn't use it.

Published **Table 10**: *"Interest-rate differentials: 2018/2019 HMDA data controlling for points paid/total loan costs."* Panel (b), controlling for points: **GSE purchase 7.820 (0.482)**, **GSE refi 6.900 (0.375)**. FE: lender×year, point-decile×year, cash-out×LTV-decile×year, cash-out×census-tract-credit-decile×year, amount-decile×year. SEs clustered at lender level.

This is dramatically closer to the tool than the 2009–2015 GSE-grid spec §9 uses: **same data source (HMDA), same vintage, points controlled, lender-clustered**. It remains note-rate (not APR−APOR), retains lender FE, and uses a tract credit-score proxy the tool lacks — but those are *documentable wedges off a matched baseline* instead of a decade-and-instrument-mismatched one.

**Consequence for refi — this is the sharpest damage.** §9: *"Refi: separate band centered on the 3.6 bps anchor."* The matched 2018/19 refi figure is **6.900** — nearly **2×** the doc's center. A 3.6-centered refi band flags a *correct* result as anomalous and **blesses an attenuated one**. §9's own logic ("a LOW result is the anomaly") is inverted by its own stale anchor.

**Fix.** Re-center on Table 10(b): ~7.8 purchase / ~6.9 refi, then apply a ledger of documented wedges from *that* baseline. See the [SET IN AUDIT-2] rulings.

---

### HIGH-3 — §9's CRA-tract wedge sign is refuted by the anchor's own successor analysis, at p<0.0001.

§9 ledger: *"Anchor excludes CRA tracts; tool includes them | **? (lean ↓)** | CRA incentives in those tracts pull the included-sample disparity down."*

Published **Table 6**, *"Interest-rate differentials by CRA status"*, GSE purchase, extracted verbatim:

```
Non-CRA tract × Minority   4.043***  (0.248)
CRA tract     × Minority   6.431***  (0.334)
p-value for test of equality  0.0000
```

Disparities are **significantly larger** in CRA tracts — the opposite of the doc's lean. Note also that the WP's stated reason for dropping CRA tracts was, verbatim: *"We additionally eliminate from our sample any loans made within a census tract covered by the Community Reinvestment Act of 1977 (CRA), **given the potential bias these census tracts would introduce** into our empirical analysis."* The published version **reversed that choice and analyzed them**.

**Why it matters, and the direction of harm.** A ↓ lean lowers the expected value → lowers the band floor → makes an attenuated engine look acceptable. It errs toward **false negatives**, in exactly the CRA tracts this tool's users care about most. For a CRA-adjacent advocacy tool this is the worst possible direction to be wrong in.

**Fix.** Flip to **↑**, cite Table 6.

---

### HIGH-4 — §9's vintage wedge (↓, "discrimination declining") is unsourced, and the closest matched comparison points the other way.

§9: *"Vintage 2009–2015 → 2018+ ("discrimination declining") | **↓** | anchor era had more; tool era should read lower."*

Nothing in the paper supports "discrimination declining." Closest matched pair, **both with lender FE, GSE purchase**: 2009–2015 (Table 3) = **4.674**; 2018/2019 HMDA (Table 10a) = **7.377**. The later vintage is **higher**.

The specs differ (Table 3 uses GSE-grid buckets with individual credit scores; Table 10 uses tract-level credit deciles), so this is not a clean causal vintage comparison — **and that is the point**: the doc asserts a confident *signed* wedge its own source does not support and the nearest evidence contradicts.

What the published abstract actually says about 2018/19 is about **FinTech convergence**, not declining levels — verbatim: *"These rate disparities were substantially lower for FinTech lenders for loans issued between 2009 and 2015, but there is no significant difference between FinTech and other lenders for loans issued in 2018 and 2019."*

**Fix.** Mark **?** or **↑** with the Table 3 vs Table 10(a) comparison stated, or delete the wedge. Do not carry an unsourced signed direction into a band bound.

---

### HIGH-5 — §9's fee wedge (↑) is inconsistent with §7's own spec.

The ledger says APR-embeds-fees pushes the tool's APR−APOR estimate **above** a note-rate anchor. But §7 **controls for** `discount_points` and `lender_credits` — and points are finance charges inside the APR (§1026.4(b)(3), quoted in CRIT-1). §7 therefore partially closes the very channel the wedge invokes.

Compounding it: if discrimination operates *through* fees — which the doc itself asserts (*"if minority borrowers face higher fees (the literature's consistent finding)"*) — then controlling for points/credits removes part of the mechanism from the coefficient. **You cannot simultaneously claim the fee channel inflates your estimate and control for the fee channel.**

The ledger was written for an uncontrolled-APR spec and was not updated when §7 decided to include fee controls.

**Not a total defect:** only points and credits are controlled; third-party and origination charges are not (§7 excludes `total_loan_costs`/`origination_charges`), so a **residual** fee wedge survives.

**Fix.** State which fees are controlled and which are not, and sign only the **residual** wedge.

---

### HIGH-6 — §6's per-field discipline is applied to 5 fields. The other regressors carry their own conventions and are unspecified — a blanket-shaped hole in the middle of the blanket-rule fix.

All rows below are verbatim "Enter NA for" conditions from the CFPB reference chart. Every one of these fields is also in the §1003.3(d) partial-exemption set and can literally read `Exempt`.

| Regressor | Field | Unhandled NA/Exempt conditions |
|---|---|---|
| `combined_LTV` | (a)(24) | purchased loans; no credit decision; **"credit decision was made without relying on combined loan-to-value ratio"** (Cmt 4(a)(24)-4) — *occurs on originated loans*. Exempt. |
| `DTI` | (a)(23) | purchased; no credit decision; **"credit decision made without relying on debt-to-income ratio"**; **applicant and co-applicant not natural persons**. Exempt. Platform *"can accept **negative numbers**"*. |
| `property_value` | (a)(28) | no credit decision; **"credit decision was made without relying on property value"** (Cmt 4(a)(28)-4). Exempt. Public file: *"Rounded to the midpoint of the nearest $10,000 interval."* |
| `applicant_income` | (a)(10)(iii) | income not considered; **applicant not a natural person**; multifamily. *"Round all dollar amounts to the nearest thousand."* |
| `loan_term` | (a)(25) | no definite term. Exempt. |
| `intro_rate_period` | (a)(26) | **fixed rate** — CRIT-4. |
| `occupancy_type` | (a)(6) | codes 1/2/3, no NA — **clean**. |
| `lien_status` | (a)(14) | codes 1/2, no NA — **clean**. |

§6 correctly argues the blanket rule is wrong and replaces it with per-field discipline — **then applies that discipline to the cost fields only**. The TDD requirement (*"one sentinel mutation test per field per state"*) is likewise scoped to §6's five fields.

**Fix.** Extend the §6 table to **all 13 regressors + outcome** before code. Per row: field, source (FIG/chart — see MED-1), *every* NA cause, Exempt encoding (literal `Exempt` vs code `1111`), handling. Note §6's claim *"`1111` is never a global sentinel"* is **confirmed correct** — coded/enumerated fields use `Code 1111—Exempt` (e.g. Credit Score (a)(15), Balloon Payment (a)(27)) while free-text numeric fields use the literal `Exempt`.

---

### HIGH-7 — `log()` of income/property_value has no guard, and the drop happens *after* the identity runs.

§7: `β4 · log(applicant_income_i)` and `β3 · log(property_value_i)`.

- Income is reported **in thousands, rounded to the nearest $1,000** (chart, verbatim: *"Round all dollar amounts to the nearest thousand (round $500 up to the next $1,000). Example: If the income amount is $35,500, enter 36."*). An applicant under $500 rounds to **0** → `log(0) = -inf`.
- `property_value` is NA'd whenever the credit decision didn't rely on it — on originated loans.

Neither is random: zero/low income correlates with non-natural-person applicants and income-not-considered decisions; both correlate with loan channel and with protected class.

**Why this one is structurally the worst.** A silent `-inf`/NaN drop inside statsmodels happens **after** the §11 reconciliation runs. The identity *cannot* catch it — the rows are `classified`, then vanish from the design matrix. `n` is reported as "post-exclusion modeled n" (§7), which is *not* the same as the regression's actual row count once the design matrix is built.

**Fix — and this single change closes the whole class.**
1. Exclude-with-reason at the **loader**, before the design matrix: `nonpositive_income`, `na_property_value`.
2. **Assert `design_matrix.shape[0] == classified_count`.** Any row that dies between reconciliation and estimation must raise. This is the one guard that makes CRIT-3, CRIT-4, HIGH-7 and MED-8 fail loudly instead of silently.

---

### HIGH-8 — The tool structurally cannot screen any bank or credit union under 500 closed-end originations, and the doc never says so.

§1003.3(d)(1) defines **"optional data"** as: *"Data identified in § 1003.4(a)(1)(i), (a)(9)(i), and **(a)(12), (15)–(30), and (32)–(38)**."*

That set contains the **outcome** ((a)(12) `rate_spread`) and essentially **every regressor**: (a)(17)–(21) costs and rate, (a)(23) DTI, (a)(24) CLTV, (a)(25) loan term, (a)(26) intro rate, (a)(28) property value. Partially exempt institutions — **insured depository institutions and insured credit unions** originating fewer than 500 closed-end mortgage loans in each of the two preceding years — report **none of them**. (Non-depository mortgage companies are *not* eligible for the partial exemption and always report in full.)

Three unstated consequences:
1. A partially exempt lender is **unscreenable** — every row excluded as `exempt_rate_spread`. For a community-advocacy tool whose users care about community-scale banks and credit unions, that is a **headline scope boundary**, not a footnote. It is also precisely the CDFI-adjacent population this portfolio serves.
2. §1003.3(d)(3)–(4) permit **voluntary** reporting. So sub-500 lenders present in the estimation sample are a **self-selected subset** of sub-500 lenders — biasing the national pooled **calibration run itself** (§9), the very thing the band is set against.
3. Interaction with §8's cluster floor: these lenders don't *fail* the floor, they **never appear**. Suppression never fires because there is nothing to suppress. The tool reports a clean result on a silently truncated lender universe.

**Fix.** State the ≥500 coverage boundary in §2 (Out) and §13. On a single-lender screen of a partially exempt LEI, raise a **distinct explicit error** — "this lender is partially exempt under §1003.3(d); pricing screening is not possible" — rather than returning n≈0 or a voluntary-subset estimate.

---

## MED

### MED-1 — §6's table attributes FIG/reference-chart language to the CFR. The load-bearing quotes are not in the cited sections.

§6's table column is headed **"Reg C cite"** and its "blank means" cells carry quotes: `discount_points` §1003.4(a)(19) — *"if no points were paid, leave blank"*; `lender_credits` §1003.4(a)(20) — *"if no lender credits, leave blank"*.

**Actual §1003.4(a)(19), verbatim:** *"For covered loans subject to the disclosure requirements in Regulation Z, 12 CFR 1026.19(f), the points paid to the creditor to reduce the interest rate, expressed in dollars, as described in Regulation Z, 12 CFR 1026.37(f)(1)(i), and disclosed pursuant to Regulation Z, 12 CFR 1026.38(f)(1)."*

**Actual §1003.4(a)(20), verbatim:** *"For covered loans subject to the disclosure requirements in Regulation Z, 12 CFR 1026.19(f), the amount of lender credits, as disclosed pursuant to Regulation Z, 12 CFR 1026.38(h)(3)."*

**Neither contains "leave blank."** That language is CFPB **filing instruction**, not regulation.

**The substance of §6's split is CORRECT and confirmed** (see the verification log): discount points and lender credits use blank-means-zero; total loan costs and origination charges report a real zero as `0`. **The §6 fix holds.** Only the attribution is wrong.

**Why it matters anyway.** The doc's own house rule is primary-source-at-write-time, and the package is branded *"the methodology federal examiners use."* Citing the CFR for a filing-instruction convention is what opposing counsel uses to establish the author didn't read the sources. Cheap to fix, expensive to leave.

**Fix.** Re-head the column **"Source"**; cite the FIG / *Reportable HMDA Data* reference chart (with edition + date) for the blank/zero conventions, and the CFR only for the field definition.

---

### MED-2 — §9's spec-match rationale for col (2) is wrong, though the cell choice is defensible.

§9: *"the tool's spec (pooled national, MSA FE, **no lender FE**) maps to Bartlett Table 4 Panel A col (2) ≈ 6.95 bps, not the headline 7.88."*

**Actual w25943 Table 4, "Robustness to Lender and Geography Fixed Effects", Panel A: Purchases:**

```
                          (1)        (2)        (3)        (4)
Latinx-/African-American  0.000788   0.000695   0.000545   0.000516
                         [3.11e-05] [2.41e-05] [2.67e-05] [3.26e-05]
Month-Year FE                Y          Y          Y          Y
GSE Grid FE                  Y          Y          Y          Y
County FE                    N          Y          Y          Y
Lender FE                    N          N          Y          Y
County x Lender FE           N          N          N          Y
```

Table note, verbatim: *"Column (1) repeats the OLS estimate of Table 2... **Column (2) adds county fixed effects; column (3) adds lender fixed effects**; column (4) adds lender crossed with county fixed effects."*

Col (1) and col (2) **both lack lender FE**. "No lender FE" does not distinguish them; **county FE** does. Also: **"Panel A" means Purchases**, not a specification panel (Panel B is Refinances).

**Rulings, precisely:**
- *"Table 4 Panel A col (1) = 7.88"* — **the doc is CORRECT.** (Table 4 col (1) repeats Table 2 col (2) = 0.000788.)
- *"col (2) ≈ 6.95"* — **the doc is CORRECT** (0.000695).
- *"col (2) corresponds to the no-lender-FE spec"* — **the doc's rationale is WRONG**, but its **cell choice is defensible**: col (2) is geography-FE + no-lender-FE ≈ the tool's MSA-FE + no-lender-FE. Right cell, wrong reason.

**What the doc missed, and it matters:** Table 4 shows lender FE cut the estimate **7.88 → 5.45** (col 3). So a **no-lender-FE** tool should read *above* a lender-FE anchor — **another ↑ the ledger omits**, and one that bears directly on HIGH-2's 7.82 (which carries lender×year FE).

---

### MED-3 — §7's occupancy dummies are guaranteed degenerate; "no more, no less" makes this a singular design matrix.

§5: `occupancy_type == 1`. §7: `+ Σ β · occupancy_type_i  # (occ==1 filtered, so only if variation remains)`. Occupancy is codes 1/2/3 with no NA (chart). After the filter there is exactly one level → **perfect collinearity with the intercept**.

The parenthetical hedge ("only if variation remains") directly contradicts §7's own governing instruction: *"write the code to build exactly these regressors — no more, no less."*

**Fix.** Decide: keep the filter and **delete the term**, or drop the filter and keep the dummies (which changes scope — investment-property pricing is a different market and the anchor is owner-occupied).

---

### MED-4 — §5 filters a field that does not exist in HMDA.

§5: *"`loan_to_value_ratio ≤ 100`"*. There is **no** `loan_to_value_ratio` data point in Reg C. The only LTV field is **Combined Loan-to-Value Ratio, §1003.4(a)(24)** — confirmed: every LTV entry in the reference chart is "Combined Loan-to-Value Ratio"; a bare LTV appears nowhere. §7 correctly uses `combined_LTV`.

Either §5 means CLTV — in which case it collides with MED-5 — or it inherited a field name from the denial engine that does not exist here. Either way §5 as written does not run.

---

### MED-5 — §2 admits subordinate liens; §9 anchors to a first-lien-only study; §5 then filters CLTV ≤ 100. Three sections, three incompatible populations.

§2 In: *"first-lien and subordinate-lien."* §9's anchor is 30-yr fixed **first-lien** GSE loans. §5 filters CLTV ≤ 100 — which removes much of the subordinate-lien population **by construction** (subordinate liens are exactly where CLTV runs high), while a lien dummy in §7 absorbs the rest.

**The doc's own principle, applied to itself.** §2 excludes FHA/VA because: *"Priced on structurally different mechanics... a loan-type dummy is a weak control for that, and pooling diverges from the calibration anchor (§9)."* Every clause applies with equal force to subordinate liens. The doc applies the principle to `loan_type` and not to `lien_status`.

Corroborating: **HPML thresholds themselves differ by lien** — 1.5pp first-lien vs 3.5pp subordinate (§1026.35(a)(1), verified) — precisely because subordinate-lien spreads are structurally higher. The regulator treats them as different pricing regimes; so should the tool.

**Fix.** **First-lien only in v0.3.0**, matching the anchor and the doc's own stated principle. Subordinate-lien as a separately-calibrated config — identical treatment to FHA/VA.

---

### MED-6 — rate_spread reportability is not {1, 2}. It is {1, 2, 8} — and the doc's own rationale argues for including 8.

**Comment 4(a)(12)-8, verbatim:** *"In the case of an application **or preapproval request** that was approved but not accepted, § 1003.4(a)(12) requires a financial institution to report the applicable rate spread."*

**Comment 4(a)(12)-7, verbatim:** *"If the application did not result in an origination **for a reason other than** the application was approved but not accepted by the applicant, a financial institution complies with § 1003.4(a)(12) by reporting that the requirement is not applicable."*

Action taken **code 8 = "Preapproval request approved but not accepted"** (chart). §4 claims the field is reported for "1 and 2" and builds its sensitivity on `{1,2}`. Action 8 is the **purest instance of §4's own logic** — *"a price the lender offered, uncontaminated by the borrower's accept/decline decision"* — and it is silently absent.

Volume is small (preapproval programs only, purchase only), so this is a correctness/consistency defect rather than a power issue. But §4's factual claim about reportability is wrong as written.

**Fix.** State the reportable set as **{1, 2, 8}** and either include 8 or exclude it on its own stated terms.

---

### MED-7 — §4's {1} vs {1,2} comparison changes the outcome's **measurement instrument**, not just the population. It is not a selection diagnostic even after CRIT-3 is fixed.

**Comment 4(a)(12)-8, verbatim:** *"...the financial institution would provide early disclosures under Regulation Z, 12 CFR 1026.18 or 1026.37 (for closed-end mortgage loans)... but might never provide any subsequent disclosures. In such cases where no subsequent disclosures are provided, a financial institution complies with § 1003.4(a)(12)(i) by **relying on the annual percentage rate for the application or preapproval request, as calculated and disclosed pursuant to Regulation Z, 12 CFR 1026.18 or 1026.37**."*

So action-2 `rate_spread` is computed from the **Loan Estimate APR**; action-1 `rate_spread` from the final **Closing Disclosure** APR. Pooling them puts **two different measurements** in the same `Y`. LE APRs are estimates that systematically differ from final APRs.

Further, from the chart: rate_spread is NA for *"Applications approved but not accepted, **if no disclosures under Regulation Z are required**"* — a non-random hole **inside** `{2}`.

**Ruling on the audit's question — "is the sensitivity actually diagnostic of selection?"** **No.** It is confounded three ways:
1. **Control-set change** (CRIT-3 — all four cost fields vanish),
2. **Outcome-instrument change** (LE APR vs CD APR — this finding),
3. **`{2}` is itself a selected population** — borrowers who shop and walk are not random; a lender's action-2 pool skews toward borrowers who got a better offer elsewhere, which correlates with shopping intensity, which correlates with race in the literature. `{2}` **changes** the bias rather than revealing it.

**Ruling on the audit's second question — is the doc right to keep `{2}`-only out of scope?** **Yes** — but not for its stated reason. `{2}`-only has no cost controls, an LE-APR outcome, and a doubly-selected population. It is not "the better lender-conduct population"; it is a *differently* biased one. Keeping it out is correct.

**But §4 must stop calling `{1,2}` a *selection* sensitivity.** It is a bounding exercise with three moving parts.

**Fix.** Rename to **"alternative-population bound"**, state all three confounds, and per CRIT-3 run it against a **control-matched `{1}`**.

---

### MED-8 — DTI's public encoding is a mixed-type column, and §7 cites the CFR for a binning the CFR doesn't specify.

§7: `Σ β · DTI_bin_i  # categorical, §1003.4(a)(23) encoding`.

**§1003.4(a)(23), verbatim:** *"Except for purchased covered loans, the ratio of the applicant's or borrower's total monthly debt to the total monthly income relied on in making the credit decision."* The reg requires a **continuous ratio** — chart: *"Enter, as a percentage... The HMDA Platform can accept up to fifteen (15) decimal places and can accept negative numbers."*

The binning is a **CFPB public-file modification**, not a Reg C encoding. Public LAR documentation bins DTI as: `<20%`, `20%-<30%`, `30%-<36%`, individual values `36`–`49`, `50%-60%`, `>60%`, `NA`, `Exempt`.

**That column is mixed `str`/`int`.** `pd.to_numeric(..., errors='coerce')` turns every string bin into `NaN` — **silently deleting the entire low-DTI and high-DTI tails** (the best and worst credits) and keeping only the 36–49 middle. A swallow-to-empty analogue with strong monotone selection on a price driver, and the drop is *correlated with the outcome*.

§7's "categorical" instinct is **right**; the citation hides the hazard and no §6 row governs it.

**Fix.** Cite the public LAR data-fields documentation; specify the exact 8-level categorical + NA/Exempt handling; **forbid numeric coercion**; mutation test per level.

---

## LOW

- **LOW-1 — §3 is the strongest section and survives intact.** `interest_rate` presence confirmed: §1003.4(a)(21), verbatim — *"The interest rate applicable to the approved application, or to the covered loan at closing or account opening"*; chart: *"Enter "NA" for applications that have been denied, withdrawn, or closed for incompleteness"* ⇒ it **is** reported for actions 1 and 2. The deletion of the false "no note rate" limitation (Audit-1 HIGH-7) is **correct and verified**. The rate_spread-over-note-rate argument (public LAR has `activity_year` only; APOR was matched at the rate-set date before that date was stripped) survives adversarial pressure and is the document's best reasoning.
- **LOW-2 — §14's HPML "verified current" holds** (see log). But §14's own framing — *"Citations (to verify verbatim in the full-doc pass)"* — is an admission that §9's "**Verified:**" claim was written *before* verification. That process defect is the direct cause of HIGH-1. The house rule didn't fail; it wasn't run.
- **LOW-3 — §12's suppression AND-gate is sound but may be strippable.** *"suppress the lender name ... unless ALL hold"* — nothing states these are non-overridable. If any becomes a constructor kwarg, an advocate (or a defendant's expert) flips it. **Fix:** no public parameter may relax suppression; add a test asserting it.

---

## Firewall ruling

**Clean.** §1 correctly places regression-adjusted pricing on the inferential side; §13 carries the caveats; §12 never says "discrimination" or "overcharging" in user-facing output. Nothing leaks toward a finding. Nothing belongs in hmda-analyzer — the raw unadjusted distribution is correctly carved out as a separate future decision.

One note, not a breach: §9's ledger reasons in prose about *"discrimination declining"* and *"the anchor era had more"* — asserting empirical claims about levels of discrimination as fact. This is internal calibration prose, never user output, so the firewall holds. But the phrasing asserts what HIGH-4 shows the doc cannot source. Fix the sourcing and soften to the evidence.

---

## OLS distributional ruling (audit task 2, item 2)

**Survives — for 2018+ only.** The doc's choice is right; its stated justification (*"continuous outcome → linear model"*) is thin, but the conclusion holds under pressure.

- **Censoring:** none post-2018 (verified — CRIT-5). Pre-2018 it is **fatal**, and CRIT-5's year guard is the entire answer. This is the one place Tobit would genuinely be required — which is the reason to refuse the data rather than model it.
- **Negative values:** real and reported. Chart, verbatim: *"If the APR is less than the APOR, enter a negative number. Example: If the APR 3.1235% and the APOR is 3.25%, enter -0.1265."* So rate_spread is genuinely two-sided. No log, no non-negativity assumption. This **strengthens** §6: `0` is not a floor, it is mid-distribution — the "never impute 0" rule is more important than §6 argues.
- **Skew / mass points:** rate sheets quote in eighths, so rate_spread has heavy discrete clustering and a long right tail. **Neither breaks OLS.** OLS still consistently estimates the best linear approximation to the CEF, which is the estimand a screening tool wants. Non-normal residuals are irrelevant at n ≈ 10⁵–10⁶.
- **Where it actually bites:** inference, not point estimation — and the doc **already routed that correctly** to cluster-robust SEs and a cluster-count floor. Internally consistent.
- **Do NOT add Tobit** (no censoring to model post-2018). **Do not** switch to quantile as primary. **Worth adding as a published secondary:** median/quantile regression — the mass points and right tail mean the mean and median effects can diverge, and a disparity concentrated in the **upper tail** is the policy-relevant one. Optional, not blocking.

---

## Cluster ruling (audit task 2, item 4)

**The doc's move from R²/p to cluster-count + CI-width is correct**, and it gets *direct primary-source support* the doc didn't know it had: Table 10's R² is **0.376–0.386** versus Table 3's **0.803** — same paper, same estimand, R² **halves** purely because HMDA lacks individual credit scores, while the coefficient stays significant at 1%. That is exactly §12's argument ("fit is not the risk; precision is"), demonstrated by the anchor.

**Does it close the manufactured-significance → unsuppressed-name path?** *Mostly — but it moves one leak.* With few clusters, cluster-robust SEs are downward-biased; wild-cluster bootstrap (Cameron–Gelbach–Miller) is the standard fix. But a bootstrap **rescues power** — it does not rescue a screen where one lender is 60% of the rows. The real risk is not cluster *count*, it is **cluster imbalance**: effective clusters can be ≈4 when raw G = 50 if one lender dominates. **A raw count floor passes that case.**

**Ruling:** a **hard floor is the honest choice** for a name-publishing tool. A wild bootstrap that converts "can't tell" into a publishable p-value is exactly the wrong trade for this deliverable's risk profile — it manufactures the confidence the floor exists to withhold. **But the floor must be on *effective* clusters, not raw count.**

---

## [SET IN AUDIT-2] rulings

### 1. Cluster-count floor — doc: `~30–50`
**Ruling: defensible as a range, but under-specified in the wrong dimension.**
**Propose: `G_eff ≥ 30` AND raw `G ≥ 30`**, where `G_eff = 1 / Σ_g (n_g/n)²` (inverse-Herfindahl of cluster shares).
**Reasoning:** ~30–50 tracks the standard cluster-asymptotics rule of thumb (Cameron & Miller's survey puts the danger zone below ~30–50) — so the doc's provisional value is **not arbitrary**; it's the conventional band. Take the conservative end: 30 is a floor, not a target, because the tool publishes names. The addition that matters is `G_eff` — mortgage markets are Herfindahl-heavy, and a single-MSA screen with 45 lenders where the top 3 hold 70% of originations has `G_eff ≈ 6`. Raw-count-only lets that through.
**Also:** on a single-lender screen §8 falls back to clustering on MSA. Apply the same `G_eff` test to MSAs — **and state that the fallback is weaker**: rate sheets are national, so lender×MSA residual correlation is *not* removed by MSA-clustering one lender's loans. §8 currently presents the fallback as equivalent. It isn't.

### 2. Purchase band — doc: `4–15 bps`, centered `~6.95`
**Ruling: center is wrong (HIGH-2); floor is too permissive under the corrected ledger.**
**Propose: center ~8 bps; flag outside `5–16 bps`.**
**Reasoning — from the matched anchor, not assertion.** Start at **Table 10(b) GSE purchase = 7.82** (2018/19 HMDA, points controlled, lender-clustered) — same data, same vintage, same fee-control posture as the tool. Then apply *sourced* wedges:
- (a) tool has **no lender FE**; Table 10 has lender×year FE. Table 4 shows lender FE moves 7.88 → 5.45 ⇒ removing it is worth roughly **+2** (bounded, not exact — different spec). *[MED-2; the doc omits this wedge entirely]*
- (b) tool omits the anchor's tract-credit-decile control ⇒ **+** (OVB; **verified**: 9.03 raw → 7.88 with grid — §9's OVB ↑ is the one wedge that checks out)
- (c) DV is APR−APOR with only points/credits controlled vs anchor's note rate ⇒ residual fee wedge **+**, magnitude unknown *[HIGH-5]*
- (d) Black-only vs pooled ⇒ **?**
- (e) tool includes CRA tracts; Table 6 shows those run **higher** ⇒ **+** *[HIGH-3 — doc has this backwards]*
Net expected value is plausibly **8–11**, not 6.95. **A floor of 4 sits well below anything the sources support and would bless a materially attenuated engine** — which is precisely the failure §9 says it exists to prevent.
**Width:** do not go narrower than ±~50% of center. The wedges are directional, not quantified; a tight band on an order-of-magnitude calibration is false precision. §13 already concedes this (*"order-of-magnitude, not a tight band"*) — §9's 4–15 should stop implying otherwise.

### 3. Refi band — doc: *"centered on the 3.6 bps anchor"*
**Ruling: reject. The center is wrong by ~2×.**
**Propose: center ~7 bps; flag outside `4–14 bps`.**
**Reasoning:** 3.6 comes from w25943 Table 2 col (4) — 2009–2015, GSE grid, note rate. The matched figure is **Table 10(b) GSE refi = 6.900** (2018/19 HMDA, points controlled). The vintage gap is **much larger for refi than purchase** (1.632 → 5.998 raw; 3.6 → 6.9 matched), so **refi is exactly where the stale anchor does the most damage**. The same +lender-FE-removal and +OVB wedges apply.
**Additional defect:** §5 says refi `31` and cash-out `32` *"run separately"*, but §9 gives **one** refi band. Every anchor spec is `cash-out × ...` interacted — cash-out and rate/term refis price differently. **Two bands, or one band explicitly scoped to `loan_purpose == 31` only.**

### 4. CI-width threshold — doc: unset
**Ruling: an absolute bps width alone is the wrong instrument.**
**Propose: suppress the name unless 95% CI half-width `≤ 5 bps` AND `≤ 1.0 × |point estimate|`. Both must hold.**
**Reasoning:** the **absolute** limb stops the tool naming a lender on a "12 bps ± 11" reading — technically CI-excludes-zero, consistent with anything from 1 to 23. Calibration for the 5 bps figure: the matched anchor's SEs run ~0.4–0.5 bps on ~1.3M loans *with* lender FE; a single-lender screen at 10³–10⁴ loans with clustered SEs will run an order of magnitude wider. So a 5 bps half-width is **achievable for a large lender and correctly unachievable for a small one** — which is the intended sorting, and it makes the threshold a real constraint rather than a formality. The **relative** limb stops a large-but-imprecise estimate qualifying purely because it is large.

### 5. Condition-number threshold — doc: unset
**Ruling: keep it, but it is the least load-bearing of the four, and the doc's framing invites a mistake.**
**Propose: κ (on the *column-standardized* design matrix) > 30 → suppress; AND VIF > 10 on the protected-class column specifically → suppress. Make VIF primary, κ a secondary sanity check.**
**Reasoning:** the conventional κ>30 threshold (Belsley–Kuh–Welsch) is defined on a **standardized** matrix. `statsmodels`' `cond_no` on a raw design carrying MSA dummies and `log(loan_amount)` will be enormous for reasons unrelated to the protected-class coefficient — so a naive κ gate either suppresses everything or gets tuned into meaninglessness. The quantity that actually matters is collinearity **of the protected-class regressor**, which is what its VIF measures.
**And §12 should state the tension it currently hides:** with MSA FE in a segregated market, geography and the protected-class indicator are **substitutes** — the more geography you absorb, the more of the disparity you absorb with it. That is a **limitation to disclose**, not a diagnostic to pass. A low protected-class VIF is reassuring; a high one may reflect segregation rather than a modeling error, and suppressing on it silently drops the most segregated markets — the ones that matter most. Suppress, but log the reason distinctly.

---

## Independent verification log

Every item below was fetched and read by me. eCFR (`ecfr.gov`) **bot-blocked with a 302 to `unblock.federalregister.gov`** and **was not reached**; regulatory text was obtained from Cornell LII and CFPB's own publications instead, as noted per row.

| # | Doc claim | Source actually read | Operative quote | Held? |
|---|---|---|---|---|
| 1 | HPML thresholds 1.5 / 2.5 / 3.5 pp over APOR, current | consumerfinance.gov/rules-policy/regulations/1026/35 | *"By **1.5** or more percentage points for loans secured by a first lien with a principal obligation... that does not exceed the [Freddie Mac conforming] limit"*; *"By **2.5** or more percentage points for [first-lien jumbo]"*; *"By **3.5** or more percentage points for loans secured by a subordinate lien"* | ✅ **HELD** |
| 2a | `discount_points` §1003.4(a)(19): blank = real 0 | CFPB *Reportable HMDA Data* chart 2024 v1 (PDF, extracted) | *"Enter, in dollars, the points paid to the creditor to reduce the interest rate. **If no points were paid, leave this field blank.**"* | ✅ **substance HELD**; ❌ **cite wrong** (MED-1) |
| 2b | `lender_credits` §1003.4(a)(20): blank = real 0 | same | *"Enter, in dollars, the amount of lender credits. **If no lender credits were provided, leave this field blank.**"* | ✅ **substance HELD**; ❌ cite wrong |
| 2c | `total_loan_costs` §1003.4(a)(17): real 0 reported as `0` | same | *"TOTAL LOAN COSTS. Enter, in dollars, the amount of total loan costs. **If the amount is zero, enter 0.**"* | ✅ **HELD** |
| 2d | `origination_charges` §1003.4(a)(18): real 0 reported as `0` | same | *"Enter, in dollars, the total of all itemized amounts that are designated borrower-paid at or before closing. **If the total is zero, enter 0.**"* | ✅ **HELD** |
| — | **§6 table verdict** | — | **All four cells correct. The load-bearing split is sound.** Attribution to the CFR is not (MED-1). | ✅ |
| 3 | `rate_spread` reported for action 1 **and 2** | Cornell LII 12 CFR §1003.4; CFPB Interp-4 | §1003.4(a)(12): *"For covered loans **and applications that are approved but not accepted**, and that are subject to Regulation Z... other than assumptions, purchased covered loans, and reverse mortgages, the difference between the covered loan's annual percentage rate and the average prime offer rate..."* | ✅ **HELD** — but **incomplete**: also action **8** (MED-6) |
| 3b | Commentary 4(a)(12)-7 = not-applicable list excludes approved-not-accepted | CFPB Interp-4 (Official Interpretations) | *"If the application did not result in an origination **for a reason other than the application was approved but not accepted** by the applicant, a financial institution complies... by reporting that the requirement is not applicable. **For partially exempt transactions under § 1003.3(d), an insured depository institution or insured credit union is not required to report the rate spread.**"* | ✅ **HELD** — doc **missed** the partial-exemption sentence (HIGH-8) |
| 3c | Commentary 4(a)(12)-8 = which APR to use | CFPB Interp-4 | *"In the case of an application **or preapproval request** that was approved but not accepted... a financial institution complies with § 1003.4(a)(12)(i) by relying on the annual percentage rate for the application or preapproval request, as calculated and disclosed pursuant to Regulation Z, **12 CFR 1026.18 or 1026.37**"* | ✅ HELD — doc **missed** the LE-vs-CD APR consequence (MED-7) and action 8 (MED-6) |
| 4 | `interest_rate` in public LAR, §1003.4(a)(21) | Cornell LII; CFPB chart; FFIEC public LAR fields | §1003.4(a)(21): *"The interest rate applicable to the approved application, or to the covered loan at closing or account opening."* Chart: *"Enter "NA" for applications that have been denied, withdrawn, or closed for incompleteness."* | ✅ **HELD** — §3's deletion of the false limitation is correct |
| 5a | Bartlett: 7.88 bps purchase / 3.6 refi | **NBER w25943 PDF, extracted by me** | Abstract: *"lenders charge Latinx/African-American borrowers **7.9 and 3.6 basis points** more for purchase and refinance mortgages respectively, costing them **$765M**"* | ⚠️ **numbers real — but in the 2019 WP, NOT in JFE 2022** (HIGH-1) |
| 5b | DV is note rate, not APR/APOR | w25943 + accepted MS, both extracted | w25943 Table 2/4: *"Dependent Variable: Mortgage Interest Rate"*. `APOR` = **0 occurrences in either paper**. | ✅ **HELD** — doc's HIGH-4 correction is right |
| 5c | Population: conventional-conforming, 30-yr fixed, 2009–2015, excludes FHA/VA/USDA **and** CRA tracts | w25943, extracted | *"we filter the data to focus on 30-year, fixed-rate, single-family residential loans, securitized by the GSEs over the period 2009 through 2015. We additionally eliminate from our sample any loans made within a census tract covered by the Community Reinvestment Act of 1977 (CRA), given the potential bias these census tracts would introduce"* | ✅ **HELD for the 2019 WP** — ❌ **refuted for the published paper**, where FHA is co-equal and CRA tracts are included and analyzed (HIGH-3) |
| 5d | SEs clustered at lender level | w25943 + accepted MS | w25943 Table 2 note: *"Standard errors are clustered at the lender level."* Accepted MS Tables 3/4/6/10: same. | ✅ **HELD** |
| 5e | **"Table 4 Panel A col (2) ≈ 6.95 corresponds to the tool's no-lender-FE spec"** | **w25943 Table 4, extracted verbatim** | Note: *"Column (1) repeats the OLS estimate of Table 2... **Column (2) adds county fixed effects; column (3) adds lender fixed effects**..."* FE rows Panel A: County FE `N Y Y Y`; **Lender FE `N N Y Y`** | ⚠️ **SPLIT**: `col(1)=7.88` ✅; `col(2)=6.95` ✅; **"no-lender-FE" rationale ❌ WRONG** — col (1) *also* has no lender FE; the discriminator is **county FE**. "Panel A" = **Purchases**, not a spec panel. Cell choice defensible, reason wrong (MED-2) |
| 5f | Published-version cross-check | **Accepted MS (May 4 2021), extracted** | `7.88` → **0 hits**; `6.95` → **0**; `Panel A` → **0**. Table 3 baseline: GSE purchase **4.674** (0.255), refi **1.632** (0.227). Abstract: *"over **$450 million** yearly."* Table 4 = *"Interest-rate differentials: FinTech vs. non-FinTech lenders"* — **no panels**. | ❌ **doc's citation does not contain the doc's numbers** (HIGH-1) |
| 5g | *(not claimed by doc — found in audit)* | **Accepted MS Table 10, extracted** | *"Interest-rate differentials: **2018/2019 HMDA data controlling for points paid/total loan costs**."* (a) no controls: **7.377** / **5.998**; (b) **controlling for points: 7.820 / 6.900**; (c) total loan costs: **7.709 / 6.806** | 🔴 **REFUTES §7's attenuation claim (CRIT-1); supplies the correct anchor (HIGH-2)** |
| 5h | *(not claimed by doc — found in audit)* | Accepted MS Table 6, extracted | Non-CRA × Minority **4.043** (0.248); **CRA tract × Minority 6.431** (0.334); *"p-value for test of equality **0.0000**"* | 🔴 **REFUTES §9's CRA wedge sign (HIGH-3)** |
| 6 | *(not claimed)* pre-2018 censoring | CFPB *Data Points: updated review of HMDA* | Previous: *"Rate spread was reported only when the APR exceeded the average prime offer rate by 1.5 percentage points or more."* Current: *"Institutions must now report rate spread for all covered loans and applications, regardless of whether the rate spread exceeds any particular threshold."* | 🔴 **CRIT-5 — no year guard exists** |
| 7 | *(not claimed)* partial-exemption scope | Cornell LII §1003.3(d) | *"**Optional data**: Data identified in § 1003.4(a)(1)(i), (a)(9)(i), and **(a)(12), (15)–(30), and (32)–(38)**"* | 🔴 **HIGH-8 — outcome + every regressor exempt for sub-500 banks/CUs** |
| 8 | *(not claimed)* points are inside APR | Cornell LII 12 CFR §1026.4 | §1026.4(a): *"The finance charge is the cost of consumer credit as a dollar amount. It includes any charge payable directly or indirectly by the consumer and imposed directly or indirectly by the creditor as an incident to or a condition of the extension of credit."* §1026.4(b)(3): *"**Points, loan fees**, assumption fees, finder's fees, and similar charges."* | 🔴 **§7 controls for a component of its own DV (CRIT-1)** |
| 9 | *(not claimed)* `intro_rate_period` NA convention | CFPB chart, extracted | *"Enter "NA" for: **Covered loan or application with a fixed rate**, Comment 4(a)(26)-3"* | 🔴 **CRIT-4** |
| 10 | *(not claimed)* public DTI binning | FFIEC public LAR data fields | Bins: `<20%`, `20%-<30%`, `30%-<36%`, `36`–`49`, `50%-60%`, `>60%`, `NA`, `Exempt`. Property value: *"Rounded to the midpoint of the nearest $10,000 interval."* Income: *"gross annual income, in thousands of dollars."* | 🔴 **MED-8 — mixed-type column, §7 cites CFR for a public-file modification** |

**Sources not reached, stated explicitly:**
- **eCFR (`ecfr.gov`)** — 302-redirected to `unblock.federalregister.gov` (bot block). Not read. Regulatory text taken from Cornell LII + CFPB publications; the two agree wherever they overlap.
- **ScienceDirect final typeset article** (S0304405X21002403) — not attempted directly by me; the delegated fetch reported HTTP 403. **My published-version evidence is the May 4 2021 accepted manuscript** (`faculty.haas.berkeley.edu/stanton/pdf/discrim.pdf`) **plus the RePEc abstract for JFE 143(1).** The RePEc abstract differs in light wording from the May-2021 abstract, so revision occurred after May 2021. **Table 10/6 cell values should be treated as from the accepted manuscript, not certified against print.** What is certain regardless and sufficient for HIGH-1: **`7.88`, `6.95`, and the string `Panel A` appear nowhere in the accepted manuscript**, and its Table 4 is the FinTech vs non-FinTech table.
- **FIG PDF** — not fetched directly; the equivalent and more authoritative CFPB *Reportable HMDA Data* reference chart (2024 v1) was fetched and text-extracted, and is quoted throughout.

---

## Strongest single objection

**Reverse §7 from "include points/credits as controls" to "publish the with/without pair, and add costs-as-outcome."**

Not because bad-control theory says so. Because **the doc's own anchor ran the experiment on the doc's own data vintage and got the opposite sign from the one §7 asserts** — 7.377 → 7.820 when points are controlled (Table 10, 2018/19 HMDA, GSE purchase). §7 asserts attenuation; promises the §9 floor will catch it; and §9 says that floor **never runs at runtime**. Three load-bearing claims propping up the single most consequential new decision in the document: **one refuted by primary source, two mutually contradictory.**

And the transfer isn't even clean in §7's favor: because points are finance charges **inside** the APR (§1026.4(b)(3)), §7 is conditioning an APR-based outcome on a component of that outcome's construction — so the note-rate evidence doesn't license *any* confident sign. The honest position is **sign unknown**, which makes a single point estimate indefensible and the with/without pair mandatory.

This is not a tuning issue. It is the pillar under v0.3.0's headline change, and it is hollow.

---

## What survives adversarial pressure (stated for completeness, not as praise)

- **§6's cost-field split** — all four cells confirmed verbatim. The version's load-bearing fix is **correct**. Only its citation is wrong.
- **§3's rate_spread-over-note-rate argument** — the public-LAR-has-no-month-date reasoning is correct, well-sourced, and the best thinking in the document.
- **§6's `1111`-is-not-a-global-sentinel rule** — confirmed. Coded fields use `Code 1111—Exempt`; numeric fields use literal `Exempt`.
- **§10's no-winsorizing rule** — correct, and correctly reasoned (rewriting an observed value with a fabricated boundary is silent substitution; it attenuates toward a lender-favorable result).
- **§12's replacement of the R²/p gate with cluster-count + precision** — correct, and independently corroborated by Table 10's R² of 0.376 vs Table 3's 0.803 on the same estimand.
- **§9's "band is dev-time only, never a per-lender runtime gate"** — correct, and the reasoning (a national band wired per-lender would silence true positives on the worst actors) is sound. It just happens to void §7's defense.
- **§9's OVB wedge (↑)** — the one ledger wedge that verifies (9.03 raw → 7.88 with the GSE grid).
- **Firewall placement** — clean.
