"""Reproducible synthetic diagnostic. Standard library only; no client data."""
import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGES = ['Onboarding', 'Growth', 'Stable', 'At-risk', 'Inactive', 'Observe']
ACTIONS = {
 'Activation': 'Review first-campaign setup, reporting comprehension and early results; agree the next campaign milestone.',
 'Retention': 'Review performance, seasonality, campaign completion and service history before recommending an incentive.',
}

def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

def read_csv(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')

def classify(tenure, value, previous, active, config):
    if tenure < config['onboarding_days']:
        return 'Onboarding', 'First account-age window is incomplete.'
    if previous is None:
        return 'Observe', 'Comparable prior window unavailable.'
    if value == 0:
        return 'Inactive', 'No spend in this window; not a prediction of future churn.'
    if previous == 0:
        return 'Observe', 'First observed activation or reactivation; growth rate undefined.'
    change = value/previous-1
    if change < config['risk_decline'] and active < config['risk_active_days']:
        return 'At-risk', f"Spend dropped more than {abs(config['risk_decline']):.0%} with fewer than {config['risk_active_days']} positive-spend days."
    if change > config['growth_rate'] and active > config['growth_active_days']:
        return 'Growth', 'Spend and activity meet the growth rule.'
    if abs(change) < config['stable_rate']:
        return 'Stable', 'Spend is within the stability band, regardless of account value.'
    return 'Observe', 'No operational rule matched; inspect the account history.'

def generate(root=ROOT):
    """Designed narrative: acquisition mix worsens; established accounts mask it.

    Latent repeat/warning states exist only here, never in the input features.
    Category and acquisition-channel associations are fabricated, not empirical.
    """
    rng = random.Random(42)
    start = date(2025,1,1); end = start+timedelta(days=359)
    accounts=[]; ledger=[]
    for i in range(480):
        incumbent = i < 120
        cohort = -1 if incumbent else (i-120)//30
        joined = start-timedelta(days=rng.randint(90,300)) if incumbent else start+timedelta(days=cohort*30+rng.randint(0,9))
        channel = 'Established' if incumbent else ('Paid acquisition' if rng.random() < (.22 if cohort < 5 else .72) else 'Partner referral')
        category=['Grocery','Flowers','Services'][i%3]
        base={'Grocery':22,'Flowers':62,'Services':42}[category] * rng.uniform(.7,1.3)
        if incumbent: base *= 3.2
        # Every account makes a first spend, so the case studies continuation, not signup-to-first-spend.
        first = joined+timedelta(days=rng.randint(0,6))
        repeat = incumbent or rng.random() < (.84 if channel=='Partner referral' else .42)
        state='active'; modes={}; max_age=(end-first).days//30
        for age_window in range(max_age+1):
            if age_window==0: mode='launch'
            elif not repeat: mode='stopped'
            elif state=='warning': mode='stopped' if rng.random()<.7 else 'active'
            elif state=='stopped': mode='active' if rng.random()<.10 else 'stopped'
            else:
                roll=rng.random()
                mode='warning' if roll<.07 else ('pause' if roll<.18 else 'active')
            state=mode
            modes[age_window]=mode
        accounts.append(dict(account_id=f'ADV-{i+1:04}',category=category,channel=channel,joined=joined.isoformat()))
        for offset in range(360):
            day=start+timedelta(days=offset)
            if day<joined: continue
            spend=0
            if day>=first:
                age=(day-first).days; mode=modes[age//30]
                local=age%30
                probability={'launch':.48,'active':.58,'warning':.08,'stopped':0,'pause':.18}[mode]
                scale={'launch':1,'active':1,'warning':.28,'stopped':0,'pause':.22}[mode]
                # Established portfolio grows slowly while new-cohort continuity weakens.
                if rng.random()<probability or age==0:
                    spend=round(base*scale*(1+offset/360*.45 if incumbent else 1)*rng.uniform(.8,1.2),2)
            ledger.append(dict(account_id=f'ADV-{i+1:04}',date=day.isoformat(),value=spend))
    write_csv(root/'data/accounts.csv',accounts)
    write_csv(root/'data/daily_value.csv',ledger)
    dump(root/'data/coverage.json',dict(start=start.isoformat(),end=end.isoformat(),synthetic=True))

def load_data(root):
    c=json.loads((root/'config.json').read_text())
    coverage=json.loads((root/'data/coverage.json').read_text())
    start,end=map(date.fromisoformat,[coverage['start'],coverage['end']])
    if end<start or (end-start).days+1<c['window_days']: raise ValueError('Insufficient coverage')
    accounts=read_csv(root/'data/accounts.csv'); ids=[a['account_id'] for a in accounts]
    if len(ids)!=len(set(ids)) or not ids: raise ValueError('Empty or duplicate account IDs')
    account_map={a['account_id']:a for a in accounts}
    for a in accounts:
        a['joined']=date.fromisoformat(a['joined'])
        if a['category'] not in c['value_thresholds']: raise ValueError('Unknown category')
    ledger={}
    for row in read_csv(root/'data/daily_value.csv'):
        key=(row['account_id'],date.fromisoformat(row['date'])); v=float(row['value'])
        if key[0] not in account_map or key in ledger or not math.isfinite(v) or v<0: raise ValueError('Unknown account, duplicate observation or invalid value')
        if not start<=key[1]<=end or key[1]<account_map[key[0]]['joined']: raise ValueError('Observation outside coverage/account lifetime')
        ledger[key]=v
    for a in accounts:
        lo=max(start,a['joined'])
        for offset in range((end-lo).days+1):
            if (a['account_id'],lo+timedelta(days=offset)) not in ledger: raise ValueError('Missing daily observation')
    return c,coverage,start,end,accounts,ledger

def build_snapshots(c,start,end,accounts,ledger):
    result=[]; w=c['window_days']
    for offset in range(w-1,(end-start).days+1,w):
        as_of=start+timedelta(days=offset); lo=as_of-timedelta(days=w-1); prevlo=lo-timedelta(days=w)
        for a in accounts:
            if a['joined']>as_of: continue
            aid=a['account_id']
            vals=[ledger[aid,lo+timedelta(days=d)] for d in range(w) if lo+timedelta(days=d)>=a['joined']]
            prior=[ledger[aid,prevlo+timedelta(days=d)] for d in range(w)] if prevlo>=start and a['joined']<=prevlo else None
            v=round(sum(vals),2); p=round(sum(prior),2) if prior is not None else None
            active=sum(x>0 for x in vals); tenure=(as_of-a['joined']).days
            stage,reason=classify(tenure,v,p,active,c)
            # Scan only the account's observed past, never future events.
            days=[start+timedelta(days=d) for d in range(offset+1) if start+timedelta(days=d)>=a['joined']]
            positive=[day for day in days if ledger[aid,day]>0]
            first=positive[0] if positive else None; last=positive[-1] if positive else None
            tier='Higher' if v>=c['value_thresholds'][a['category']] else 'Lower'
            result.append(dict(account_id=aid,as_of=as_of.isoformat(),category=a['category'],channel=a['channel'],tenure_days=tenure,value=v,previous_value=p,change=round(v/p-1,4) if p else None,active_days=active,stage=stage,value_tier=tier,reason=reason,first_observed_spend=first.isoformat() if first else None,days_since_first=(as_of-first).days if first else None,days_since_last=(as_of-last).days if last else None))
    return result

def cohort_analysis(start,end,accounts,ledger,w):
    groups=defaultdict(list)
    for a in accounts:
        if a['joined']<start: continue # left-censored incumbent activation
        days=[a['joined']+timedelta(days=d) for d in range((end-a['joined']).days+1)]
        positives=[d for d in days if ledger[a['account_id'],d]>0]
        if not positives: continue
        first=positives[0]; cohort=(first-start).days//w
        eligible=first+timedelta(days=2*w-1)<=end
        repeated=eligible and any(ledger[a['account_id'],first+timedelta(days=d)]>0 for d in range(w,2*w))
        for category in ['All',a['category']]:
            for channel in ['All',a['channel']]:
                groups[cohort,category,channel].append((eligible,repeated))
    return [dict(cohort=f'C{k[0]+1:02}',cohort_index=k[0],category=k[1],channel=k[2],first_spenders=len(v),eligible=sum(x[0] for x in v),repeaters=sum(x[1] for x in v),rate=round(sum(x[1] for x in v)/sum(x[0] for x in v),4) if any(x[0] for x in v) else None,censored=sum(not x[0] for x in v)) for k,v in sorted(groups.items())]

def score_predictions(rows,predict):
    positives=sum(r['outcome'] for r in rows); flagged=[r for r in rows if predict(r)]
    tp=sum(r['outcome'] for r in flagged); fp=len(flagged)-tp
    return dict(observations=len(rows),unique_accounts=len({r['account_id'] for r in rows}),outcomes=positives,flagged=len(flagged),true_positive=tp,false_positive=fp,false_negative=positives-tp,precision=round(tp/len(flagged),4) if flagged else None,recall=round(tp/positives,4) if positives else None,base_rate=round(positives/len(rows),4) if rows else None)

def evaluation(snapshots,start,end,c):
    lookup={(s['account_id'],s['as_of']):s for s in snapshots}; rows=[]; w=c['window_days']
    # Preregistered demo split: the final three feature windows with observable next windows.
    for s in snapshots:
        idx=(date.fromisoformat(s['as_of'])-start).days//w
        if idx not in (8,9,10) or s['previous_value'] is None or s['previous_value']<=0 or s['value']<=0: continue
        nxt=lookup.get((s['account_id'],(date.fromisoformat(s['as_of'])+timedelta(days=w)).isoformat()))
        if nxt is not None: rows.append(dict(s,outcome=nxt['value']==0))
    strategies=[('Spend-only baseline',-.5,None),('Lifecycle rule',-.5,5),('Looser decline',-.3,5),('Stricter decline',-.7,5),('Wider activity band',-.5,10)]
    metrics=[]
    for name,decline,days in strategies:
        predict=lambda s: s['change']<decline and (days is None or s['active_days']<days)
        by_period=[]
        for period in sorted({r['as_of'] for r in rows}):
            part=[r for r in rows if r['as_of']==period]
            by_period.append(dict(as_of=period,**score_predictions(part,predict)))
        base={(r['account_id'],r['as_of']) for r in rows if r['change']<-.5 and r['active_days']<5}
        flags={(r['account_id'],r['as_of']) for r in rows if predict(r)}
        overlap=len(base & flags)/len(base | flags) if base | flags else 1
        metrics.append(dict(name=name,decline=decline,active_days=days,flag_overlap=round(overlap,4),**score_predictions(rows,predict),by_period=by_period))
    return metrics

def make_queue(latest,c):
    queue=[]
    for s in latest:
        age=s['days_since_first']; recency=s['days_since_last']
        # First spend known only for accounts created inside coverage. The tenure check excludes incumbents.
        activation=age is not None and 14<=age<=59 and s['tenure_days']<=65 and recency>=7
        if activation: motion='Activation'
        elif s['stage']=='At-risk' and s['value']>0: motion='Retention'
        else: continue
        reference=max(s['value'],s['previous_value'] or 0)
        queue.append(dict(s,motion=motion,reference_value=reference,suggested_action=ACTIONS[motion],owner='Unassigned',status='Not started'))
    # Activation-first is a deliberate operating policy for this specific case, not predicted ROI.
    queue.sort(key=lambda s:(0 if s['motion']=='Activation' else 1,-s['reference_value'],s['account_id']))
    for rank,s in enumerate(queue,1): s['rank']=rank
    return queue

def analyze(root=ROOT):
    c,coverage,start,end,accounts,ledger=load_data(root)
    snapshots=build_snapshots(c,start,end,accounts,ledger)
    cohorts=cohort_analysis(start,end,accounts,ledger,c['window_days'])
    validation=evaluation(snapshots,start,end,c)
    last_date=max(s['as_of'] for s in snapshots); latest=[s for s in snapshots if s['as_of']==last_date]
    queue=make_queue(latest,c)
    dates=sorted({s['as_of'] for s in snapshots}); trends=[]
    for d in dates:
        for category in ['All']+list(c['value_thresholds']):
            ss=[s for s in snapshots if s['as_of']==d and (category=='All' or s['category']==category)]
            value=sum(s['value'] for s in ss); incumbents=sum(s['value'] for s in ss if s['channel']=='Established')
            trends.append(dict(as_of=d,category=category,spend=round(value,2),accounts=len(ss),established_share=round(incumbents/value,4) if value else None,stages=dict(Counter(s['stage'] for s in ss))))
    transitions=Counter(); previous={}
    for s in snapshots:
        before=previous.get(s['account_id'])
        if before: transitions[before['stage'],s['stage']]+=1
        previous[s['account_id']]=s
    totals=Counter()
    for (a,b),n in transitions.items(): totals[a]+=n
    transition_rows=[dict(from_stage=a,to_stage=b,count=transitions[a,b],row_share=round(transitions[a,b]/totals[a],4) if totals[a] else None) for a in STAGES for b in STAGES]
    switches=sum(n for (a,b),n in transitions.items() if a!=b)
    stability=dict(adjacent_pairs=sum(transitions.values()),switches=switches,switch_rate=round(switches/sum(transitions.values()),4))
    histories=defaultdict(list)
    for s in snapshots: histories[s['account_id']].append({k:s[k] for k in ('as_of','value','stage','active_days')})
    dashboard=dict(meta=dict(synthetic=True,seed=42,version='2.0',start=start.isoformat(),end=end.isoformat(),as_of=last_date,accounts=len(accounts),window_days=c['window_days'],snapshots=len(snapshots)),config=c,stability=stability,trends=trends,cohorts=cohorts,validation=validation,latest=latest,queue=queue,histories=histories,transitions=transition_rows)
    write_csv(root/'reports/snapshots.csv',snapshots)
    write_csv(root/'reports/action_queue.csv',queue,fields=list(queue[0]) if queue else ['account_id','rank','motion'])
    write_csv(root/'reports/cohorts.csv',cohorts)
    write_csv(root/'reports/transitions.csv',transition_rows)
    write_csv(root/'reports/validation.csv',[{k:v for k,v in r.items() if k!='by_period'} for r in validation])
    dump(root/'demo/data.json',dashboard)
    write_case(root,dashboard)
    print(f"Generated {len(snapshots)} snapshots; {len(queue)} action candidates; {validation[0]['observations']} held-out account-windows")
    return dashboard

def pooled(cohorts,lo,hi,channel='All'):
    rows=[r for r in cohorts if lo<=r['cohort_index']<=hi and r['category']=='All' and r['channel']==channel]
    n=sum(r['eligible'] for r in rows); successes=sum(r['repeaters'] for r in rows)
    return successes,n,successes/n if n else None

def write_case(root,d):
    early=pooled(d['cohorts'],0,4); later=pooled(d['cohorts'],5,9)
    rate=lambda x: f'{x:.1%}' if x is not None else 'N/A'
    lines=['# First spend is not sustained adoption','', '**Synthetic case study — fabricated merchant behavior, not measured client impact.**','',
    '## Decision and evidence', '',
    'The operating question: which first-time advertisers need help continuing to spend, and who should a small operations team contact first?', '',
    f"For fully observed first-spend cohorts C01–C05, {early[0]}/{early[1]} ({rate(early[2])}) spent again on days 30–59 after first spend. For C06–C10, the figure is {later[0]}/{later[1]} ({rate(later[2])}). First spend is day 0. This is next-window continuation, not continuous activity or causal retention uplift.", '',
    'The generator deliberately shifts later acquisition toward a lower-continuation channel while established-account spend grows. Channel and category filters expose the composition. This is a constructed explanation, not a discovered real-world causal driver. Without campaign-efficiency, acquisition-cost or service records, do not infer poor ROI or onboarding failure.', '',
    '## Check alternative explanations', '',
    '- Censoring: compare fully observed cohorts; display the eligible denominator and exclude accounts without all 60 days of follow-up.',
    '- Mix: compare within channel and category before attributing an overall decline to onboarding.',
    '- Value versus lifecycle: Stable no longer requires high spend. Value tier is a separate category-relative feature.',
    '- Seasonality, campaign completion and advertiser efficiency: not measured by this input; these remain questions for operators.', '',
    '## Evidence about the risk rule', '',
    'Outcome: zero spend in the next fixed 30-day window. Eligible observations have positive current and prior spend and complete windows. Feature windows 9–11 are evaluated against windows 10–12. The latest window is excluded. Repeated account-windows are correlated; no independence-based significance claim is made.', '',
    '| Rule | Flagged | True / false positives | Precision | Recall |', '|---|---:|---:|---:|---:|']
    for v in d['validation']:
        lines.append(f"| {v['name']} | {v['flagged']} | {v['true_positive']} / {v['false_positive']} | {rate(v['precision'])} | {rate(v['recall'])} |")
    lines += ['', 'Threshold alternatives are sensitivity checks on the same held-out slice, not separately validated winners. The synthetic generator contains pre-stop warning behavior, so apparent discrimination cannot establish performance on customer data. A simpler baseline can outperform the lifecycle rule; retain that result rather than tuning the demo to win.', '',
    '## Action under a capacity constraint', '',f"There are {len(d['queue'])} candidates at {d['meta']['as_of']}. A 20-account weekly capacity selects the first 20 (or all if fewer). Activation candidates come first, then retention-risk accounts; within each motion sort by max(current, prior) spend. This is a transparent policy, not an estimate of treatment benefit.", '',
    'Activation eligibility: observed first spend 14–59 days ago, account age at most 65 days, no spend for at least 7 days. Retention eligibility: currently positive-spend At-risk accounts. Reasons and suggestions are hypotheses to investigate, not known causes. Existing CRM ownership, campaign schedules and consent/contact history must be checked before outreach.', '',
    'The capacity tool reports selected count and reference spend coverage. Reference spend is historical spending, not revenue at risk or recoverable money. Unselected candidates remain visible; exporting the list does not send messages.', '',
    '## What a client engagement would deliver', '',
    '1. Agree account, activation, meaningful repeat behavior and revenue definitions.',
    '2. Audit coverage, reconcile zero activity and missing data, and map the required fields.',
    '3. Produce cohort diagnostics, a reviewed segmentation, and a capacity-aware list.',
    '4. Validate reasons with operators and scope a randomized intervention pilot.',
    '5. Measure profit/revenue per randomized eligible account, costs and guardrails; report uncertainty.', '',
    'Contact: [lihanyuan1998@gmail.com](mailto:lihanyuan1998@gmail.com). Do not send raw customer data in an initial inquiry.']
    (root/'reports/summary.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--generate-demo',action='store_true'); args=parser.parse_args()
    if args.generate_demo: generate()
    analyze()
