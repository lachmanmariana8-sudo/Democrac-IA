# Chapter 9 — Predictive analysis

**Objective:** project probabilistic scenarios for the next 2-6 weeks. A distinctive chapter of the Elite Report.

**IMPORTANT — Chapter scope:**
- It is NOT political forecast (who wins). Pollsters do that.
- It IS estimation of institutional dynamics: disputes, nullity, runoff, crisis, legislative reform.
- Probabilities are NOT mutually exclusive.

**Expected structure (## subsections):**

## 9.1 Predictive-analysis methodology

- Hybrid pipeline: deterministic rules over Hunter patterns + qualitative analysis with Claude
- Evidence sources used: aggregated signals, historical trajectory (datasets), normative framework (legal thresholds)
- Acknowledged limitations: short horizon, does not predict partisan political behaviour

## 9.2 Identified dominant pattern

- Describe the `dominant_pattern` provided in the forecast context
- Ground it with 2-3 concrete signals from the evidence (figures + sources)

## 9.3 Probabilistic scenarios

For each of the 3-5 scenarios from the `ForecastPayload`:

- **Name and probability** (with confidence interval if available)
- **Indicators supporting it** (cite specific findings)
- **Applicable normative framework** (article/resolution)
- **Implications** if it occurs
- **Watch signals** — what to monitor to confirm/disconfirm

Suggested format for each scenario:

```
### Scenario A: {label}

**Estimated probability:** {prob}% (95% CI: {low}–{high}%)
**Normative basis:** {legal_basis}

**Indicators:**
- {indicator_1}
- {indicator_2}
- {indicator_3}

**Implications:** {implications}

**Signals to monitor:**
- {watch_1}
- {watch_2}
```

## 9.4 Early-warning level

- Current level (green/amber/orange/red) with justification
- Criteria that would shift the level in the next 2 weeks
- Recommended update period for the report

**Requirements:**

- Length: **800-1000 words**.
- Use EXACTLY the scenarios provided in the `forecast_formatted` context. Do not invent new scenarios.
- Each scenario must have an exact numeric probability.
- Do NOT make value judgements on which scenario is "good" or "bad". Only describe objective implications.
- Subsection 9.4 must close with an **operational sentence**: if `early_warning=orange`, for example: "An update to this report within no more than 7 days is recommended given the ongoing dynamics".

**Tone:** analytical-prospective. Cautious. Institutional risk-analysis language.

Now write **Chapter 9 — Predictive analysis** in markdown. Start with `## 9.1`.
