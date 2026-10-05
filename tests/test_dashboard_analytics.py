"""Synthetic tests for published-data analytics and disclosure controls."""

import hashlib
import importlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from dashboard.services.dataset_service import DatasetService

dataset_module = importlib.import_module("dashboard.services.dataset_service")


class DashboardAnalyticsTests(unittest.TestCase):
    def test_small_categories_are_combined_and_suppressed(self):
        values = pd.Series(["1"] * 100 + ["2"] * 12 + ["3"] * 4)
        entries = DatasetService._chart_entry_rows(values, numeric_only=True)
        self.assertEqual(entries[0]["label"], "Código 1 (sin etiqueta en el diccionario)")
        self.assertEqual(entries[0]["display_count"], "100")
        complementary = next(item for item in entries if item["label"] == "Código 2 (sin etiqueta en el diccionario)")
        self.assertEqual(complementary["display_count"], "Supresión complementaria")
        self.assertEqual(complementary["bar_pct"], 0)
        small = next(item for item in entries if item["label"] == "Categorías suprimidas (<10 c/u)")
        self.assertEqual(small["display_count"], "Suprimido (<10 por categoría)")
        self.assertNotIn("count", complementary)
        self.assertNotIn("count", small)

    def test_literal_na_and_empty_are_separate_internal_categories(self):
        values = pd.Series(["", "NA"] * 12 + ["1"] * 12)
        entries = DatasetService._chart_entry_rows(values, numeric_only=True)
        self.assertEqual({entry["label"] for entry in entries}, {"Celda vacía", "Token NA", "Código 1 (sin etiqueta en el diccionario)"})

    def test_explicit_dictionary_labels_replace_generic_code_names(self):
        values = pd.Series(["1"] * 12 + ["2"] * 12)
        entries = DatasetService._chart_entry_rows(
            values,
            numeric_only=True,
            category_labels={"1": "1. Hombre", "2": "2. Mujer"},
        )
        self.assertEqual({entry["label"] for entry in entries}, {"Hombre (código 1)", "Mujer (código 2)"})

    def test_age_bins_follow_ddi_top_code_and_valid_range(self):
        self.assertEqual(DatasetService._age_display_label("0"), "0–4 años (incluye <1 año)")
        self.assertEqual(DatasetService._age_display_label("97"), "95–97 años")
        self.assertEqual(DatasetService._age_display_label("98"), "98 años o más (código tope 98)")
        self.assertEqual(DatasetService._age_display_label("99"), "Fuera del rango documentado (>98)")
        self.assertEqual(DatasetService._age_display_label(""), "Celda vacía")
        self.assertEqual(DatasetService._age_display_label("NA"), "Token NA")

    def test_published_reader_verifies_catalog_hash_and_reads_only_requested_columns(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            relative = Path("data/proprosessing/versions/persona-test")
            version_dir = root / relative
            version_dir.mkdir(parents=True)
            (version_dir / "manifest.json").write_text("{}", encoding="utf-8")
            csv_path = version_dir / "persona_clean_master.csv"
            csv_path.write_text("folio,nro,s01a_03\nh1,1,25\nh2,1,NA\n", encoding="utf-8")
            digest = hashlib.sha256(csv_path.read_bytes()).hexdigest()
            registry = root / "audit_log.json"
            registry.write_text(json.dumps({
                "published_version_id": "persona-test",
                "versions": [{"version_id": "persona-test", "status": "published_internal_with_semantic_limitations",
                              "relative_path": str(relative), "csv_file": csv_path.name, "csv_sha256": digest}],
            }), encoding="utf-8")
            with patch.object(dataset_module, "BASE_DIR", str(root)), \
                 patch.object(dataset_module, "VERSIONS_DIR", str(root / "data/proprosessing/versions")), \
                 patch.object(dataset_module, "REGISTRY_FILE", str(registry)):
                service = DatasetService()
                subset = service._load_published_columns(["s01a_03"])
                self.assertEqual(subset.columns.tolist(), ["s01a_03"])
                self.assertEqual(subset["s01a_03"].tolist(), ["25", "NA"])
                csv_path.write_text("folio,nro,s01a_03\nh1,1,26\nh2,1,NA\n", encoding="utf-8")
                self.assertIsNone(service._load_published_columns(["s01a_03"]))


if __name__ == "__main__":
    unittest.main()
