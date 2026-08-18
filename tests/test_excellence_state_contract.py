import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "machine" / "excellence-state.json"
TARGET_PATH = ROOT / "machine" / "target-contract.json"
POSITION_PATH = ROOT / "machine" / "apex-position.json"

PRINCIPAL_STATES = [
    "DISCOVERED",
    "IDENTITY_RESOLVED",
    "PROBLEM_VERIFIED",
    "TARGET_CONTRACTED",
    "SEEDED",
    "VERTICAL_SLICE",
    "IMPLEMENTED",
    "TESTED",
    "ADVERSARIAL_VERIFIED",
    "OPERABLE",
    "PROOF_REPRODUCED",
    "PROMOTED",
    "CANONICAL",
    "EVOLVING",
]
STAGE_GATES = {
    "IDENTITY_RESOLVED": "IDENTITY_RESOLVED",
    "PROBLEM_VERIFIED": "PROBLEM_VERIFIED",
    "TARGET_CONTRACTED": "TARGET_CONTRACT_FROZEN",
    "SEEDED": "DONOR_PLAN_RESOLVED",
    "VERTICAL_SLICE": "VERTICAL_SLICE_ALIVE",
    "IMPLEMENTED": "CENTRAL_MECHANISM_PRESENT",
    "TESTED": "DETERMINISTIC_PROOF_GREEN",
    "ADVERSARIAL_VERIFIED": "ADVERSARIAL_SURVIVAL",
    "OPERABLE": "OPERABLE_AND_OBSERVABLE",
    "PROOF_REPRODUCED": "PROOF_RECEIPT_BOUND",
    "PROMOTED": "AUTHORITY_BOUND",
    "CANONICAL": "APEX_POSITION_RESOLVED",
    "EVOLVING": "EVOLUTION_CURSOR_DEFINED",
}


class ExcellenceStateContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        cls.target = json.loads(TARGET_PATH.read_text(encoding="utf-8"))
        cls.position = json.loads(POSITION_PATH.read_text(encoding="utf-8"))

    def test_principal_state_has_all_prerequisite_gates(self):
        current = self.state["principal_state"]
        end = PRINCIPAL_STATES.index(current)
        for stage in PRINCIPAL_STATES[1 : end + 1]:
            gate = STAGE_GATES[stage]
            self.assertEqual(
                self.state["gates"].get(gate, {}).get("status"),
                "PASS",
                f"{current} outruns {gate}",
            )

    def test_target_contract_matches_repository_and_state(self):
        self.assertEqual(
            self.target["identity"]["repository_id"],
            "GlacierEQ/waymo-uncertainty-lane-graph",
        )
        self.assertEqual(
            self.target["current"]["principal_state"],
            self.state["principal_state"],
        )
        self.assertEqual(self.target["donor_plan"]["status"], "RESOLVED")

    def test_apex_position_preserves_independent_identity(self):
        self.assertEqual(self.position["position_state"], "RESOLVED")
        policy = self.position["integration_policy"]
        self.assertTrue(policy["preserve_repository_identity"])
        self.assertTrue(policy["preserve_lineage"])
        self.assertTrue(policy["presentation_independent"])
        self.assertTrue(policy["absorption_requires_functional_equivalence"])
        self.assertTrue(policy["absorption_requires_proof_equivalence"])

    def test_external_claim_ceiling_does_not_exceed_promotion_authority(self):
        self.assertEqual(self.state["claim_ceiling"], "PROMOTED")


if __name__ == "__main__":
    unittest.main()
