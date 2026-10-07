import json
from pathlib import Path
import unittest

from floodlens import AnalysisError, analyse


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "demo-manifest.json"


class FloodLensAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_returns_evidence_derived_counts(self):
        report = analyse(self.manifest)
        self.assertEqual(report["flood_debris"]["impacted_cell_count"], 4)
        self.assertEqual(report["infrastructure"]["impacted_asset_count"], 2)
        self.assertEqual(report["connectivity"]["cut_off_settlements"], ["Syabrubesi", "Timure"])

    def test_rejects_reference_damage_map_input(self):
        self.manifest["reference_damage_maps_used_as_input"] = True
        with self.assertRaisesRegex(AnalysisError, "must never"):
            analyse(self.manifest)

    def test_rejects_mismatched_orbits(self):
        self.manifest["after"]["sat:relative_orbit"] = 73
        with self.assertRaisesRegex(AnalysisError, "same relative orbit"):
            analyse(self.manifest)


if __name__ == "__main__":
    unittest.main()
