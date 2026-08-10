#!/usr/bin/env python3
"""ELITE_HAND_OPERATE — real UncertaintyLaneGraph shortest_path mechanism."""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lane_graph import EdgeState, UncertaintyLaneGraph


def main() -> int:
    g = UncertaintyLaneGraph()
    g.add_edge("a", "b", EdgeState.FREE)
    g.add_edge("b", "c", EdgeState.FREE)
    path = g.shortest_path("a", "c")
    expected = ["a", "b", "c"]
    out = {
        "repository": "GlacierEQ/waymo-uncertainty-lane-graph",
        "module": "lane_graph",
        "smoke": {
            "kind": "class",
            "name": "UncertaintyLaneGraph",
            "method": "shortest_path",
            "result": path,
            "content_checked": True,
            "invoked": True,
        },
        "ok": path == expected,
    }
    print(json.dumps(out, sort_keys=True, default=str))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
