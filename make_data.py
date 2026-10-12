from data_generator import save_customers


if __name__ == "__main__":
    df = save_customers()
    print(f"Generated {len(df)} customer rows in customers.csv")
