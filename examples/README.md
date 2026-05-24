# Examples

## demo_fair_lending_screener.ipynb

A narrative walkthrough of `fair-lending-screener` v0.2.0 for community advocates, investigative journalists, and CDFI practitioners. The notebook fetches 2023 HMDA data for Illinois from the CFPB public API, runs an adjusted denial disparity analysis (binary logistic regression with FFIEC-standard controls), and generates a Markdown report explaining the adjusted odds ratio, confidence interval, and what the result does and does not prove. It also shows the non-significant disclaimer variant, demonstrates how to access the bundled methodology documentation, and closes with a limitations section covering the key data gaps in public HMDA (credit score, AUS recommendations, asset data).

**To run:**

```bash
pip install fair-lending-screener
pip install jupyter
jupyter notebook examples/demo_fair_lending_screener.ipynb
```

The data-fetch cells require internet access to the CFPB HMDA Data Browser API and may take 1–2 minutes. All other cells run locally with no network access required.
