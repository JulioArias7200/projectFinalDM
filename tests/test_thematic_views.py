"""Synthetic tests for thematic view scope, keys, and household conflicts."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "data" / "proprosessing" / "preprocessing.py"
SPEC = importlib.util.spec_from_file_location("persona_preprocessing_for_tests", MODULE_PATH)
PREPROCESSING = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PREPROCESSING
SPEC.loader.exec_module(PREPROCESSING)


class ThematicViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = pd.DataFrame({
            "folio": ["h1", "h1", "h2", "h2", "h3", "h4", "h5", "h6"],
            "nro": ["1", "2", "1", "2", "1", "1", "1", "1"],
            "area": ["1"] * 8, "depto": ["1"] * 8, "upm": ["u1"] * 8,
            "estrato": ["1"] * 8, "factor": ["10"] * 8,
            "s01a_02": ["2", "1", "2", "1", "1", "2", "2", "2"],
            "s01a_03": ["13", "3", "50", "6", "51", "12", "", "7"],
            "s01a_04c": ["2012", "2022", "1975", "2019", "1974", "2013", "", "2018"],
            "s02a_01": ["1"] * 8, "s02b_06": ["1", "NA", "2", "NA", "NA", "NA", "NA", "NA"],
            "s02c_15": ["NA"] * 8, "s02d_16": ["NA"] * 8,
            "s03a_01": ["1"] * 8, "s04a_01": ["1"] * 8,
            "s04e_25": ["1", "NA", "2", "NA", "NA", "NA", "NA", "NA"],
            "s04e_26_cod": ["A", "NA", "B", "NA", "NA", "NA", "NA", "NA"],
            "s04f_31a": ["0"] * 8, "pet": ["1"] * 8, "condact": ["1"] * 8,
            "s05a_01a": ["0"] * 8, "totper": ["2", "2", "2", "2", "1", "1", "1", "1"],
            "tipohogar": ["1"] * 8, "yhog": ["100", "100", "200", "250", "80", "60", "70", "90"],
            "yhogpc": ["50", "50", "100", "125", "80", "60", "70", "90"],
            "z": ["90", "NA", "90", "90", "90", "90", "90", "90"], "zext": ["50"] * 8,
            "p0": ["1"] * 8, "p1": ["0"] * 8, "p2": ["0"] * 8,
            "pext0": ["0"] * 8, "pext1": ["0"] * 8, "pext2": ["0"] * 8,
        })
        self.metadata = {
            "dataset_id": "EH2025_Persona", "run_id": "synthetic-run",
            "version_id": "synthetic-version", "output_dataset_sha256": "synthetic-hash",
        }

    def test_universe_views_keep_expected_rows_and_secondary_exception(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = PREPROCESSING.build_thematic_views(self.frame, Path(temp) / "views", self.metadata)
            counts = {v["view_id"]: v["rows"] for v in result["views"]}
            self.assertEqual(counts["demografia_persona"], 8)
            self.assertEqual(counts["salud_fecundidad_mujeres_13_50"], 2)
            self.assertEqual(counts["salud_asistencia_infantil_menores_6"], 1)
            self.assertEqual(counts["salud_bono_menores_5"], 1)
            self.assertEqual(counts["educacion_personas_4_mas"], 6)
            self.assertEqual(counts["empleo_personas_7_mas"], 5)
            self.assertEqual(counts["empleo_secundario_casos"], 2)
            secondary = pd.read_csv(Path(temp) / "views" / "empleo_secundario_casos.csv", dtype=str)
            self.assertEqual((secondary["secondary_filter_status"] == "affirmative_filter").sum(), 1)
            self.assertEqual((secondary["secondary_filter_status"] == "reported_data_with_negative_filter_review").sum(), 1)
            for view in result["views"]:
                data = pd.read_csv(Path(temp) / "views" / view["file"], dtype=str)
                self.assertFalse(data.duplicated(view["key"]).any(), view["view_id"])

    def test_household_summary_excludes_nonconstant_values_without_choosing_one(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = PREPROCESSING.build_thematic_views(self.frame, Path(temp) / "views", self.metadata)
            household = pd.read_csv(Path(temp) / "views" / "hogar_resumen_persona_candidato.csv", dtype=str)
            self.assertEqual(len(household), 6)
            self.assertNotIn("yhog", household.columns)
            self.assertNotIn("yhogpc", household.columns)
            self.assertIn("z", household.columns)
            self.assertEqual(household.loc[household.folio == "h1", "z"].iloc[0], "90")
            self.assertEqual(result["household_field_conflicts_excluded"]["yhog"], 1)
            self.assertEqual(result["household_field_conflicts_excluded"]["yhogpc"], 1)
            self.assertEqual(result["household_missing_copies_coalesced"]["z"], 1)
            self.assertEqual(household.loc[household.folio == "h1", "person_records_in_source"].iloc[0], "2")

    def test_does_not_mutate_source_or_overwrite_existing_output(self) -> None:
        original = self.frame.copy(deep=True)
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "views"
            PREPROCESSING.build_thematic_views(self.frame, target, self.metadata)
            pd.testing.assert_frame_equal(self.frame, original)
            with self.assertRaises(FileExistsError):
                PREPROCESSING.build_thematic_views(self.frame, target, self.metadata)

    def test_lowercases_only_allowlisted_open_text_and_preserves_missing_and_ids(self) -> None:
        raw = pd.DataFrame({
            "folio": ["H-ABC", "H-DEF"], "nro": ["1", "1"],
            "s01b_12e": ["MiXed Answer", "NA"],
        })
        original = raw.copy(deep=True)
        cleaned, rule_log, cell_log = PREPROCESSING.clean_frame(raw, PREPROCESSING.CONFIG)
        self.assertEqual(cleaned["folio"].tolist(), ["H-ABC", "H-DEF"])
        self.assertEqual(cleaned["s01b_12e"].tolist(), ["mixed answer", "NA"])
        self.assertEqual(len(cell_log.loc[cell_log["rule_id"].eq("S-02")]), 1)
        self.assertEqual(int(rule_log.loc[rule_log["rule_id"].eq("S-02"), "cells_changed"].iloc[0]), 1)
        pd.testing.assert_frame_equal(raw, original)

    def test_exact_duplicates_are_audited_and_blocked_without_deletion(self) -> None:
        duplicate = pd.DataFrame({
            "folio": ["H-ABC", "H-ABC"], "nro": ["1", "1"],
            "s01b_12e": ["NA", "NA"],
        })
        with self.assertRaisesRegex(ValueError, "No se deduplicó"):
            PREPROCESSING.clean_frame(duplicate, PREPROCESSING.CONFIG)


if __name__ == "__main__":
    unittest.main()
