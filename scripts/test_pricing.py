#!/usr/bin/env python3
"""Tests for scripts/pricing.py. Run with:

    python3 -m unittest discover -s scripts -p 'test_pricing.py' -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pricing  # noqa: E402


class TestPricing(unittest.TestCase):
    def test_price_table_values(self):
        self.assertEqual(
            pricing.PRICES["deepseek-v4.1-flash"], (0.15, 0.60, 0.003, 100)
        )
        self.assertEqual(pricing.PRICES["glm-5.3"], (1.40, 4.40, 0.26, 15))
        self.assertEqual(pricing.PRICES["glm-5.3-flash"], (0.15, 0.50, 0.03, 60))

    def test_go_prices_is_same_table(self):
        self.assertIs(pricing.GO_PRICES, pricing.PRICES)

    def test_plan_split(self):
        self.assertEqual(
            pricing.PLAN_SPLIT, {"5h": 0.20, "weekly": 0.50, "monthly": 1.0}
        )


if __name__ == "__main__":
    unittest.main()
