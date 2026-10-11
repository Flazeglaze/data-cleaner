import pandas as pd

df = pd.read_csv("customers.csv")
#print(df.head())
#print(df.shape)
#print(df.dtypes) 

phone = pd.Series(df["phone"])
#print(df[df["phone"].isna()]) # prints only rows with NaN values in the phone column

valid_emails = df["email"].str.contains("@") #prints a boolean series indicating whether each email address is valid (contains "@")   
invalid_emails = df[~df["email"].str.contains("@")]  # prints only rows with invalid email addresses
#print(invalid_emails)

combined = pd.concat([invalid_emails, df[df["phone"].isna()]], ignore_index=True) # combines the invalid email and missing phone records into a single DataFrame
print(combined) # prints the combined DataFrame
print(f"Number of rows with invalid emails or missing phone numbers: {len(combined)}")