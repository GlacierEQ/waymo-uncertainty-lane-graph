from __future__ import annotations
import unittest
from src.lane_graph import EdgeState, UncertaintyLaneGraph

class LaneTests(unittest.TestCase):
    def test_refuses_unknown(self):
        g = UncertaintyLaneGraph()
        g.add_edge("A", "B", EdgeState.FREE)
        g.add_edge("B", "C", EdgeState.UNKNOWN)
        self.assertIsNone(g.shortest_path("A", "C", allow_unknown=False))
        self.assertEqual(g.shortest_path("A", "C", allow_unknown=True), ["A", "B", "C"])

if __name__ == "__main__":
    unittest.main()
