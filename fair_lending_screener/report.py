"""
Markdown report generation from DisparityResult.

Reports are journalist-legible: clear English with numbers exposed.
Safety guardrails (addition A7) prevent lender-attributed headlines
when the analysis does not meet minimum quality standards.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

from .disparity import DisparityResult
from .methodology import (
    FFIEC_FAIR_LENDING_PROCEDURES,
    FFIEC_URL,
    MARKUP_METHODOLOGY_CITATION,
    STANDARD_DISCLAIMER,
    STANDARD_DISCLAIMER_NON_SIGNIFICANT,
    ALPHA_DISCLAIMER,
    WOOLDRIDGE_OVB_CITATION,
)


def generate_disparity_report(
    result: DisparityResult,
    lender_name: Optional[str] = None,
    geography: Optional[str] = None,
    year: Optional[int] = None,
    include_methodology: bool = True,
) -> str:
    """
    Generate a Markdown report from a DisparityResult.

    The report is journalist-legible: it explains what was found, what was
    controlled for, what cannot be concluded, and how to reproduce the analysis.

    Safety guardrails (see A7): lender_name is suppressed from the headline
    and interpretation sections when any of the following are true:
    - sample_size < 100 (unreliable — should have been caught by InsufficientDataError,
      but checked here as a belt-and-suspenders measure)
    - p_value > 0.05 (not statistically significant)
    - model failed convergence (detected via model_diagnostics)
    - pseudo-R² < 0.05 (model controls contribute essentially nothing)
    In these cases, numbers are still reported, but the report explicitly flags the issue.

    Args:
        result:              DisparityResult from adjusted_denial_disparity().
        lender_name:         Optional lender name for context. Subject to safety guardrails.
        geography:           Optional geography description (e.g., "Chicago MSA", "Illinois").
        year:                Optional data year.
        include_methodology: If True, append methodology and citation section.

    Returns:
        Markdown string.
    """
    guardrail_flags = _check_guardrails(result)
    safe_to_name_lender = len(guardrail_flags) == 0

    lines: list[str] = []

    # ── Title ─────────────────────────────────────────────────────────────────
    title_parts = ["Fair Lending Disparity Analysis"]
    if geography:
        title_parts.append(geography)
    if year:
        title_parts.append(str(year))
    lines.append(f"# {' — '.join(title_parts)}")
    lines.append("")
    lines.append(f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*")
    lines.append("")

    # ── Alpha disclaimer ──────────────────────────────────────────────────────
    lines.append(f"> **Alpha release notice:** {ALPHA_DISCLAIMER}")
    lines.append("")

    # ── Guardrail warning (if applicable) ─────────────────────────────────────
    if guardrail_flags:
        lines.append("## ⚠ Analysis Quality Flags")
        lines.append("")
        lines.append(
            "One or more quality thresholds were not met. The numbers below are reported "
            "for transparency, but **should not be used to draw conclusions about any specific "
            "lender** until these issues are resolved."
        )
        lines.append("")
        for flag in guardrail_flags:
            lines.append(f"- {flag}")
        lines.append("")

    # ── Headline result ───────────────────────────────────────────────────────
    lines.append("## Headline Finding")
    lines.append("")

    lender_phrase = ""
    if lender_name:
        if safe_to_name_lender:
            lender_phrase = f" at **{lender_name}**"
        else:
            lender_phrase = " *(lender name withheld — see quality flags above)*"

    if result.is_statistically_significant:
        headline = (
            f"After controlling for {len(result.controls_used)} legitimate underwriting "
            f"factors, **{result.protected_class} applicants faced "
            f"{result.adjusted_odds_ratio:.2f}× higher odds of denial** than "
            f"{result.comparison_class} applicants{lender_phrase}. "
            f"This disparity is statistically significant (p={result.p_value:.4f})."
        )
    else:
        headline = (
            f"After controlling for {len(result.controls_used)} legitimate underwriting "
            f"factors, the adjusted denial disparity between {result.protected_class} "
            f"and {result.comparison_class} applicants{lender_phrase} "
            f"(odds ratio: {result.adjusted_odds_ratio:.2f}×) was **not statistically "
            f"significant** (p={result.p_value:.4f})."
        )
    lines.append(headline)
    lines.append("")
    _disclaimer = STANDARD_DISCLAIMER if result.is_statistically_significant else STANDARD_DISCLAIMER_NON_SIGNIFICANT
    lines.append(f"> {_disclaimer}")
    lines.append("")

    # ── Key numbers ───────────────────────────────────────────────────────────
    lines.append("## Key Numbers")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Unadjusted odds ratio | {result.unadjusted_odds_ratio:.4f}× |")
    lines.append(f"| **Adjusted odds ratio** | **{result.adjusted_odds_ratio:.4f}×** |")
    lines.append(f"| 95% Confidence interval | {result.confidence_interval_95[0]:.4f}× – {result.confidence_interval_95[1]:.4f}× |")
    lines.append(f"| P-value | {result.p_value:.6f} |")
    lines.append(f"| Statistically significant? | {'Yes (p < 0.05, CI excludes 1.0)' if result.is_statistically_significant else 'No'} |")
    lines.append(f"| Total applications analyzed | {result.sample_size:,} |")
    lines.append(f"| {result.protected_class} applicants | {result.sample_size_protected:,} |")
    lines.append(f"| {result.comparison_class} applicants | {result.sample_size_comparison:,} |")
    lines.append(f"| McFadden pseudo-R² | {result.model_diagnostics.get('pseudo_r2_mcfadden', 'N/A'):.4f} |")
    lines.append(f"| Model converged | {'Yes' if result.model_diagnostics.get('converged', True) else 'No'} |")
    lines.append("")

    # ── What "adjusted" means ─────────────────────────────────────────────────
    lines.append("## What 'Adjusted' Means")
    lines.append("")
    lines.append(
        "The **unadjusted** odds ratio compares raw denial rates between groups, "
        "without accounting for any differences in income, loan size, or other factors. "
        "The **adjusted** odds ratio accounts for the legitimate underwriting factors "
        "listed below — it asks: among applicants who look similar on paper "
        "(same income bracket, similar loan-to-value ratio, same MSA), "
        "do denial rates still differ by race?"
    )
    lines.append("")
    lines.append(
        "The difference between the unadjusted and adjusted figures shows how much "
        f"of the raw disparity ({result.unadjusted_odds_ratio:.2f}×) is explained "
        f"by the available controls. The remaining adjusted disparity ({result.adjusted_odds_ratio:.2f}×) "
        "persists after accounting for those factors."
    )
    lines.append("")

    # ── Controls used ─────────────────────────────────────────────────────────
    lines.append("## Controls Used in the Adjusted Model")
    lines.append("")
    lines.append(
        "The following legitimate underwriting factors were included as controls "
        "in the logistic regression model (FFIEC Interagency Fair Lending "
        "Examination Procedures, 2009):"
    )
    lines.append("")
    for ctrl in result.controls_used:
        lines.append(f"- `{ctrl}`")
    lines.append("")

    n_msa = result.model_diagnostics.get("n_msa_dummies", 0)
    if n_msa > 0:
        lines.append(
            f"**MSA fixed effects:** {n_msa} MSA indicator variables were included "
            f"to control for local market conditions (home prices, lender composition, "
            f"economic environment). MSAs with fewer than 30 observations were grouped "
            f"into a reference category."
        )
        lines.append("")

    if result.dropped_controls:
        lines.append(
            f"**Controls dropped (zero variance in this sample):** "
            f"{', '.join(f'`{c}`' for c in result.dropped_controls)}. "
            f"These columns were constant in the analysis sample — they contribute "
            f"nothing to model fit and would cause a singular Hessian. "
            f"Common cause: `dti_missing` when all applicants reported DTI, or "
            f"an MSA dummy covering a single outcome category."
        )
        lines.append("")

    # ── Limitations ───────────────────────────────────────────────────────────
    lines.append("## Limitations of This Analysis")
    lines.append("")
    lines.append(
        "**Public HMDA data does not include several factors that affect lending decisions.** "
        "This analysis controls for what is available, but cannot control for what is absent. "
        "Each omission is a source of omitted-variable bias."
    )
    lines.append("")
    for lim in result.limitations:
        if lim != STANDARD_DISCLAIMER:
            lines.append(f"- {lim}")
    lines.append("")

    # ── What this does NOT prove ───────────────────────────────────────────────
    lines.append("## What This Analysis Does NOT Prove")
    lines.append("")
    lines.append(
        "This analysis is a **statistical screening tool**, not a legal finding. Specifically:"
    )
    lines.append("")
    lines.append("- It does **not** prove that the lender intentionally discriminated.")
    lines.append("- It does **not** establish a causal link between race and denial.")
    lines.append("- It does **not** account for credit score, AUS recommendations, or asset data.")
    lines.append("- It does **not** constitute a finding of a violation of ECOA or the Fair Housing Act.")
    lines.append("- It does **not** mean any specific applicant was treated unlawfully.")
    lines.append(
        "- It **does** identify a statistical pattern that warrants further review "
        "with full loan-file data, internal underwriting guidelines, and examiner access."
    )
    lines.append("")
    lines.append(f"> {_disclaimer}")
    lines.append("")

    # ── Methodology section ───────────────────────────────────────────────────
    if include_methodology:
        lines.append("## Methodology")
        lines.append("")
        lines.append(
            "**Statistical method:** Binary logistic regression (statsmodels.api.Logit). "
            "The outcome variable is denial (1) vs. origination (0) per FFIEC exam procedures. "
            "The coefficient on the protected class indicator is exponentiated to produce "
            "the adjusted odds ratio."
        )
        lines.append("")
        lines.append("**Regulatory basis:**")
        lines.append(f"- {FFIEC_FAIR_LENDING_PROCEDURES} ({FFIEC_URL})")
        lines.append(f"- {MARKUP_METHODOLOGY_CITATION}")
        lines.append("")
        lines.append(
            "**Known upward bias from omitted controls:** "
            f"{WOOLDRIDGE_OVB_CITATION} "
            "AUS recommendations and credit scores — the primary omitted variables — "
            "are correlated with both race and denial, producing upward bias in the "
            "racial disparity coefficient. Results should be interpreted as an upper "
            "bound on the unexplained disparity."
        )
        lines.append("")
        lines.append(
            "**Full methodology documentation:** `docs/methodology.md` in the package repository."
        )
        lines.append("")

    # ── Reproducibility / Provenance ──────────────────────────────────────────
    lines.append("## Reproducibility")
    lines.append("")
    lines.append(
        "The following provenance block contains all information needed to reproduce "
        "this analysis. Copy it verbatim if citing this result."
    )
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(result.provenance, indent=2, default=str))
    lines.append("```")
    lines.append("")

    # ── Methodology feedback ──────────────────────────────────────────────────
    lines.append(
        "*Methodology concerns? Open a GitHub issue tagged `methodology` at "
        "https://github.com/Jaypatel1511/fair-lending-screener/issues with specific "
        "concerns and citations. All methodology changes are versioned in CHANGELOG.md.*"
    )
    lines.append("")

    return "\n".join(lines)


def _check_guardrails(result: DisparityResult) -> list[str]:
    """
    Check A7 safety guardrails. Returns list of flag strings (empty = all clear).

    Lender name is suppressed from headlines when any flag is raised.
    """
    flags = []

    if result.sample_size < 100:
        flags.append(
            f"Sample size ({result.sample_size:,}) is below the 100-observation minimum. "
            "Results are statistically unreliable."
        )

    if result.p_value > 0.05:
        flags.append(
            f"Not statistically significant (p={result.p_value:.4f} > 0.05). "
            "The disparity is within the range expected by chance."
        )

    if not result.model_diagnostics.get("converged", True):
        flags.append(
            "Logistic regression did not converge. Coefficient estimates are unreliable. "
            "Check for perfect separation or near-collinear predictors."
        )

    pseudo_r2 = result.model_diagnostics.get("pseudo_r2_mcfadden", 1.0)
    if pseudo_r2 < 0.05:
        flags.append(
            f"Model pseudo-R² ({pseudo_r2:.4f}) is below 0.05 — the controls explain "
            "very little of the variance in denial decisions. The model may be underspecified."
        )

    return flags
