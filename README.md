# data-cleaner

A small sample project for generating and checking customer data quality.

## Generate demo data

```bash
python make_data.py
```

This creates `customers.csv` with realistic customer records, including a few intentionally bad rows.

## Check the data quality

```bash
python check_data.py
```

The validation script reports:
- invalid email addresses
- missing phone numbers
- duplicate email records
- a summary quality report

## Validation tests

```bash
python -m unittest discover -s tests -v
```
