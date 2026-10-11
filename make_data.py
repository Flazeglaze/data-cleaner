import random
import pandas as pd
from faker import Faker

fake = Faker("en_NZ")
rows = [{"name": fake.name(), "email": fake.email(), "phone": fake.phone_number()}
        for _ in range(200)]

# add duplicates with small typos, and some bad records
for r in random.sample(rows, 20):
    rows.append({**r, "name": r["name"].replace("a", "e", 1)})
rows[5]["email"] = "not-an-email"
rows[9]["phone"] = ""

pd.DataFrame(rows).to_csv("customers.csv", index=False) 