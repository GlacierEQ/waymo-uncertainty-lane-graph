from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    text = (ROOT / path).read_text()
    for marker in ("<<<<<<<", "=======", ">>>>>>>"):
        if marker in text:
            raise AssertionError(f"unresolved conflict marker in {path}: {marker}")
    return json.loads(text)


CANONICAL = load("machine/apex-position.json")
CAPABILITIES = load("machine/capabilities.json")
TARGET = load("machine/target-contract.json")
STATE = load("machine/excellence-state.json")
PROOF = load("machine/apex-position-proof.json")


class CanonicalPositionContractTests(unittest.TestCase):
    def test_repository_owns_uncertainty_topology_not_freespace(self):
        self.assertEqual(CANONICAL["role"], "CANONICAL_SPECIALIST")
        self.assertEqual(
            CANONICAL["owns"],
            "conflict_safe_uncertainty_aware_lane_topology_routing",
        )
        self.assertIn("freespace certification", CANONICAL["does_not_own"])
        self.assertIn(
            "autonomous-driving actuation authority", CANONICAL["does_not_own"]
        )

    def test_freespace_sibling_is_not_integrated(self):
        edge = CANONICAL["relationships"][0]
        self.assertEqual(
            edge["repository"], "GlacierEQ/waymo-phantom-freespace-certificate"
        )
        self.assertFalse(edge["integration_exercised"])
        self.assertFalse(TARGET["donor_plan"]["integration_exercised"])

    def test_capabilities_are_repository_native(self):
        capabilities = set(CAPABILITIES["capabilities"])
        self.assertNotIn("hyper-scaling", capabilities)
        self.assertIn("conflicting_edge_state_refusal", capabilities)
        self.assertIn("default_unknown_edge_refusal", capabilities)
        self.assertIn("least_uncertain_route_policy", capabilities)
        self.assertIn("python_go_route_outcome_parity", capabilities)

    def test_state_is_evolving_but_external_claim_ceiling_stays_promoted(self):
        self.assertEqual(STATE["principal_state"], "EVOLVING")
        self.assertEqual(STATE["state"], "EVOLVING")
        self.assertEqual(STATE["claim_ceiling"], "PROMOTED")
        self.assertEqual(TARGET["current"]["external_claim_ceiling"], "PROMOTED")
        self.assertEqual(
            STATE["gates"]["APEX_POSITION_RESOLVED"]["status"], "PASS"
        )

    def test_proof_binds_exact_tested_source_and_run(self):
        self.assertEqual(
            PROOF["source_sha"],
            "e22e8a85d455cca69cfd40ebc7bcae0c2fedad07",
        )
        self.assertEqual(PROOF["workflow"]["run_id"], 31404546209)
        self.assertEqual(PROOF["workflow"]["conclusion"], "success")
        self.assertEqual(set(PROOF["workflow"]["jobs"]), {"py", "go"})

    def test_truth_boundary_excludes_external_authority(self):
        boundary = CAPABILITIES["truth_boundary"]
        self.assertIn("does not certify freespace", boundary)
        self.assertIn("autonomous-driving", boundary)
        self.assertIn("Waymo affiliation/adoption", boundary)


if __name__ == "__main__":
    unittest.main()
