# Public HMDA Data Limitations

**Scope:** This tool analyzes HMDA-reportable mortgage transactions only. See [`methodology.md`](methodology.md) for full scope and [`README.md`](../README.md) for excluded products (e.g., Section 1071 small business lending).

**This document is required reading before drawing conclusions from fair-lending-screener output.**

Public HMDA data is the foundation of this tool, and it is incomplete. The following information is absent from the public dataset and therefore absent from every analysis this tool produces. Each omission is a source of omitted-variable bias that may cause the adjusted odds ratio to be overstated or understated relative to a fully specified model.

---

## What Is Missing and Why It Matters

### 1. Credit Score
**What:** The applicant's credit score (FICO or equivalent).  
**Why missing:** Industry successfully lobbied for its exclusion during Dodd-Frank rulemaking. CFPB shares credit score with federal regulators under supervisory authority but not publicly (12 C.F.R. § 1003.4(a)(15) note).  
**Why it matters:** Credit score is the single most predictive variable in mortgage underwriting. Its omission means the model cannot fully separate creditworthiness from protected class status.  
**Bias direction:** If credit score gaps between groups reflect legitimate differences in credit history, omitting credit score overstates the racial disparity. If credit score gaps reflect structural discrimination in credit access, omitting it understates the true disparity. The direction is contested.

### 2. Automated Underwriting System (AUS) Recommendation
**What:** The Fannie Mae Desktop Underwriter (DU) or Freddie Mac Loan Prospector (LP) output — the primary tool lenders use for conventional underwriting.  
**Why missing:** Not required to be reported publicly in Regulation C.  
**Why it matters:** AUS recommendations drive the vast majority of conventional loan decisions. An AUS "Refer" or "Refer with Caution" may precede a denial regardless of the applicant's demographics.  
**Bias direction:** Omitting AUS produces upward bias in the racial disparity coefficient, because AUS correlates with both race (groups with lower average credit scores receive more "Refer" outputs) and denial (Refer outputs lead to higher denial rates). See Wooldridge (2019) §3.3.

### 3. Liquid Assets and Reserves
**What:** Checking/savings account balances, retirement assets, and cash reserves.  
**Why missing:** Not a required HMDA field.  
**Why it matters:** Reserves (typically 2–6 months of PITI) are a required or preferred element of many underwriting guidelines. Groups with lower average savings may face higher denial rates for this legitimate reason.

### 4. Co-Applicant Credit Profile
**What:** Co-applicant credit score, liabilities, and employment.  
**Why missing:** Regulation C collects co-applicant income and race but not credit profile.  
**Why it matters:** For two-applicant households, the co-applicant's creditworthiness materially affects underwriting. This is not controllable with public HMDA data.

### 5. Credit History and Tradeline Data
**What:** Derogatory marks, delinquency history, number of open accounts, bankruptcies, charge-offs.  
**Why missing:** Not required under HMDA.  
**Why it matters:** These are significant underwriting factors. Their absence means the regression cannot separate credit-history-driven denials from potentially disparate ones.

### 6. Appraisal Method and Results
**What:** Whether an appraisal was conducted, its method (full, desktop, waiver), and whether the value was below the purchase price.  
**Why missing:** Regulation C includes the lender-reported property value but not appraisal method or disputes.  
**Why it matters:** Appraisal gaps in majority-minority neighborhoods are a documented phenomenon. If properties in minority neighborhoods receive lower appraisals, this affects LTV and may produce denials unrelated to applicant creditworthiness.

### 7. Underwriter Override Data
**What:** Whether a human underwriter overrode an AUS recommendation (approve → deny or deny → approve).  
**Why missing:** Discretionary decisions are internal lender data and not captured in HMDA.  
**Why it matters:** Underwriter overrides are a documented vector for both intentional and unconscious bias. Even if AUS recommends approval, a human override to denial would appear in HMDA as a denial indistinguishable from an AUS-driven denial.

### 8. Conditional Approval vs. Clean Approval
**What:** Whether an approval included conditions (additional documentation requirements, rate adjustments, reduced loan amount).  
**Why missing:** HMDA codes both conditional and unconditional approvals that ultimately originate as `action_taken == 1`.  
**Why it matters:** Disparately applied conditions are a form of differential treatment not detectable with this tool.

### 9. Employment History and Type
**What:** Employment type (W-2, self-employed, gig/contractor), tenure at employer, and industry.  
**Why missing:** Not a required HMDA field.  
**Why it matters:** Employment stability and income documentation requirements vary by type. Self-employed applicants face more complex underwriting; groups with higher rates of self-employment or gig work may face higher denial rates for this legitimate reason.

### 10. Lender-Specific Underwriting Overlays
**What:** Each lender's credit overlays above GSE minimums (e.g., requiring a 680 minimum score vs. the GSE's 620).  
**Why missing:** Internal lender policy; not reported in HMDA.  
**Why it matters:** Overlays vary substantially across lenders. Comparing applicants across lenders implicitly compares them under different underwriting standards.

---

## What This Means for Results

> All results produced by fair-lending-screener should be treated as **lower bounds on the information needed** to determine whether discrimination occurred, and as **screening signals** that warrant further investigation with full loan-file data.

An adjusted odds ratio of 1.8× does not mean that 80% of the disparity in denial rates is attributable to race. It means that after controlling for the factors available in public HMDA data, the unexplained denial rate disparity is 1.8×. With access to credit scores, AUS recommendations, and full loan files — as federal examiners have — the odds ratio might be higher, lower, or not statistically significant.

The tool is honest about this. Every generated report includes the complete limitations list and the standard disclaimer:

> "This analysis identifies a statistically significant adjusted disparity in denial rates. It does not constitute a finding of discrimination under ECOA or the Fair Housing Act, and it does not establish that any protected class characteristic caused any lending outcome. Further review of application files, underwriting guidelines, and internal lender data would be required to assess whether discrimination occurred."

---

## Regulatory Context

Federal fair lending examiners (OCC, Federal Reserve, FDIC, NCUA, CFPB) have access to data that is not public:
- Credit scores (submitted to regulators under supervisory authority)
- Full loan files
- Internal underwriting guidelines and overlays
- Comparative file reviews (matched-pair analysis)
- AUS recommendation records

This tool replicates the public-data layer of fair lending examination. Full examination requires access to internal data that is not available to community advocates, journalists, or researchers using public HMDA.
