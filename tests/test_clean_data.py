import tempfile
import unittest
from pathlib import Path

import pandas as pd

from clean_data import clean_customers, clean_file, normalize_nz_phone


class CleanDataTests(unittest.TestCase):
    def test_normalizes_values_and_excludes_missing_contact_fields(self):
        source = pd.DataFrame(
            {
                "name": ["  Alice Smith  ", " Bob Jones ", " Carol Jones "],
                "email": [" ALICE@EXAMPLE.COM ", "bad-email", "   "],
                "phone": [" 021 234 5678 ", "   ", "021 222 3333"],
                "note": ["  customer  ", "  missing phone  ", " missing email "],
            }
        )

        cleaned, review = clean_customers(source)

        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.loc[0, "name"], "Alice Smith")
        self.assertEqual(cleaned.loc[0, "email"], "alice@example.com")
        self.assertEqual(cleaned.loc[0, "note"], "customer")
        self.assertEqual(review["source_row"].tolist(), [3, 4])
        self.assertEqual(
            review["quality_issues"].tolist(),
            ["invalid_email;missing_phone", "missing_email"],
        )
        self.assertTrue(cleaned["email"].notna().all())
        self.assertTrue(cleaned["phone"].notna().all())
        self.assertEqual(cleaned.loc[0, "phone"], "+64212345678")

    def test_keeps_only_valid_new_zealand_numbers_and_formats_e164(self):
        source = pd.DataFrame(
            {
                "name": ["Mobile", "Landline", "Invalid", "Overseas"],
                "email": [
                    "mobile@example.com",
                    "landline@example.com",
                    "invalid@example.com",
                    "overseas@example.com",
                ],
                "phone": [
                    "021 234 5678",
                    "09 302 1234",
                    "12345",
                    "+1 202 555 0100",
                ],
            }
        )

        cleaned, review = clean_customers(source)

        self.assertEqual(cleaned["phone"].tolist(), ["+64212345678", "+6493021234"])
        self.assertEqual(review["source_row"].tolist(), [4, 5])
        self.assertEqual(
            review["quality_issues"].tolist(),
            ["invalid_phone", "invalid_phone"],
        )
        self.assertIsNone(normalize_nz_phone("12345"))
        self.assertIsNone(normalize_nz_phone("+1 202 555 0100"))

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
                    "phone": ["021 234 5678"],
                }
            ).to_csv(input_path, index=False)

            result = clean_file(input_path, output_path, review_path)

            self.assertEqual(result, (1, 0))
            self.assertEqual(pd.read_csv(output_path).loc[0, "email"], "alice@example.com")
            self.assertEqual(len(pd.read_csv(review_path)), 0)


if __name__ == "__main__":
    unittest.main()
