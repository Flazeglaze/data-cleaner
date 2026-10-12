import argparse
from pathlib import Path

import pandas as pd

from data_validator import is_valid_email, load_customers, normalise_customers

DEFAULT_INPUT = Path("customers.csv")
DEFAULT_OUTPUT = Path("customers_cleaned.csv")
DEFAULT_REVIEW_OUTPUT = Path("customers_review.csv")
REQUIRED_COLUMNS = {"name", "email", "phone"}


def clean_customers(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Input data is missing required columns: {missing}")

    cleaned = df.copy()
    for column in cleaned.select_dtypes(include=["object", "string"]).columns:
        cleaned[column] = cleaned[column].astype("string").str.strip()
        cleaned[column] = cleaned[column].replace(r"^$", pd.NA, regex=True)
    cleaned = normalise_customers(cleaned).reset_index(drop=True)

    valid_email = cleaned["email"].map(is_valid_email)
    missing_phone = cleaned["phone"].isna()
    duplicate_email = (
        cleaned["email"].notna()
        & cleaned.duplicated(subset=["email"], keep=False)
    )

    issues = []
    for row_index in range(len(cleaned)):
        row_issues = []
        if not valid_email.iloc[row_index]:
            row_issues.append("invalid_email")
        if missing_phone.iloc[row_index]:
            row_issues.append("missing_phone")
        if duplicate_email.iloc[row_index]:
            row_issues.append("duplicate_email")
        issues.append(";".join(row_issues))

    review_mask = pd.Series([bool(value) for value in issues])
    review = cleaned.loc[review_mask].copy()
    review.insert(0, "source_row", review.index + 2)
    review["quality_issues"] = [issues[index] for index in review.index]

    return cleaned, review.reset_index(drop=True)


def clean_file(
    input_path: str | Path = DEFAULT_INPUT,
    output_path: str | Path = DEFAULT_OUTPUT,
    review_path: str | Path = DEFAULT_REVIEW_OUTPUT,
) -> tuple[int, int]:
    input_path = Path(input_path)
    output_path = Path(output_path)
    review_path = Path(review_path)

    resolved_paths = [path.resolve() for path in (input_path, output_path, review_path)]
    if len(set(resolved_paths)) != len(resolved_paths):
        raise ValueError("Input, cleaned output, and review output must be different files.")

    source = load_customers(input_path)
    cleaned, review = clean_customers(source)
    cleaned.to_csv(output_path, index=False)
    review.to_csv(review_path, index=False)
    return len(cleaned), len(review)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize customer data and save rows needing review separately."
    )
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Input CSV (default: customers.csv)")
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Cleaned CSV output (default: customers_cleaned.csv)",
    )
    parser.add_argument(
        "--review-output",
        default=DEFAULT_REVIEW_OUTPUT,
        help="Rows needing review (default: customers_review.csv)",
    )
    args = parser.parse_args()

    try:
        total_rows, review_rows = clean_file(args.input, args.output, args.review_output)
    except (OSError, pd.errors.ParserError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")

    print(f"Processed {total_rows} rows.")
    print(f"Cleaned data saved to {args.output}.")
    print(f"{review_rows} rows flagged for review and saved to {args.review_output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
