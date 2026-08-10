from __future__ import annotations

import unittest

from src.lane_graph import EdgeState, UncertaintyLaneGraph


class LaneTests(unittest.TestCase):
    def test_refuses_unknown_by_default(self):
        graph = UncertaintyLaneGraph()
        graph.add_edge("A", "B", EdgeState.FREE)
        graph.add_edge("B", "C", EdgeState.UNKNOWN)
        self.assertIsNone(graph.shortest_path("A", "C", allow_unknown=False))
        self.assertEqual(
            graph.shortest_path("A", "C", allow_unknown=True),
            ["A", "B", "C"],
        )

    def test_blocked_never_routes(self):
        graph = UncertaintyLaneGraph()
        graph.add_edge("A", "B", EdgeState.BLOCKED)
        self.assertIsNone(graph.shortest_path("A", "B", allow_unknown=True))
        self.assertIsNone(graph.least_uncertain_path("A", "B"))

    def test_exact_duplicate_edge_is_idempotent(self):
        graph = UncertaintyLaneGraph()
        graph.add_edge("A", "B", EdgeState.FREE)
        before = graph.graph_fingerprint()
        graph.add_edge("A", "B", EdgeState.FREE)
        self.assertEqual(before, graph.graph_fingerprint())
        self.assertEqual(graph.shortest_path("A", "B"), ["A", "B"])

    def test_conflicting_edge_state_refuses(self):
        graph = UncertaintyLaneGraph()
        graph.add_edge("A", "B", EdgeState.FREE)
        with self.assertRaisesRegex(ValueError, "conflicting state"):
            graph.add_edge("A", "B", EdgeState.BLOCKED)
        self.assertEqual(graph.shortest_path("A", "B"), ["A", "B"])

    def test_equal_hop_shortest_path_is_insertion_order_independent(self):
        first = UncertaintyLaneGraph()
        first.add_edge("A", "C", EdgeState.FREE)
        first.add_edge("C", "D", EdgeState.FREE)
        first.add_edge("A", "B", EdgeState.FREE)
        first.add_edge("B", "D", EdgeState.FREE)

        second = UncertaintyLaneGraph()
        second.add_edge("B", "D", EdgeState.FREE)
        second.add_edge("A", "B", EdgeState.FREE)
        second.add_edge("C", "D", EdgeState.FREE)
        second.add_edge("A", "C", EdgeState.FREE)

        self.assertEqual(first.graph_fingerprint(), second.graph_fingerprint())
        self.assertEqual(first.shortest_path("A", "D"), ["A", "B", "D"])
        self.assertEqual(first.shortest_path("A", "D"), second.shortest_path("A", "D"))

    def test_least_uncertain_prefers_longer_free_route(self):
        graph = UncertaintyLaneGraph()
        graph.add_edge("A", "X", EdgeState.UNKNOWN)
        graph.add_edge("X", "D", EdgeState.FREE)
        graph.add_edge("A", "B", EdgeState.FREE)
        graph.add_edge("B", "C", EdgeState.FREE)
        graph.add_edge("C", "D", EdgeState.FREE)

        self.assertEqual(
            graph.shortest_path("A", "D", allow_unknown=True),
            ["A", "X", "D"],
        )
        self.assertEqual(
            graph.least_uncertain_path("A", "D"),
            ["A", "B", "C", "D"],
        )

    def test_least_uncertain_uses_unknown_when_no_free_route_exists(self):
        graph = UncertaintyLaneGraph()
        graph.add_edge("A", "B", EdgeState.FREE)
        graph.add_edge("B", "C", EdgeState.UNKNOWN)
        decision = graph.decide_least_uncertain_path("A", "C")
        self.assertEqual(decision.path, ("A", "B", "C"))
        self.assertEqual(decision.unknown_edges, 1)
        self.assertEqual(decision.hops, 2)
        self.assertIsNone(decision.reason)

    def test_unknown_endpoint_refuses_without_phantom_self_route(self):
        graph = UncertaintyLaneGraph()
        decision = graph.decide_path("A", "A")
        self.assertIsNone(decision.path)
        self.assertEqual(decision.reason, "UNKNOWN_ENDPOINT")

    def test_decision_receipt_binds_graph_and_policy(self):
        graph = UncertaintyLaneGraph()
        graph.add_edge("A", "B", EdgeState.FREE)
        strict = graph.decide_path("A", "B", allow_unknown=False)
        permissive = graph.decide_path("A", "B", allow_unknown=True)
        self.assertEqual(strict.path, permissive.path)
        self.assertEqual(strict.graph_fingerprint, permissive.graph_fingerprint)
        self.assertNotEqual(strict.fingerprint, permissive.fingerprint)

        graph.add_edge("B", "C", EdgeState.FREE)
        changed = graph.decide_path("A", "B", allow_unknown=False)
        self.assertNotEqual(strict.graph_fingerprint, changed.graph_fingerprint)
        self.assertNotEqual(strict.fingerprint, changed.fingerprint)

    def test_invalid_nodes_state_and_policy_refuse(self):
        graph = UncertaintyLaneGraph()
        with self.assertRaisesRegex(ValueError, "machine-safe"):
            graph.add_edge("", "B", EdgeState.FREE)
        with self.assertRaisesRegex(ValueError, "machine-safe"):
            graph.add_edge("bad node", "B", EdgeState.FREE)
        with self.assertRaisesRegex(ValueError, "EdgeState"):
            graph.add_edge("A", "B", "FREE")  # type: ignore[arg-type]

        graph.add_edge("A", "B", EdgeState.FREE)
        with self.assertRaisesRegex(ValueError, "allow_unknown"):
            graph.decide_path("A", "B", allow_unknown=1)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
