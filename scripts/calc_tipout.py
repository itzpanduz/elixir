from scripts.clean_time import get_clean_shift_data
from scripts.clean_tips import get_clean_tip_data
import pandas as pd
import os
import glob
from datetime import datetime

# === Configuration ===
TIP_DATA_DIR = "data/"
SHIFT_DATA_FILE = "data/processed_shifts.xlsx"
OUTPUT_FILE = "data/tip_calculations.xlsx"

# === Helper Functions ===
def find_latest_tip_file(directory):
    """Finds the most recent processed tip data file."""
    search_pattern = os.path.join(directory, "processed_tips_*.xlsx")
    list_of_files = glob.glob(search_pattern)
    if not list_of_files:
        raise FileNotFoundError(f"No tip data files found in {directory}")
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


# === Main Calculation Function ===
def calculate_tipout():
    try:
        # 1. Load Data using the imported functions
        tips_df = get_clean_tip_data()
        shifts_df = get_clean_shift_data()


        # # 2. Data Cleaning/Preprocessing (Check for NaN values and potential data type conversion)
        # if tips_df.isnull().any().any():
        #     print("Warning: Missing values found in tip data.  Investigate.")
        # if shifts_df.drop(columns=["LAST NAME ↑"], errors="ignore").isnull().any().any():
        #         print("Warning: Missing values found in shift data (excluding LAST NAME). Investigate.")


        # # Ensure 'TIP' is numeric (handle potential errors)
        # try:
        #     # regex remove the $ from the TIP column
        #     tips_df['TIP_clean'] = tips_df['TIP'].str.replace(r'^\$', '', regex=True)

        #     # convert TIP_clean to number
        #     tips_df['TIP_clean'] = pd.to_numeric(tips_df['TIP_clean'], errors='coerce')

        # except KeyError:
        #     print("Warning: 'TIP' column not found in tip data. Check column names.")
        #     return  # Exit if critical column is missing
        # except ValueError as e:
        #     print(f"Error converting 'TIP' to numeric: {e}")
        #     return  # Exit if conversion fails


        # # 3. Data Cleaning and formatting the date columns for the merge
        tips_df['date'] = tips_df['date'].dt.strftime('%m/%d/%Y')
        shifts_df['date'] = pd.to_datetime(shifts_df['date']).dt.strftime('%m/%d/%Y')
        print(tips_df.dtypes)


        # 4. Calculate total hours, shift_a, and shift_b by date in shifts_df
        shifts_grouped = shifts_df.groupby('date').agg(
            total_hours=('HOURS', 'sum'),  # Assuming 'HOURS' is the column name for shift duration
            total_shift_a=('shift_a', 'sum'),
            total_shift_b=('shift_b', 'sum')
        ).reset_index()

        print(shifts_grouped)

        # 5. Calculate total tips, total_a_tips, and total_b_tips for each day in tips_df
        #def calculate_tips_by_shift(group, shift_type):
        """Helper function to calculate total tips for a specific shift type."""
            #return group[group['shift'] == shift_type]['TIP'].sum()

        tips_grouped = tips_df.groupby(['date', 'shift']).agg(
            total_tips=('TIP', 'sum'),
            total_a_tips=('TIP', lambda x: calculate_tips_by_shift(tips_df[tips_df['date'] == x.name], 'A')),
            total_b_tips=('TIP', lambda x: calculate_tips_by_shift(tips_df[tips_df['date'] == x.name], 'B'))
        ).reset_index()

        print(tips_grouped)

        # 6. Merge the aggregated dataframes
        merged_df = pd.merge(shifts_grouped, tips_grouped, on='date', how='outer')

        # 7. Calculate Tip Rates (Handle potential division by zero)
        merged_df['tip_rate_a'] = merged_df.apply(
            lambda row: row['total_a_tips'] / row['total_shift_a'] if row['total_shift_a'] > 0 else 0, axis=1
        )
        merged_df['tip_rate_b'] = merged_df.apply(
            lambda row: row['total_b_tips'] / row['total_shift_b'] if row['total_shift_b'] > 0 else 0, axis=1
        )

        # 8. Output Results
        # merged_df.to_excel(OUTPUT_FILE, index=False)
        print(merged_df)
        print(f"✅ Tip calculations written to: {OUTPUT_FILE}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# === Entry Point ===
if __name__ == "__main__":
    calculate_tipout()
