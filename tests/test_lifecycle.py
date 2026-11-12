import copy
import csv
import hashlib
import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from lifecycle import ROOT, classify, generate, analyze, load_data, build_snapshots, score_predictions, cohort_analysis

class Rules(unittest.TestCase):
    def setUp(self): self.c=json.loads((ROOT/'config.json').read_text())
    def stage(self, age=90, value=1000, previous=1000, active=20):
        return classify(age,value,previous,active,self.c)[0]
    def test_new_accounts_are_not_called_inactive(self):
        self.assertEqual(self.stage(age=10,value=0,previous=None,active=0),'Onboarding')
    def test_zero_baseline_is_not_infinite_growth(self):
        self.assertEqual(self.stage(previous=0),'Observe')
    def test_missing_history_is_not_risk(self):
        self.assertEqual(self.stage(value=0,previous=None,active=0),'Observe')
    def test_current_inactivity_is_not_a_prediction(self):
        self.assertEqual(self.stage(value=0,active=0),'Inactive')
    def test_risk_needs_both_signals(self):
        self.assertEqual(self.stage(value=100,active=2),'At-risk')
        self.assertEqual(self.stage(value=100,active=20),'Observe')
    def test_low_value_can_be_stable(self):
        self.assertEqual(self.stage(value=50,previous=50),'Stable')
    def test_growth_precedence(self): self.assertEqual(self.stage(value=1150),'Growth')
    def test_strict_thresholds(self):
        self.assertEqual(self.stage(value=500,active=2),'Observe')
        self.assertEqual(self.stage(value=100,active=5),'Observe')
    def test_undefined_metrics_are_null(self):
        m=score_predictions([],lambda r:True)
        self.assertIsNone(m['precision']);self.assertIsNone(m['recall'])

class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name)
        (cls.root/'config.json').write_text((ROOT/'config.json').read_text())
        generate(cls.root);cls.d=analyze(cls.root)
        cls.loaded=load_data(cls.root)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_no_future_features(self):
        c,cov,start,end,accounts,ledger=self.loaded
        cutoff=start+timedelta(days=239)
        changed={k:v*100 if k[1]>cutoff else v for k,v in ledger.items()}
        full=build_snapshots(c,start,end,accounts,ledger)
        perturbed=build_snapshots(c,start,end,accounts,changed)
        self.assertEqual([s for s in full if s['as_of']<=cutoff.isoformat()],[s for s in perturbed if s['as_of']<=cutoff.isoformat()])
    def test_censored_cohorts_excluded(self):
        last=[r for r in self.d['cohorts'] if r['cohort']=='C12' and r['category']=='All' and r['channel']=='All'][0]
        self.assertEqual(last['eligible'],0);self.assertIsNone(last['rate'])
        early=[r for r in self.d['cohorts'] if r['cohort']=='C01' and r['category']=='All' and r['channel']=='All'][0]
        self.assertEqual(early['eligible'],30)
    def test_repeat_boundary_days_30_to_59(self):
        c,_,start,_,_,_=self.loaded
        account=dict(account_id='test',joined=start,category='Grocery',channel='Partner referral')
        end=start+timedelta(days=59)
        ledger={('test',start+timedelta(days=d)):float(d in (0,29)) for d in range(60)}
        def row():return next(r for r in cohort_analysis(start,end,[account],ledger,30) if r['category']=='All' and r['channel']=='All')
        self.assertEqual(row()['repeaters'],0)
        ledger['test',start+timedelta(days=59)]=1
        self.assertEqual(row()['repeaters'],1)
    def test_validation_uses_same_population(self):
        metrics=self.d['validation']
        self.assertEqual(len({m['observations'] for m in metrics}),1)
        for m in metrics:
            self.assertEqual(m['true_positive']+m['false_negative'],m['outcomes'])
            self.assertEqual(m['true_positive']+m['false_positive'],m['flagged'])
            self.assertEqual(len(m['by_period']),3)
            self.assertNotIn(self.d['meta']['as_of'],[p['as_of'] for p in m['by_period']])
    def test_queue_policy_and_unique_accounts(self):
        q=self.d['queue'];keys=[(0 if s['motion']=='Activation' else 1,-s['reference_value'],s['account_id']) for s in q]
        self.assertEqual(keys,sorted(keys));self.assertEqual(len(q),len({s['account_id'] for s in q}))
        self.assertTrue(all(s['stage']=='At-risk' and s['value']>0 for s in q if s['motion']=='Retention'))
        self.assertEqual([s['rank'] for s in q],list(range(1,len(q)+1)))
    def test_deterministic_regeneration(self):
        first=(self.root/'demo/data.json').read_bytes()
        generate(self.root);analyze(self.root)
        self.assertEqual(first,(self.root/'demo/data.json').read_bytes())
    def test_missing_rows_fail(self):
        p=self.root/'data/daily_value.csv';original=p.read_bytes()
        try:
            lines=original.decode().splitlines(True);p.write_text(''.join(lines[:1]+lines[2:]))
            with self.assertRaisesRegex(ValueError,'Missing daily observation'):load_data(self.root)
        finally:p.write_bytes(original)
    def test_nonfinite_spend_fails(self):
        p=self.root/'data/daily_value.csv';original=p.read_bytes()
        try:
            lines=original.decode().splitlines(True);parts=lines[1].strip().split(',');parts[-1]='nan';lines[1]=','.join(parts)+'\n';p.write_text(''.join(lines))
            with self.assertRaisesRegex(ValueError,'invalid value'):load_data(self.root)
        finally:p.write_bytes(original)

if __name__=='__main__':unittest.main()
