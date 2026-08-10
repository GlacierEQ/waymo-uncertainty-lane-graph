"""Uncertainty lane graph — deterministic topology with explicit unknown edges.

The graph preserves FREE / UNKNOWN / BLOCKED as distinct edge states. Conflicting
redefinitions of the same directed edge fail closed instead of making route
semantics depend on insertion order. Default routing refuses UNKNOWN edges;
an explicit uncertainty-first route mode can traverse UNKNOWN only when needed.
"""
from __future__ import annotations

import hashlib
import heapq
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class EdgeState(str, Enum):
    FREE = "FREE"
    UNKNOWN = "UNKNOWN"
    BLOCKED = "BLOCKED"


_NODE_RE = re.compile(r"^[A-Za-z0-9_.:/-]+$")


def digest(obj: object) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class PathDecision:
    path: tuple[str, ...] | None
    allow_unknown: bool
    unknown_edges: int | None
    hops: int | None
    reason: str | None
    graph_fingerprint: str
    fingerprint: str


@dataclass
class UncertaintyLaneGraph:
    # directed node -> neighbor -> state
    edges: Dict[str, Dict[str, EdgeState]] = field(default_factory=dict)

    @staticmethod
    def _validate_node(node: str) -> None:
        if not isinstance(node, str) or not node or not _NODE_RE.fullmatch(node):
            raise ValueError("node identifiers must be non-empty machine-safe tokens")

    @staticmethod
    def _validate_state(state: EdgeState) -> None:
        if not isinstance(state, EdgeState):
            raise ValueError("state must be EdgeState")

    def add_edge(self, a: str, b: str, state: EdgeState) -> None:
        self._validate_node(a)
        self._validate_node(b)
        self._validate_state(state)
        outgoing = self.edges.setdefault(a, {})
        existing = outgoing.get(b)
        if existing is None:
            outgoing[b] = state
            return
        if existing is state:
            return
        raise ValueError(
            f"conflicting state for directed edge {a}->{b}: "
            f"{existing.value} vs {state.value}"
        )

    def nodes(self) -> frozenset[str]:
        result = set(self.edges)
        for outgoing in self.edges.values():
            result.update(outgoing)
        return frozenset(result)

    def graph_fingerprint(self) -> str:
        return digest(
            {
                "edges": [
                    {"from": src, "to": dst, "state": state.value}
                    for src in sorted(self.edges)
                    for dst, state in sorted(self.edges[src].items())
                ]
            }
        )

    def _validate_endpoints(self, src: str, dst: str) -> None:
        self._validate_node(src)
        self._validate_node(dst)

    def shortest_path(
        self, src: str, dst: str, allow_unknown: bool = False
    ) -> list[str] | None:
        """Deterministic minimum-hop route under the requested edge policy."""
        decision = self.decide_path(src, dst, allow_unknown=allow_unknown)
        return list(decision.path) if decision.path is not None else None

    def decide_path(
        self, src: str, dst: str, allow_unknown: bool = False
    ) -> PathDecision:
        self._validate_endpoints(src, dst)
        if not isinstance(allow_unknown, bool):
            raise ValueError("allow_unknown must be boolean")

        graph_fp = self.graph_fingerprint()
        known = self.nodes()
        if src not in known or dst not in known:
            return self._decision(
                None,
                allow_unknown,
                None,
                None,
                "UNKNOWN_ENDPOINT",
                graph_fp,
                mode="minimum_hops",
            )

        # Heap key makes equal-hop choices lexicographically deterministic.
        frontier: list[tuple[int, tuple[str, ...], str, int]] = [
            (0, (src,), src, 0)
        ]
        best_hops: dict[str, int] = {src: 0}
        while frontier:
            hops, path, node, unknown_count = heapq.heappop(frontier)
            if hops != best_hops.get(node):
                continue
            if node == dst:
                return self._decision(
                    path,
                    allow_unknown,
                    unknown_count,
                    hops,
                    None,
                    graph_fp,
                    mode="minimum_hops",
                )
            for nbr, state in sorted(self.edges.get(node, {}).items()):
                if state is EdgeState.BLOCKED:
                    continue
                if state is EdgeState.UNKNOWN and not allow_unknown:
                    continue
                new_hops = hops + 1
                previous = best_hops.get(nbr)
                if previous is not None and new_hops > previous:
                    continue
                if previous is None or new_hops < previous:
                    best_hops[nbr] = new_hops
                heapq.heappush(
                    frontier,
                    (
                        new_hops,
                        path + (nbr,),
                        nbr,
                        unknown_count + int(state is EdgeState.UNKNOWN),
                    ),
                )

        return self._decision(
            None,
            allow_unknown,
            None,
            None,
            "NO_ROUTE",
            graph_fp,
            mode="minimum_hops",
        )

    def least_uncertain_path(self, src: str, dst: str) -> list[str] | None:
        """Prefer fewer UNKNOWN edges, then fewer hops, then lexical path order."""
        decision = self.decide_least_uncertain_path(src, dst)
        return list(decision.path) if decision.path is not None else None

    def decide_least_uncertain_path(self, src: str, dst: str) -> PathDecision:
        self._validate_endpoints(src, dst)
        graph_fp = self.graph_fingerprint()
        known = self.nodes()
        if src not in known or dst not in known:
            return self._decision(
                None,
                True,
                None,
                None,
                "UNKNOWN_ENDPOINT",
                graph_fp,
                mode="uncertainty_then_hops",
            )

        frontier: list[tuple[int, int, tuple[str, ...], str]] = [
            (0, 0, (src,), src)
        ]
        best: dict[str, tuple[int, int, tuple[str, ...]]] = {
            src: (0, 0, (src,))
        }
        while frontier:
            unknown_count, hops, path, node = heapq.heappop(frontier)
            if best.get(node) != (unknown_count, hops, path):
                continue
            if node == dst:
                return self._decision(
                    path,
                    True,
                    unknown_count,
                    hops,
                    None,
                    graph_fp,
                    mode="uncertainty_then_hops",
                )
            for nbr, state in sorted(self.edges.get(node, {}).items()):
                if state is EdgeState.BLOCKED:
                    continue
                candidate = (
                    unknown_count + int(state is EdgeState.UNKNOWN),
                    hops + 1,
                    path + (nbr,),
                )
                if nbr not in best or candidate < best[nbr]:
                    best[nbr] = candidate
                    heapq.heappush(
                        frontier,
                        (candidate[0], candidate[1], candidate[2], nbr),
                    )

        return self._decision(
            None,
            True,
            None,
            None,
            "NO_ROUTE",
            graph_fp,
            mode="uncertainty_then_hops",
        )

    @staticmethod
    def _decision(
        path: tuple[str, ...] | None,
        allow_unknown: bool,
        unknown_edges: int | None,
        hops: int | None,
        reason: str | None,
        graph_fingerprint: str,
        *,
        mode: str,
    ) -> PathDecision:
        body = {
            "path": list(path) if path is not None else None,
            "allow_unknown": allow_unknown,
            "unknown_edges": unknown_edges,
            "hops": hops,
            "reason": reason,
            "graph_fingerprint": graph_fingerprint,
            "mode": mode,
        }
        return PathDecision(
            path,
            allow_unknown,
            unknown_edges,
            hops,
            reason,
            graph_fingerprint,
            digest(body),
        )
