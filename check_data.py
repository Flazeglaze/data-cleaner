from data_validator import build_quality_report, inspect_customers, load_customers


def main() -> int:
    try:
        df = load_customers("customers.csv")
    except FileNotFoundError:
        print("customers.csv not found. Run python make_data.py first.")
        return 1

    report = build_quality_report(df)
    details = inspect_customers("customers.csv")

    print("Data quality report")
    for key, value in report.items():
        print(f"- {key}: {value}")

    print("\nInvalid email rows:")
    print(details["invalid_emails"])

    print("\nMissing phone rows:")
    print(details["missing_phones"])

    print("\nDuplicate rows:")
    print(details["duplicates"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
