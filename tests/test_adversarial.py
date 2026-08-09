from __future__ import annotations
import unittest
from src.lane_graph import UncertaintyLaneGraph, EdgeState

class Adv(unittest.TestCase):
    def test_blocked_never_traversed(self):
        g = UncertaintyLaneGraph()
        g.add_edge("A", "B", EdgeState.BLOCKED)
        self.assertIsNone(g.shortest_path("A", "B", allow_unknown=True))
    def test_unknown_default_refuse(self):
        g = UncertaintyLaneGraph()
        g.add_edge("A", "B", EdgeState.UNKNOWN)
        self.assertIsNone(g.shortest_path("A", "B", allow_unknown=False))
    def test_free_path(self):
        g = UncertaintyLaneGraph()
        g.add_edge("A", "B", EdgeState.FREE)
        self.assertEqual(g.shortest_path("A", "B"), ["A", "B"])

