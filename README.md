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

The cleaning script reads a CSV with `name`, `email`, and `phone` columns. It trims whitespace in text columns, converts blank text to missing values, lowercases email addresses, validates phone numbers against New Zealand's numbering plan, and formats valid numbers as E.164 (for example, `+64212345678`). It does not guess at corrections.

### Try it with the sample data

Generate sample data first if you do not already have `customers.csv`:

```bash
python make_data.py
python check_data.py
python clean_data.py
```

The script reads `customers.csv` and writes two files:

- `customers_cleaned.csv` - rows with an email present and a valid NZ phone number, with phones formatted as E.164 and other columns preserved. Invalid-email and duplicate-email rows are flagged for review but kept in the cleaned output.
- `customers_review.csv` - rows needing attention, with a `source_row` number and `quality_issues` field identifying missing or invalid emails, missing or invalid NZ phone numbers, and duplicate valid emails. Rows with missing/invalid email or phone are excluded from the cleaned output but kept here.

The input file is never overwritten. Review `customers_review.csv` and decide how to address those records yourself.

### Clean your own data

You can either copy your CSV to the project folder and name it `customers.csv`, or pass its path directly. For example:

```bash
python clean_data.py --input path/to/my_customers.csv --output path/to/normalized.csv --review-output path/to/review.csv
```

On Windows, use Windows-style paths, for example `python clean_data.py --input "C:\Data\my_customers.csv" --output "C:\Data\normalized.csv" --review-output "C:\Data\review.csv"`.

Do not run `python make_data.py` when `customers.csv` contains your own data: it replaces that file with generated sample data. Keep a backup of important input data.

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
