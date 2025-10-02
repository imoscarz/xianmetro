import unittest
from xianmetro.core import plan_route

class TestRoutePlanning(unittest.TestCase):

    def test_least_transfer(self):
        result = plan_route("1422 803|1422 803", "1756 749|1756 749", strategy=1)
        self.assertIsInstance(result, dict)
        self.assertIn("route", result)
        self.assertIn("total_stops", result)
        self.assertIn("total_distance", result)
        self.assertIn("transfers", result)

    def test_least_stops(self):
        result = plan_route("1422 803|1422 803", "1756 749|1756 749", strategy=2)
        self.assertIsInstance(result, dict)

    def test_shortest_distance(self):
        result = plan_route("1422 803|1422 803", "1756 749|1756 749", strategy=3)
        self.assertIsInstance(result, dict)

    def test_transfer_station(self):
        result = plan_route("1422 803|1422 803", "1422 749|1422 749", strategy=1)
        self.assertIsInstance(result, dict)

    def test_same_start_end(self):
        result = plan_route("1422 803|1422 803", "1422 803|1422 803", strategy=1)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["total_stops"], 1)

if __name__ == "__main__":
    unittest.main()