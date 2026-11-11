"""Transparent lifecycle demo; Python standard library only."""
import csv
import json
import random
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGES = ["Onboarding", "Growth", "Mature", "At-risk", "Observe"]
ACTIONS = {
    "Onboarding": "Check first-campaign setup and activation blockers",
    "Growth": "Review efficiency before recommending additional budget",
    "Mature": "Review performance and suitable product expansion",
    "At-risk": "Diagnose performance, seasonality and service issues before incentives",
    "Observe": "Review account history; do not trigger automated incentives",
}

def classify(tenure, value, previous, active, threshold, c):
    # Explicit precedence is a demo design choice, not a recovered original rule.
    if tenure < c["onboarding_days"]:
        return "Onboarding", "Account has not completed its first lifecycle window"
    if previous is None:
        return "Observe", "Comparable prior window unavailable"
    if previous == 0:
        return "Observe", "Prior value is zero; review activation or reactivation"
    rate = value / previous - 1
    if rate < c["risk_decline"] and active < c["risk_active_days"]:
        return "At-risk", "Value and activity fell below risk rules"
    if rate > c["growth_rate"] and active > c["growth_active_days"]:
        return "Growth", "Value growth and activity exceed growth rules"
    if value >= threshold and abs(rate) < c["stable_rate"]:
        return "Mature", "Value exceeds category threshold and is stable"
    return "Observe", "No actionable rule matched; manual review required"

def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def generate():
    """Entirely fictional accounts and complete daily spend ledger, seed 42."""
    rng = random.Random(42)
    start = date(2025, 1, 1)
    end = start + timedelta(days=269)
    accounts, events = [], []
    for i in range(240):
        category = ["grocery", "flowers", "services"][i % 3]
        joined = start + timedelta(days=rng.randrange(-150, 210))
        accounts.append(dict(account_id=f"demo_{i:04}", category=category, joined=joined.isoformat()))
        base = {"grocery": 25, "flowers": 75, "services": 50}[category]
        for d in range(270):
            day = start + timedelta(days=d)
            if day < joined:
                continue
            period = d // 30
            kind = i % 5
            probability = .6
            scale = 1
            if kind == 0:
                scale = 1 + period * .22
            elif kind == 1 and period >= 6:
                probability, scale = .06, .25
            elif kind == 2 and period in (3, 4):
                probability = 0
            elif kind == 3:
                probability, scale = .2, .3
            spend = round(base * scale * rng.uniform(.75, 1.25), 2) if rng.random() < probability else 0
            events.append(dict(account_id=f"demo_{i:04}", date=day.isoformat(), value=spend))
    write_csv(ROOT / "data/accounts.csv", accounts)
    write_csv(ROOT / "data/daily_value.csv", events)
    (ROOT / "data/coverage.json").write_text(json.dumps(dict(start=start.isoformat(), end=end.isoformat(), synthetic=True), indent=2)+"\n")

