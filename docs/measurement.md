# Three different questions require three kinds of evidence

## 1. Is the data and segmentation reliable?

Audit full daily coverage, duplicate/unknown accounts, invalid amounts, account-age definitions and the treatment of zero history. Sample every state with operators. Compare transitions by period and business group; inspect unusual jumps. Stable low-value accounts must not be called unhealthy simply because they are small.

The implementation has deterministic generation and tests that alter future events without changing earlier features. These establish computation behavior, not business validity.

## 2. Does a flag identify a subsequent behavior?

The demo compares a spend-only baseline with lifecycle rules and threshold alternatives on the same population. Features in windows 9–11 precede outcomes in 10–12; currently inactive and incomplete-history observations are excluded. Outcome is next-window zero spend. Report eligible observations, distinct accounts, base rate, flags, true/false positives, precision and recall. Empty denominators are N/A.

The dataset is synthetic and includes a deliberately generated warning-before-stop mechanism. The split illustrates temporal evaluation; it does not provide independently validated real-world performance. No threshold is fitted to the held-out slice. Comparing variants there does not create a new holdout for a chosen winner. Repeated account-windows are correlated; no independent-binomial significance claim is made. Real deployment needs an untouched future period, realistic operating constraints, label/cost review and uncertainty estimation that respects account/cluster dependence.

First-spend continuation is a separate descriptive diagnostic: positive spend on days 30–59 after first spend, with all 60 days observed. Exclude censored accounts from its denominator. Compare channel/category mix before attributing changes to the onboarding experience.

## 3. Does the proposed action create incremental value?

Freeze eligibility and stage before assignment. Randomize eligible accounts within stage and key strata into intervention and holdout. Where account managers create spillovers, consider cluster assignment and cluster-aware analysis. Predefine outcome window, detectable effect, sample size, stopping rule, assignment unit and cost logging.

Primary outcome: contribution profit per randomized eligible account, or an explicitly defined revenue metric if costs are unavailable. Include incentives and service costs. Guardrails: advertiser efficiency, complaints, unsubscribes and account health. Analyze original assignment (intention to treat), including accounts not reached. Report uncertainty and allocation/exposure counts. Do not stop opportunistically on significance.

A stage improvement, reduced alert volume, historical spend coverage or before/after revenue increase is not incremental return. The original project's approximately 3% post-adoption increase, described in personal retrospective notes, is not reproduced or causally attributed by this repository.
