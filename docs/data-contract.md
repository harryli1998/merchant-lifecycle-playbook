# Data contract

`accounts.csv`: unique `account_id`, `category`, and ISO `joined` date. The onboarding clock starts at account creation in this demo; explicitly decide whether activation should use first spend instead for your business.

`daily_value.csv`: exactly one row per account and date from max(joined, coverage.start) through coverage.end, including explicit zero-value rows. Fields: `account_id`, ISO `date`, finite nonnegative `value`. Value means advertiser spend in one currency, not platform net revenue, profit, or advertiser ROI. Active days count positive-value dates.

`coverage.json`: inclusive dates with complete observed data. Missing rows fail rather than silently becoming inactivity. This demo assumes accounts remain observable after joining; production must model closures, pauses, data outages, timezone and late-arriving events explicitly. Refunds and multiple currencies require a preprocessing policy; negative values are rejected here.

`config.json`: illustrative category thresholds, not calibrated estimates. The original approach also considered competitive intensity; this demo implements category only. Extend grouping only when there is enough historical support, and define a fallback for sparse groups. Unknown categories fail explicitly.

Windows are consecutive, non-overlapping 30-day periods anchored to coverage.start. Each snapshot includes its ending date. A comparable prior window requires both full coverage and account existence at its beginning. Historical snapshots never read later events. Historical backtests need threshold versions fitted only on information available at the time; the demo uses a fixed illustrative config, not a fitted model.

For SaaS or retail, redefine the value and meaningful-activity signals and window lengths; do not reuse advertising thresholds unchanged. Keep lifecycle, customer value and predicted treatment benefit separate.
