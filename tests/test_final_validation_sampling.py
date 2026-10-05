"""Synthetic tests for the reproducible QA-sampling helpers."""
import unittest

import pandas as pd

from data.proprosessing.final_validation_sampling import allocate_strata, select_households


class FinalValidationSamplingTests(unittest.TestCase):
    def test_allocation_is_exact_and_censuses_small_strata(self):
        allocation = allocate_strata({"large": 100, "medium": 50, "tiny": 5}, target=60, minimum=15)
        self.assertEqual(sum(allocation.values()), 60)
        self.assertEqual(allocation["tiny"], 5)
        self.assertGreaterEqual(allocation["large"], 15)
        self.assertGreaterEqual(allocation["medium"], 15)

    def test_allocation_below_minimum_is_proportional_and_exact(self):
        allocation = allocate_strata({"a": 100, "b": 50, "c": 5}, target=10, minimum=15)
        self.assertEqual(sum(allocation.values()), 10)
        self.assertEqual(allocation, {"a": 7, "b": 3, "c": 0})

    def test_sample_is_repeatable_and_contains_row_positions_not_ids(self):
        rows = []
        for household in range(30):
            for person in range(1 + household % 2):
                rows.append({"folio": f"synthetic-{household:03d}", "nro": str(person + 1),
                             "depto": str(household % 3 + 1), "area": str(household % 2 + 1)})
        frame = pd.DataFrame(rows, dtype="string")
        sample_a, design_a, seed_a = select_households(frame, "0123456789abcdef" + "0" * 48, target=12)
        sample_b, design_b, seed_b = select_households(frame, "0123456789abcdef" + "0" * 48, target=12)
        pd.testing.assert_frame_equal(sample_a, sample_b)
        pd.testing.assert_frame_equal(design_a, design_b)
        self.assertEqual(seed_a, seed_b)
        self.assertEqual(int(design_a.households_selected_n_h.sum()), 12)
        self.assertNotIn("folio", sample_a.columns)
        self.assertNotIn("nro", sample_a.columns)
        self.assertTrue(sample_a.source_csv_row_number_1based.between(2, len(frame) + 1).all())


if __name__ == "__main__":
    unittest.main()
