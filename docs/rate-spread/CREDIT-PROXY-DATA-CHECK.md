# Credit-Proxy Data Availability — the CRIT-2 gate, answered

**Question:** does any public/free dataset provide a census-tract-level credit-score (or credit-risk) measure that could serve as the credit control the rate-channel tool omits — closing CRIT-2 and making pricing revivable?

**Answer: No. The feature is conclusively data-blocked** — not "unbuilt," but blocked by contractual vendor restriction on the only source that has the right shape, and by geography/metric mismatch on the only downloadable source. Verified July 14 2026.

## What exists, and why none of it works as a control

| Source | Geography | Metric | By race? | Downloadable? | Verdict |
|---|---|---|---|---|---|
| **Philadelphia Fed Consumer Credit Explorer** | **census tract** | Equifax Risk Score (280–850) | **yes** (neighborhood majority race/ethnicity) | **NO** — "Due to data vendor restrictions, the Philadelphia Fed is not able to provide any series… in spreadsheet format." Contractual Equifax lock; view-only in the tool | Right shape, **unusable** — cannot be merged into a model |
| **NY Fed Credit Insecurity Index** | state / county / city | credit-*insecurity* index (share credit-constrained / no file) | no | **yes** (Excel, 2018–2023) | Wrong geography (no tract), wrong metric (not a credit score), not by race |
| NY Fed CCP/Equifax (the underlying panel) | tract-derivable | Equifax Risk Score | — | proprietary (data-use agreement only) | This is the same Equifax source Bartlett used via McDash-Equifax — **not public** |
| Public HMDA itself | tract | — | — | yes | **Credit score is masked** in public HMDA by design ("cannot control for applicant credit scores") |

## Two independent walls
1. **The only tract-level, by-race credit data (Phil Fed Explorer) is contractually non-downloadable.** The block is an Equifax vendor agreement, not a technical gap — it will not resolve by looking harder. An open-source package that ingests public data cannot depend on a view-only tool.
2. **The only downloadable credit geography (NY Fed CII) is county-level, an insecurity index, and not by race** — wrong on all three axes for a tract-matched, credit-score control in a HMDA model.

## Even the best case wouldn't fix CRIT-2
If a tract-level average credit score *were* obtainable, it is an **ecological proxy** — it controls for tract-average credit risk, not individual. The OVB that CRIT-2 identifies is driven by *individual* credit differences within tract (the LLPA pass-through is priced off the individual's score). Bartlett could lean on tract proxies only because his identification came from the GSE credit×LTV grid plus lender/tract fixed effects — not from the proxy alone. In the tool's pooled public-HMDA model with no grid, a tract average would weakly reduce OVB while introducing ecological-inference bias. So the proxy route is not just unavailable — it is insufficient in principle.

## Consequence
The rate-channel pricing feature stays deferred, and this is the definitive reason: **the data required to control for the single largest legitimate rate driver does not exist in usable public form.** Revisiting pricing would require one of:
- CFPB/FFIEC releasing tract-level credit data (unlikely given the same vendor restrictions), or
- Jay obtaining a CCP/Equifax data-use agreement — which makes it a **non-public-data tool**, changing the package's entire premise and its "for community advocates" positioning, or
- a re-scope that needs no credit control — which the five audits showed makes the output uninterpretable.

None is a drafting task. The methodology thread is closed; do not open a v6.

**Sources:** [Philadelphia Fed Consumer Credit Explorer — Data Sources](https://www.philadelphiafed.org/surveys-and-data/community-development-data/consumer-credit-explorer-data-sources) · [NY Fed Credit Insecurity Index / Community Credit](https://www.newyorkfed.org/outreach-and-education/household-financial-stability/credit-insecurity-united-states) · [Fed Communities — Credit Insecurity Index](https://fedcommunities.org/data-tools/credit-insecurity-index/) · [CFPB — public HMDA masks credit score (proxy report)](https://www.consumerfinance.gov/data-research/research-reports/using-publicly-available-information-to-proxy-for-unidentified-race-and-ethnicity/)
