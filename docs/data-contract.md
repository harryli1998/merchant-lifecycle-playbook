# Data contract and exact definitions (v2)

## Inputs

`accounts.csv`: unique `account_id`, `category`, `channel`, and ISO `joined` date. Supported demo categories: Grocery, Flowers, Services. Channel is an acquisition source, not a quality score. The synthetic incumbent group is called Established. Each account remains observable after joining.

`daily_value.csv`: exactly one row for every account-date from max(joined, coverage.start) through coverage.end, including explicit zero values. Fields: `account_id`, ISO `date`, and finite nonnegative `value`. Value is advertiser spend in one synthetic currency, not platform revenue, contribution profit or advertiser return. Activity means a positive-spend day. Negative values, unknown IDs, duplicate rows, rows outside coverage/account lifetime, missing days and unknown categories fail.

`coverage.json`: inclusive start/end dates representing a complete observation period. Do not use this contract if zero and missing cannot be distinguished. Explicit preprocessing is required for refunds, multi-currency accounts, time zones, late arrivals, account closures, consent and tracking outages. A join date later than the last full snapshot is legitimately absent from that snapshot.

`config.json`: illustrative windows and thresholds, not fitted estimates. `value_thresholds` are separate from lifecycle labels. Sparse grouping fallback and competitive-intensity segmentation are not implemented. Account age begins at creation, not first spend; first-spend cohort age is a separate clock.

## Historical snapshot

Fixed non-overlapping 30-day windows are anchored to coverage.start, inclusive of each ending date. Incomplete trailing windows are omitted. A prior value exists only when the entire preceding window is inside coverage and the account existed at its start. Partial current windows are allowed for new accounts and identified by tenure. No future event enters a snapshot feature.

First/last observed spend are computed through the snapshot date. For incumbents created before coverage, first *observed* spend is not necessarily their first-ever spend. They are excluded from first-spend cohorts; the action list's account-age condition prevents them from being treated as newly activated.

## Next-window continuation

For accounts created within coverage, day 0 is the first observed positive-spend date. Outcome: at least one positive-spend day during days 30–59 inclusive. Eligibility: observation coverage through day 59. First-spend cohorts are 30-day bins from coverage.start. Censored accounts remain in first-spender counts but not in the rate denominator; zero eligible accounts return null/N/A, not zero retention. An account that never spends is not in these cohorts, so this does **not** estimate signup-to-first-spend conversion. The generator makes every account spend once; that is a narrative assumption.

Compare C01–C05 and C06–C10, each with 150 fully observed first spenders in this seed. Never pool rows across both `All` and category/channel detail, or you will double-count accounts. The page selects exactly one category and one channel aggregation.

## Lifecycle and value

Rules are sequential: Onboarding (<30 days); Observe for missing comparable prior; Inactive for zero current spend; Observe for zero prior; At-risk (decline >50%, <5 active days); Growth (>10% growth, >10 active days); Stable (absolute change <20%); otherwise Observe. Strict inequalities are intentional. Stable has no value minimum. Higher/Lower value tier is current spend relative to the account category's threshold. Neither value nor state identifies intervention benefit.

## Action eligibility and capacity

Activation: first observed spend 14–59 days ago, account age ≤65 days, no spend for ≥7 days. Retention: positive-spend At-risk accounts, unless already eligible for Activation. Deduplicate accounts; sort Activation before Retention, then descending max(current, comparable prior) spend, then account ID. If prior is unavailable, reference spend is current only; it may understate new-account history. This is a policy to review, not an optimized ranking.

Capacity selects the first N after category/motion filtering. Reference-spend coverage divides selected reference spend by all filtered candidates' reference spend. A zero denominator is N/A. It is not expected recovery, causal revenue at risk or ROI. Ownership/status fields are placeholders for operator review. No outreach is sent.

## Validation and transitions

Risk evaluation uses feature windows 9–11 and outcomes in windows 10–12. Both current and comparable prior spend must be positive. Outcome: next window's total spend is zero. The same eligible account-windows are used for every rule. Repeated accounts are correlated. No new threshold is chosen by optimizing the evaluation slice. Sensitivity variants compare decline thresholds -30/-50/-70% and activity caps 5/10; the simple baseline ignores activity. Jaccard overlap compares each flagged set with the lifecycle rule, including window date in the key.

Transitions pool every pair of adjacent snapshots for the same account. New accounts enter only after a previous snapshot exists. The demo has no closures or outages. Row percentages and overall switch rate are descriptive, not proof of label quality or individual churn probabilities.
