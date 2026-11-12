# Merchant Lifecycle Playbook

**First spend is a start. What happens next?**

A reproducible diagnostic for advertising platforms and marketplaces: find weak advertiser continuation, challenge the segmentation rules, and build an account list that fits your team's capacity.

[Explore the interactive diagnostic](https://merchant-lifecycle-harry-li.shrewdnutmeg1.chatgpt.site) · [Read the case](reports/summary.md) · [Discuss a project](mailto:lihanyuan1998@gmail.com?subject=Merchant%20lifecycle%20diagnostic)

> **Synthetic demonstration, not a client result.** All 480 merchants and their behavior are fabricated. The generator intentionally changes acquisition mix and introduces pre-stop warning behavior. Results illustrate an evaluation workflow; they do not validate real-world predictive performance, causal impact or a revenue uplift.

## A three-minute walkthrough

1. **Diagnose.** In this constructed case, next-window spending falls from 75.3% (113/150) in first-spend cohorts C01–C05 to 46.7% (70/150) in C06–C10. Split by category and acquisition channel before blaming onboarding. Spend totals alone conceal changes in the new-advertiser journey.
2. **Challenge the rule.** On 667 held-out account-windows, the spend-only baseline raises 91 alerts, including 69 false alerts. The lifecycle rule raises 31, including 11 false alerts, but misses 5 subsequent zero-spend windows rather than 3. Both use the same eligible population. These are synthetic descriptive results, not evidence of production effectiveness.
3. **Make the decision operational.** Set a weekly capacity, inspect account histories and reasons, then export the selected review list. The latest snapshot has 29 candidates; a capacity of 20 leaves 9 waiting. The ordering is an explicit operating policy, not predicted treatment ROI.
4. **Measure the action separately.** A correct risk label does not prove that a call or incentive helps. The [measurement plan](docs/measurement.md) specifies what an intervention pilot must establish.

## Run it locally

Python 3.10+; no third-party Python dependencies or credentials.

```sh
python3 lifecycle.py --generate-demo
python3 -m unittest discover -s tests -v
python3 -m http.server 8000 --directory demo
```

Open `http://localhost:8000` to use the interactive page. Open it through HTTP, not by double-clicking the HTML: it loads a local JSON file.

`--generate-demo` overwrites the local inputs with the deterministic seed-42 dataset. `python3 lifecycle.py` analyzes existing inputs. Real client inputs and derived reports must stay in a private workspace: `data/` and full historical snapshots are ignored, but the public demo JSON and sample reports are tracked. Do not commit a client-data run to this public repository.

## What's included

| Artifact | Purpose |
|---|---|
| [lifecycle.py](lifecycle.py) | Generate synthetic inputs; validate coverage; derive historical features, cohorts, evaluation and actions |
| [config.json](config.json) | Explicit illustrative rules and category-relative value tiers |
| [demo/](demo/) | Buildless HTML/CSS/JS diagnostic with committed synthetic JSON |
| [reports/summary.md](reports/summary.md) | Decision-oriented case with definitions, alternatives and limitations |
| [reports/cohorts.csv](reports/cohorts.csv) | Eligible denominator, repeaters and censoring by cohort/category/channel |
| [reports/validation.csv](reports/validation.csv) | Baseline comparison and threshold sensitivity, including flag-set overlap |
| [reports/action_queue.csv](reports/action_queue.csv) | Latest eligible accounts with reasons, operating motion and transparent rank |
| [reports/transitions.csv](reports/transitions.csv) | Pooled adjacent-state counts and row shares |
| [tests/](tests/) | Rules, censoring, future-data leakage, determinism, data quality and queue policy |

Daily inputs and complete historical snapshots are generated locally. Current demo: 480 accounts, 360 days, 3 categories, 3,780 snapshots. Fixed 30-day windows are not calendar months.

## Explainable states, separate value

| State | Rule, in precedence order |
|---|---|
| Onboarding | Account age <30 days |
| Observe | Comparable full prior window unavailable |
| Inactive | Current spend is zero after history checks; not predicted churn |
| Observe | Prior spend is zero; growth rate is undefined |
| At-risk | Positive spend declined >50%, and <5 positive-spend days |
| Growth | Spend growth >10%, and >10 positive-spend days |
| Stable | Absolute spend change <20%, at any value level |
| Observe | No rule matched |

A separate Higher/Lower **value tier** compares current spend with the category threshold. It is not a health assessment. Unknown categories and missing daily observations fail explicitly. Historical features read only data available as of their snapshot.

Activation outreach is a distinct operating motion: observed first spend 14–59 days ago, account age ≤65 days, and no spend for ≥7 days. Retention outreach uses currently spending At-risk accounts. Activation comes first; within each motion, rank by max(current, comparable prior) spend. Missing comparable prior spend is omitted from that maximum. The page shows unselected candidates as well as selected accounts and exports only the selected list.

## What transfers—and what needs redesign

The reusable method is **decision → data contract → behavioral states → validation → capacity-aware action → incremental measurement**. The original advertiser lifecycle experience informs this loop; this public implementation is newly written with synthetic data.

For marketplace sellers, use meaningful order/fulfillment activity. For SaaS, consider adoption and renewal cadence. Recalibrate windows, operational states and value thresholds; advertising defaults are not universal. Review the [data contract](docs/data-contract.md), [Chinese methodology](docs/methodology.zh-CN.md), and [client scoping guide](docs/client-diagnostic.md).

## Work with Harry

I help advertising and marketplace teams turn merchant activity into explainable growth and retention decisions. A scoped engagement can deliver a data-readiness review, cohort diagnostic, reviewed segmentation, account action list, operator walkthrough and measurement plan.

**[Email lihanyuan1998@gmail.com](mailto:lihanyuan1998@gmail.com?subject=Merchant%20lifecycle%20diagnostic)** with your platform type, difficult operating decision and available data at a high level. No raw customer data is needed for an initial conversation. Scope and timing depend on readiness; no fixed revenue increase is promised. Use GitHub issues for technical questions.

## Limits and validation

This is not a production CRM, a trained churn model, or an automated outreach system. It does not measure advertiser efficiency, model seasonality, infer reasons for inactivity, estimate treatment response, or implement access controls. The latest period has no observed future outcome. Correlated account-windows are not treated as independent experiments. The generator's built-in patterns make synthetic evaluation easier than real-world deployment.

Seventeen Python tests cover rule boundaries, small stable accounts, missing/zero history, next-window boundaries, right censoring, future-event perturbation, queue ordering, missing/non-finite inputs and deterministic regeneration. Browser checks cover category/channel filters, rule comparison, zero/full capacity, account details, CSV export and a 390px mobile layout.

MIT license. The data generator and included synthetic outputs are under the same license.
