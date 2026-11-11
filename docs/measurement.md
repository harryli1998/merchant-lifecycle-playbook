# From labels to evidence

## Label validation

Review coverage, Observe share, stage distributions by category, and adjacent-stage changes. Sample accounts from each stage and ask operators to review reasons without seeing a suggested action first. Compare risk labels with behavior in a subsequent held-out period. Report observation coverage and sample sizes. Stability is useful, but a diagonal transition matrix is not proof of validity.

For a six-month backtest, retain at least one preceding feature window and an additional future outcome window where needed. This demo provides nine 30-day periods; it reproduces the mechanics, not the original dataset or a validated predictive backtest. No future-outcome validation or threshold optimization is claimed.

## Intervention evaluation

Freeze eligibility and stage before assignment. Randomize eligible accounts within stage and important business strata into treatment and holdout; if one salesperson's behavior affects multiple accounts, consider cluster assignment and corresponding analysis. Define the assignment unit, outcome window, detectable effect, sample size, exposure logging and stopping rule before launch.

Primary outcome: contribution profit per randomized eligible account, or a clearly specified revenue measure where costs are unavailable. Include incentive and service costs. Guardrails: complaints, unsubscribes, advertiser efficiency and account health. Analyze by original assignment (intention to treat), including accounts that were not successfully reached. Report uncertainty and allocation counts, and avoid repeatedly stopping on significance.

A stage transition, revenue increase after launch or before/after comparison alone does not establish incremental impact. Do not publish simulated uplift as measured performance. The historical project notes describe an approximately 3% post-adoption revenue increase; this repository does not reproduce, independently verify or causally attribute that figure.
