import random
from pathlib import Path

import pandas as pd
from faker import Faker


DEFAULT_OUTPUT = Path("customers.csv")


def generate_customers(num_rows: int = 200, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    fake = Faker("en_NZ")

    rows = [
        {"name": fake.name(), "email": fake.email(), "phone": fake.phone_number()}
        for _ in range(num_rows)
    ]

    duplicate_indexes = random.sample(range(len(rows)), min(20, len(rows)))
    for index in duplicate_indexes:
        original = rows[index]
        rows.append({**original, "name": original["name"].replace("a", "e", 1)})

    if len(rows) > 5:
        rows[5]["email"] = "not-an-email"
    if len(rows) > 9:
        rows[9]["phone"] = ""
    if len(rows) > 15:
        rows[15]["email"] = ""
    if len(rows) > 21:
        rows[21]["phone"] = "   "

    return pd.DataFrame(rows)


def save_customers(path: str | Path = DEFAULT_OUTPUT, num_rows: int = 200, seed: int = 42) -> pd.DataFrame:
    path = Path(path)
    df = generate_customers(num_rows=num_rows, seed=seed)
    df.to_csv(path, index=False)
    return df


if __name__ == "__main__":
    save_customers()
    print(f"Generated {len(pd.read_csv(DEFAULT_OUTPUT))} rows in {DEFAULT_OUTPUT}")
