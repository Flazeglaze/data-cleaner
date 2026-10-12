import tempfile
import unittest
from pathlib import Path

import pandas as pd

from clean_data import clean_customers, clean_file


class CleanDataTests(unittest.TestCase):
    def test_normalizes_values_and_preserves_rows(self):
        source = pd.DataFrame(
            {
                "name": ["  Alice Smith  ", " Bob Jones "],
                "email": [" ALICE@EXAMPLE.COM ", "bad-email"],
                "phone": [" 021 123 4567 ", "   "],
                "note": ["  customer  ", "  needs review  "],
            }
        )

        cleaned, review = clean_customers(source)

        self.assertEqual(len(cleaned), len(source))
        self.assertEqual(cleaned.loc[0, "name"], "Alice Smith")
        self.assertEqual(cleaned.loc[0, "email"], "alice@example.com")
        self.assertEqual(cleaned.loc[0, "note"], "customer")
        self.assertTrue(pd.isna(cleaned.loc[1, "phone"]))
        self.assertEqual(review["source_row"].tolist(), [3])
        self.assertEqual(review["quality_issues"].tolist(), ["invalid_email;missing_phone"])

    def test_flags_all_records_sharing_a_valid_email(self):
        source = pd.DataFrame(
            {
                "name": ["Alice", "Alicia", "Bob"],
                "email": ["alice@example.com", " ALICE@example.com ", "bad"],
                "phone": ["021 123 4567", "021 765 4321", "021 000 0000"],
            }
        )

        _, review = clean_customers(source)

        self.assertEqual(review["source_row"].tolist(), [2, 3, 4])
        self.assertEqual(
            review["quality_issues"].tolist(),
            ["duplicate_email", "duplicate_email", "invalid_email"],
        )

    def test_rejects_missing_required_columns(self):
        source = pd.DataFrame({"name": ["Alice"], "email": ["alice@example.com"]})

        with self.assertRaisesRegex(ValueError, "phone"):
            clean_customers(source)

    def test_clean_file_writes_separate_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "input.csv"
            output_path = Path(temp_dir) / "cleaned.csv"
            review_path = Path(temp_dir) / "review.csv"
            pd.DataFrame(
                {
                    "name": [" Alice "],
                    "email": [" alice@example.com "],
                    "phone": ["021 123 4567"],
                }
            ).to_csv(input_path, index=False)

            result = clean_file(input_path, output_path, review_path)

            self.assertEqual(result, (1, 0))
            self.assertEqual(pd.read_csv(output_path).loc[0, "email"], "alice@example.com")
            self.assertEqual(len(pd.read_csv(review_path)), 0)


if __name__ == "__main__":
    unittest.main()
