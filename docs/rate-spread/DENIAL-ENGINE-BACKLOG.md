# Denial-Engine Functional Backlog — the real "what's left to upgrade"

Now that pricing is closed (data-blocked) and the 0.2.2 accuracy correction is specced, this is the remaining work on the live denial engine. **Two separate releases:**
- **0.2.2 — accuracy correction** (docs/strings only; spec ready in `0.2.2-CORRECTION-SPEC.md`). Ship first; it fixes live false claims.
- **0.2.3 (or 0.3.0 if any fix changes behavior) — functional.** The tracked MED/LOW items below. Each verified against the code this session where noted; the rest are *hypotheses to confirm* (the knowledge files drift).

## Verified live this session (fix in the functional release)
- **MED-4 — reported `sample_size` overstates modeled n.** `disparity.py:198` `n_total = len(df)` (pre-regression) → `:340 sample_size = n_total`. The Logit fit drops NaN rows; the reported n doesn't. **Confirm** there's no `dropna` between :198 and the fit, then report the *post-drop modeled n* (or both raw and modeled). Most substantive item here — a wrong n undercuts every result's credibility. `[2-line code confirm]`
- **LOW-2 — MSA baseline docstring vs behavior mismatch.** `:426` says "most-common"; `:440–442` uses alphabetically-first (`sorted_msas[0]`). Either fix the docstring, OR (better, but a behavior change → minor bump) switch the code to the **most-common (largest) MSA** as baseline — a larger reference group is a more stable baseline. Decide which.

## Tracked, need code confirmation (from prior audits — treat as hypotheses)
- **LOW-3 — `baseline_msa` possibly dead code.** It's computed at `:442`; confirm whether it's actually used downstream or statsmodels drops the reference automatically (making it dead). If dead, remove.
- **LOW-NEW-3 — `InsufficientGroupSizeError` has zero tests.** Exception exists (`exceptions.py:81`), raised (`disparity.py:208`); grep `tests/` — if untested, add a raise-path test (positive + boundary).
- **MED-1 — methodology equation lists variables the code never creates.** Re-check the equation in `methodology.md`/`_methodology_doc.md` against the actual regressors built in `disparity.py`. (This is the same equation-vs-code drift class the pricing audits hammered — worth closing on the shipped doc too.)
- **MED-3 — "national" calibration test runs on Illinois-only data.** Check the calibration test fixture; if it validates a "national" 1.8× target on IL data, either broaden the data or rename the test to its true scope.
- **LOW-NEW-5 — guardrail p-value check vs `is_statistically_significant` boundary divergence.** Confirm the suppression guardrail and the significance flag use the same p threshold/boundary; a divergence at p≈0.05 could name a lender the significance flag would suppress.
- **LOW-1** CFPB API URL inconsistency (methodology.md vs code) · **LOW-4** FFIEC PDF URL 403 (the `FFIEC_URL` link — and note the 0.2.2 correction touches this citation anyway) · **LOW-5** McFadden pseudo-R² citation threshold · **LOW-6** `STANDARD_DISCLAIMER` duplication (grep all uses; the pricing thread's lesson — a constant paraphrased in >1 place drifts).

## Infra (separate, low priority)
- **data-health.yml two-tier redesign** — currently red on cloud-CI 403s (the pre-flight `check_data_source` from a datacenter IP). Standing answer: residential-authoritative + CI-files-an-issue. Parked.
- **Node 20→24 action-pin bump** (portfolio-wide, coordinate across the 6 CI'd packages).

## Recommended sequence
1. **Ship 0.2.2** (accuracy correction) — it's live-false-claim remediation; don't queue it behind functional work.
2. **Settle 0.2.2**, then a functional **0.2.3**: MED-4 (the real one) + LOW-2 + confirm/close LOW-3, LOW-NEW-3, MED-1, MED-3, LOW-NEW-5, and the LOW cluster. Any behavior change (e.g. baseline switch, n redefinition) → 0.3.0 and its own fresh hostile audit per house discipline.
3. Infra items whenever convenient.

## Method-soundness note (why this is polish, not crisis)
The denial engine's core is defensible: single-lender estimand (coefficient is that lender's, so naming is identified — unlike the pooled pricing design), credit-score omission *disclosed as an upper-bound* (not hidden), asymmetric calibration band accommodating the known upward bias, lender-name suppression when non-significant, and it's the established Markup/academic method. The five-round pricing saga's fatal problems (no credit control hidden, pooled coefficient naming lenders, fabricated provenance) do **not** transfer — the denial engine handles the same limitations honestly. This backlog is correctness polish on a sound tool.
