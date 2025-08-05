import pandas as pd
from pathlib import Path

# Define the folder containing the Excel files
data_folder = Path("SMS_data")
all_files = sorted(data_folder.glob("2024-*.xlsx"))

# List to hold all dataframes
dfs = []

for file in all_files:
    # Extract the month from the filename (e.g., "2024-01.xlsx" → "2024-01")
    month = file.stem  # gets filename without extension

    # Read Excel
    df = pd.read_excel(file)

    # Drop the 'SMS content' column
    df = df.drop(columns=["SMS content"])

    # Add the month column
    df["month"] = month

    # Rename columns: replace spaces with underscores
    df.columns = [col.strip().replace(" ", "_") for col in df.columns]

    dfs.append(df)

# Concatenate all dataframes
final_df = pd.concat(dfs, ignore_index=True)

# Save to Parquet
final_df.to_parquet("all_sms_data.parquet", index=False)

print("✅ Combined data saved as 'all_sms_data.parquet'")
