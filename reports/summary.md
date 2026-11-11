# Synthetic merchant lifecycle diagnostic

**Fictional data. No measured intervention effect or historical revenue replication.**

Latest snapshot: 2025-09-27; 240 accounts. Fixed 30-day windows, not calendar months.

| Stage | Accounts | Share |
|---|---:|---:|
| Onboarding | 0 | 0.0% |
| Growth | 67 | 27.9% |
| Mature | 58 | 24.2% |
| At-risk | 19 | 7.9% |
| Observe | 96 | 40.0% |

## Adjacent-window transitions

Counts pooled over all adjacent snapshots: one account can contribute multiple transitions. New accounts do not enter a transition until a previous snapshot exists. The demo has no account deletions. Row percentages are descriptive, not churn probabilities.

| From / To | Onboarding | Growth | Mature | At-risk | Observe |
|---|---:|---:|---:|---:|---:|
| Onboarding | 0.0% | 0.7% | 1.4% | 0.0% | 97.8% |
| Growth | 0.0% | 23.1% | 48.4% | 6.4% | 22.1% |
| Mature | 0.0% | 39.6% | 44.1% | 8.0% | 8.2% |
| At-risk | 0.0% | 1.1% | 0.0% | 11.5% | 87.4% |
| Observe | 0.0% | 20.3% | 20.0% | 7.4% | 52.4% |

## Operational interpretation

At-risk accounts need diagnosis before discounts; growth accounts need efficiency review before budget expansion. Observe is an intentional review bucket, not a low-value judgment. The queue uses illustrative stage-first and value-second ordering, not predicted incremental return. Apply team capacity, account ownership and outreach policies before activation.

See `action_queue.csv` for account-level reasons and suggested actions. Changes in stage are not evidence that an intervention worked.
