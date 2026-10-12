import re
from pathlib import Path

import pandas as pd

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}$"
)


def load_customers(path: str | Path = "customers.csv") -> pd.DataFrame:
    return pd.read_csv(path)


def normalise_customers(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["name"] = cleaned["name"].astype("string").str.strip()
    cleaned["email"] = cleaned["email"].astype("string").str.strip().str.lower()
    cleaned["phone"] = cleaned["phone"].astype("string").str.strip()
    cleaned["email"] = cleaned["email"].replace(r"^$", pd.NA, regex=True)
    cleaned["phone"] = cleaned["phone"].replace(r"^$", pd.NA, regex=True)
    return cleaned


def is_valid_email(value: object) -> bool:
    if pd.isna(value):
        return False
    email = str(value).strip().lower()
    return bool(EMAIL_PATTERN.fullmatch(email))


def find_missing_phones(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = normalise_customers(df)
    return cleaned[cleaned["phone"].isna()].copy()


def find_invalid_emails(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = normalise_customers(df)
    valid = cleaned["email"].map(is_valid_email)
    return cleaned[~valid].copy()


def find_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = normalise_customers(df)
    return cleaned[cleaned.duplicated(subset=["email"], keep=False)].copy()


def build_quality_report(df: pd.DataFrame) -> dict:
    cleaned = normalise_customers(df)
    invalid_email_rows = find_invalid_emails(cleaned)
    missing_phone_rows = find_missing_phones(cleaned)
    duplicate_rows = find_duplicates(cleaned)

    return {
        "total_rows": len(cleaned),
        "invalid_email_count": len(invalid_email_rows),
        "missing_phone_count": len(missing_phone_rows),
        "duplicate_count": len(duplicate_rows),
        "clean_rows": len(cleaned) - len(invalid_email_rows) - len(missing_phone_rows),
    }


def inspect_customers(path: str | Path = "customers.csv") -> dict:
    df = load_customers(path)
    return {
        "report": build_quality_report(df),
        "invalid_emails": find_invalid_emails(df),
        "missing_phones": find_missing_phones(df),
        "duplicates": find_duplicates(df),
    }
