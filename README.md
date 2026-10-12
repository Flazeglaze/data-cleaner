# Data Cleaner

A small Python project for generating sample customer data and checking it for common data-quality issues. The generator creates synthetic data with a few intentional problems so you can try the validator safely.

## Requirements

- Python 3.10 or newer
- pip

## Set up

Open a terminal in the project folder, then create and activate a virtual environment.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, you can install and run the tools without activating the environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe make_data.py
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Generate sample data

```bash
python make_data.py
```

This writes `customers.csv` in the current project folder. By default, it contains 200 generated customers plus 20 extra records with repeated email addresses, and some intentionally invalid or missing contact details. Running the generator again overwrites the existing CSV.

## Check data quality

After generating the CSV, run:

```bash
python check_data.py
```

The report lists:

- Total number of records
- Invalid email addresses
- Missing phone numbers (including empty or whitespace-only values)
- Records with duplicate email addresses
- A `clean_rows` count, calculated as total rows minus invalid-email and missing-phone counts; duplicate rows are not subtracted

Email checks trim whitespace, ignore case, and apply a basic format check. Duplicate detection is based on normalized email addresses, and reports every row in a duplicate group. The validator reports issues; it does not remove or repair records.

The checker expects `customers.csv` in the current working directory and requires the columns `name`, `email`, and `phone`. To check your own data, put a CSV with those columns in the project folder and name it `customers.csv` (back up your data first, as generating sample data overwrites that file).

## Clean and review data

To normalize the data while preserving all records, run:

```bash
python clean_data.py
```

The script reads `customers.csv` and writes two new files:

- `customers_cleaned.csv` — all rows, with surrounding whitespace trimmed, blank text converted to missing values, and email addresses lowercased. Other columns are preserved.
- `customers_review.csv` — only rows needing attention, with a `source_row` number and `quality_issues` field identifying invalid emails, missing phones, and duplicate valid emails.

The input file is never overwritten, and flagged rows are not removed from the cleaned output. Review the flagged records and make judgment calls manually.

You can choose different paths:

```bash
python clean_data.py --input my_customers.csv --output normalized.csv --review-output review.csv
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Project files

- `make_data.py` — entry point for creating the sample CSV
- `data_generator.py` — reusable sample-data generation functions
- `check_data.py` — command-line data-quality report
- `clean_data.py` — writes normalized data and a separate review file without dropping rows
- `data_validator.py` — reusable validation and reporting functions
- `tests/` — unit tests for generation and validation
