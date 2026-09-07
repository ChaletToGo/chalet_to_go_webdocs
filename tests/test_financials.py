import unittest
from app.revista.financials import budget_context, product_context

class FinancialTests(unittest.TestCase):
    def test_budget_reconciles(self):
        budget = budget_context()
        self.assertEqual(budget['total'], 575000)
        self.assertEqual(budget['setup'] + budget['working_capital'], budget['total'])
        self.assertAlmostEqual(sum(item['percentage'] for item in budget['items']), 100)

    def test_confirmed_unit_economics(self):
        products = product_context()
        self.assertEqual([p['balance'] for p in products], [25000,40000,61000])
        self.assertEqual([p['scenarios'][-1] for p in products], [375000,600000,915000])
        for p in products:
            self.assertAlmostEqual(p['production_width'] + p['balance_width'], p['price']/1000)
