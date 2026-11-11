import json
import unittest
from lifecycle import ROOT, classify

class Rules(unittest.TestCase):
    def setUp(self):
        self.c = json.loads((ROOT / "config.json").read_text())
    def stage(self, age=90, value=1000, previous=1000, active=20):
        return classify(age, value, previous, active, 300, self.c)[0]
    def test_new_account_is_not_churn(self):
        self.assertEqual(self.stage(age=12, value=0, previous=None, active=0), "Onboarding")
    def test_zero_baseline_not_infinite_growth(self):
        self.assertEqual(self.stage(previous=0), "Observe")
    def test_missing_history_not_churn(self):
        self.assertEqual(self.stage(value=0, previous=None, active=0), "Observe")
    def test_risk_requires_both_signals(self):
        self.assertEqual(self.stage(value=100, active=2), "At-risk")
        self.assertEqual(self.stage(value=100, active=20), "Observe")
    def test_growth_precedes_overlapping_maturity(self):
        self.assertEqual(self.stage(value=1150), "Growth")
    def test_low_value_stable_is_not_churn(self):
        self.assertEqual(self.stage(value=50, previous=50), "Observe")
    def test_stable_mature(self):
        self.assertEqual(self.stage(), "Mature")
    def test_strict_risk_boundary(self):
        self.assertEqual(self.stage(value=500, active=2), "Observe")

if __name__ == "__main__":
    unittest.main()
