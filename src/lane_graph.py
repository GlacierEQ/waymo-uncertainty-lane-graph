"""Uncertainty lane graph — topology with explicit unknown edges."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple


class EdgeState(str, Enum):
    FREE = "FREE"
    UNKNOWN = "UNKNOWN"
    BLOCKED = "BLOCKED"


@dataclass
class UncertaintyLaneGraph:
    # node -> list[(neighbor, state)]
    edges: Dict[str, List[Tuple[str, EdgeState]]] = field(default_factory=dict)

    def add_edge(self, a: str, b: str, state: EdgeState) -> None:
        self.edges.setdefault(a, []).append((b, state))

    def shortest_path(self, src: str, dst: str, allow_unknown: bool = False) -> list[str] | None:
        # BFS
        q: list[tuple[str, list[str]]] = [(src, [src])]
        seen: Set[str] = {src}
        while q:
            node, path = q.pop(0)
            if node == dst:
                return path
            for nbr, state in self.edges.get(node, []):
                if state is EdgeState.BLOCKED:
                    continue
                if state is EdgeState.UNKNOWN and not allow_unknown:
                    continue
                if nbr in seen:
                    continue
                seen.add(nbr)
                q.append((nbr, path + [nbr]))
        return None
