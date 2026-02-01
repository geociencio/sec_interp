"""Dataset validation script for Data Science skill."""

import argparse
import pandas as pd
from pathlib import Path


def validate_dataset(file_path: str):
    """Perform a sanity check on a dataset.

    Args:
        file_path: Path to the CSV/Excel file.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File {file_path} not found.")
        return

    # Load data (assuming CSV for this example)
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    print(f"\n--- Validation Report: {path.name} ---")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

    # Check nulls
    nulls = df.isnull().sum()
    if nulls.any():
        print("\nNull values detected:")
        print(nulls[nulls > 0])
    else:
        print("\nNo null values detected.")

    # Check duplicates
    dupes = df.duplicated().sum()
    print(f"\nDuplicate rows: {dupes}")

    # Data types summary
    print("\nData Types:")
    print(df.dtypes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sanity check for datasets.")
    parser.add_argument("--input", required=True, help="Path to the dataset file")
    args = parser.parse_args()
    validate_dataset(args.input)
