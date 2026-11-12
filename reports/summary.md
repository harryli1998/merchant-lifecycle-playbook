# First spend is not sustained adoption

**Synthetic case study — fabricated merchant behavior, not measured client impact.**

## Decision and evidence

The operating question: which first-time advertisers need help continuing to spend, and who should a small operations team contact first?

For fully observed first-spend cohorts C01–C05, 113/150 (75.3%) spent again on days 30–59 after first spend. For C06–C10, the figure is 70/150 (46.7%). First spend is day 0. This is next-window continuation, not continuous activity or causal retention uplift.

The generator deliberately shifts later acquisition toward a lower-continuation channel while established-account spend grows. Channel and category filters expose the composition. This is a constructed explanation, not a discovered real-world causal driver. Without campaign-efficiency, acquisition-cost or service records, do not infer poor ROI or onboarding failure.

## Check alternative explanations

- Censoring: compare fully observed cohorts; display the eligible denominator and exclude accounts without all 60 days of follow-up.
- Mix: compare within channel and category before attributing an overall decline to onboarding.
- Value versus lifecycle: Stable no longer requires high spend. Value tier is a separate category-relative feature.
- Seasonality, campaign completion and advertiser efficiency: not measured by this input; these remain questions for operators.

## Evidence about the risk rule

Outcome: zero spend in the next fixed 30-day window. Eligible observations have positive current and prior spend and complete windows. Feature windows 9–11 are evaluated against windows 10–12. The latest window is excluded. Repeated account-windows are correlated; no independence-based significance claim is made.

| Rule | Flagged | True / false positives | Precision | Recall |
|---|---:|---:|---:|---:|
| Spend-only baseline | 91 | 22 / 69 | 24.2% | 88.0% |
| Lifecycle rule | 31 | 20 / 11 | 64.5% | 80.0% |
| Looser decline | 31 | 20 / 11 | 64.5% | 80.0% |
| Stricter decline | 31 | 20 / 11 | 64.5% | 80.0% |
| Wider activity band | 75 | 22 / 53 | 29.3% | 88.0% |

Threshold alternatives are sensitivity checks on the same held-out slice, not separately validated winners. The synthetic generator contains pre-stop warning behavior, so apparent discrimination cannot establish performance on customer data. A simpler baseline can outperform the lifecycle rule; retain that result rather than tuning the demo to win.

## Action under a capacity constraint

There are 29 candidates at 2025-12-26. A 20-account weekly capacity selects the first 20 (or all if fewer). Activation candidates come first, then retention-risk accounts; within each motion sort by max(current, prior) spend. This is a transparent policy, not an estimate of treatment benefit.

Activation eligibility: observed first spend 14–59 days ago, account age at most 65 days, no spend for at least 7 days. Retention eligibility: currently positive-spend At-risk accounts. Reasons and suggestions are hypotheses to investigate, not known causes. Existing CRM ownership, campaign schedules and consent/contact history must be checked before outreach.

The capacity tool reports selected count and reference spend coverage. Reference spend is historical spending, not revenue at risk or recoverable money. Unselected candidates remain visible; exporting the list does not send messages.

## What a client engagement would deliver

1. Agree account, activation, meaningful repeat behavior and revenue definitions.
2. Audit coverage, reconcile zero activity and missing data, and map the required fields.
3. Produce cohort diagnostics, a reviewed segmentation, and a capacity-aware list.
4. Validate reasons with operators and scope a randomized intervention pilot.
5. Measure profit/revenue per randomized eligible account, costs and guardrails; report uncertainty.

Contact: [lihanyuan1998@gmail.com](mailto:lihanyuan1998@gmail.com). Do not send raw customer data in an initial inquiry.
