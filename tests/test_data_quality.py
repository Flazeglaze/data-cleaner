import unittest

import pandas as pd

from data_generator import generate_customers
from data_validator import build_quality_report, find_invalid_emails, find_missing_phones


class DataQualityTests(unittest.TestCase):
    def test_generate_customers_includes_rows(self):
        df = generate_customers(num_rows=50, seed=7)
        self.assertEqual(len(df), 50 + 20)

    def test_missing_phone_detection_handles_empty_strings(self):
        df = pd.DataFrame(
            {
                "name": ["Alice", "Bob"],
                "email": ["alice@example.com", "bob@example.com"],
                "phone": ["", "021 123 4567"],
            }
        )
        missing = find_missing_phones(df)
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing.iloc[0]["name"], "Alice")

    def test_invalid_email_detection_finds_bad_values(self):
        df = pd.DataFrame(
            {
                "name": ["Alice", "Bob"],
                "email": ["not-an-email", "bob@example.com"],
                "phone": ["021 123 4567", "021 765 4321"],
            }
        )
        invalid = find_invalid_emails(df)
        self.assertEqual(len(invalid), 1)
        self.assertEqual(invalid.iloc[0]["email"], "not-an-email")

    def test_quality_report_counts_issues(self):
        df = pd.DataFrame(
            {
                "name": ["Alice", "Alice", "Bob"],
                "email": ["alice@example.com", "alice@example.com", "bad-email"],
                "phone": ["", "021 123 4567", "021 765 4321"],
            }
        )
        report = build_quality_report(df)
        self.assertEqual(report["total_rows"], 3)
        self.assertEqual(report["invalid_email_count"], 1)
        self.assertEqual(report["missing_phone_count"], 1)


if __name__ == "__main__":
    unittest.main()