def analyze():
    c = json.loads((ROOT / "config.json").read_text())
    coverage = json.loads((ROOT / "data/coverage.json").read_text())
    start, end = date.fromisoformat(coverage["start"]), date.fromisoformat(coverage["end"])
    accounts = list(csv.DictReader((ROOT / "data/accounts.csv").open()))
    ids = [a["account_id"] for a in accounts]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate account IDs")
    known = set(ids)
    ledger = {}
    for row in csv.DictReader((ROOT / "data/daily_value.csv").open()):
        key = row["account_id"], date.fromisoformat(row["date"])
        value = float(row["value"])
        import math
        if key[0] not in known or key in ledger or not math.isfinite(value) or value < 0:
            raise ValueError("Unknown account, duplicate daily row or invalid value")
        if not start <= key[1] <= end:
            raise ValueError("Daily row outside declared coverage")
        ledger[key] = value
    snapshots = []
    window = c["window_days"]
    for offset in range(window - 1, (end-start).days+1, window):
        as_of = start + timedelta(days=offset)
        current_start = as_of - timedelta(days=window-1)
        previous_start = current_start - timedelta(days=window)
        for a in accounts:
            joined = date.fromisoformat(a["joined"])
            if joined > as_of:
                continue
            category = a["category"]
            if category not in c["thresholds"]:
                raise ValueError("Category requires a calibrated threshold")
            def values(lo, hi):
                result = []
                for n in range((hi-lo).days+1):
                    day = lo + timedelta(days=n)
                    if day >= joined:
                        key = a["account_id"], day
                        if key not in ledger:
                            raise ValueError(f"Missing daily observation: {key}")
                        result.append(ledger[key])
                return result
            recent = values(current_start, as_of)
            prior = values(previous_start, current_start-timedelta(days=1)) if previous_start >= start and joined <= previous_start else None
            value = round(sum(recent), 2)
            previous = round(sum(prior), 2) if prior is not None else None
            active = sum(v > 0 for v in recent)
            stage, reason = classify((as_of-joined).days, value, previous, active, c["thresholds"][category], c)
            snapshots.append(dict(account_id=a["account_id"], as_of=as_of.isoformat(), category=category, tenure_days=(as_of-joined).days, value=value, previous_value=previous, active_days=active, stage=stage, reason=reason))
    write_csv(ROOT / "reports/snapshots.csv", snapshots)
    by_account = defaultdict(list)
    transitions = Counter()
    for s in snapshots:
        by_account[s["account_id"]].append(s)
    for history in by_account.values():
        for before, after in zip(history, history[1:]):
            if (date.fromisoformat(after["as_of"])-date.fromisoformat(before["as_of"])).days == window:
                transitions[before["stage"], after["stage"]] += 1
    totals = Counter()
    for (source, target), count in transitions.items():
        totals[source] += count
    rows = [dict(from_stage=s, to_stage=t, count=transitions[s,t], row_share=round(transitions[s,t]/totals[s], 4) if totals[s] else "") for s in STAGES for t in STAGES]
    write_csv(ROOT / "reports/transitions.csv", rows)
    latest = [s for s in snapshots if s["as_of"] == snapshots[-1]["as_of"]]
    priority = {"At-risk": 0, "Onboarding": 1, "Growth": 2, "Mature": 3, "Observe": 4}
    latest.sort(key=lambda s: (priority[s["stage"]], -s["value"]))
    actions = [dict(**s, suggested_action=ACTIONS[s["stage"]], owner="Unassigned", status="Not started") for s in latest]
    write_csv(ROOT / "reports/action_queue.csv", actions)
    counts = Counter(s["stage"] for s in latest)
    lines = ["# Synthetic merchant lifecycle diagnostic", "", "**Fictional data. No measured intervention effect or historical revenue replication.**", "", f"Latest snapshot: {latest[0]['as_of']}; {len(latest)} accounts. Fixed {window}-day windows, not calendar months.", "", "| Stage | Accounts | Share |", "|---|---:|---:|"]
    for s in STAGES:
        lines.append(f"| {s} | {counts[s]} | {counts[s]/len(latest):.1%} |")
    lines += ["", "## Adjacent-window transitions", "", "Counts pooled over all adjacent snapshots: one account can contribute multiple transitions. New accounts do not enter a transition until a previous snapshot exists. The demo has no account deletions. Row percentages are descriptive, not churn probabilities.", "", "| From / To | " + " | ".join(STAGES) + " |", "|---|" + "---:|"*len(STAGES)]
    for s in STAGES:
        lines.append("| " + s + " | " + " | ".join(f"{transitions[s,t]/totals[s]:.1%}" if totals[s] else "N/A" for t in STAGES) + " |")
    lines += ["", "## Operational interpretation", "", "At-risk accounts need diagnosis before discounts; growth accounts need efficiency review before budget expansion. Observe is an intentional review bucket, not a low-value judgment. The queue uses illustrative stage-first and value-second ordering, not predicted incremental return. Apply team capacity, account ownership and outreach policies before activation.", "", "See `action_queue.csv` for account-level reasons and suggested actions. Changes in stage are not evidence that an intervention worked."]
    (ROOT / "reports/summary.md").write_text("\n".join(lines)+"\n")
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="390" viewBox="0 0 900 390">', '<rect width="900" height="390" fill="#101c2d"/>', '<g font-family="Arial" fill="#edf4ff"><text x="32" y="45" font-size="26">Where should merchant operations focus?</text><text x="32" y="75" font-size="15">Synthetic demo · 240 accounts · descriptive lifecycle states</text>']
    for i,s in enumerate(STAGES):
        y=110+i*48
        svg += [f'<text x="32" y="{y+20}" font-size="17">{s}</text>', f'<rect x="165" y="{y}" width="{counts[s]*3}" height="28" rx="4" fill="#69d4b1"/>', f'<text x="{178+counts[s]*3}" y="{y+20}" font-size="16">{counts[s]}</text>']
    svg += ['<text x="32" y="374" font-size="13">Explain the state. Diagnose the cause. Assign an action. Measure incremental impact.</text></g></svg>']
    (ROOT / "reports/overview.svg").write_text("".join(svg))
    print(f"Generated {len(snapshots)} snapshots and {sum(transitions.values())} adjacent transitions")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-demo", action="store_true", help="Overwrite data with deterministic synthetic records")
    args = parser.parse_args()
    if args.generate_demo:
        generate()
    analyze()
