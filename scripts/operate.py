#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lane_graph import UncertaintyLaneGraph, EdgeState

def main() -> int:
    g = UncertaintyLaneGraph()
    g.add_edge("A", "B", EdgeState.FREE)
    g.add_edge("B", "C", EdgeState.UNKNOWN)
    refuse = g.shortest_path("A", "C", allow_unknown=False)
    allow = g.shortest_path("A", "C", allow_unknown=True)
    out = {"unknown_refused": refuse is None, "path_when_allowed": allow, "ok": refuse is None and allow == ["A", "B", "C"]}
    print(json.dumps(out, sort_keys=True))
    return 0 if out["ok"] else 1
if __name__ == "__main__":
    raise SystemExit(main())
