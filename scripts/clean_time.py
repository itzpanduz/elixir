import pandas as pd
from datetime import datetime, timedelta
import os


# === Config ===
SHIFT_BOUNDARY = datetime.strptime("6:30 PM", '%I:%M %p').time()
TIME_FORMAT = '%m-%d-%y %I:%M %p'
INPUT_FILES = {
    'Monroe': 'data/m_time_33125.csv',
    'Buford': 'data/b_time_33125.csv'
}
OUTPUT_FILE = 'data/processed_shifts.xlsx'

# === Shift Calculations ===
def calculate_shift_a(row, shift_boundary):
    if pd.isna(row['CLOCKED IN']) or pd.isna(row['CLOCKED OUT']):
        return 0

    time_in = row['CLOCKED IN'].time()
    time_out = row['CLOCKED OUT'].time()

    if row['CLOCKED IN'].date() == row['CLOCKED OUT'].date():
        if time_in < shift_boundary:
            shift_a_end = min(shift_boundary, time_out)
            shift_a = (datetime.combine(row['CLOCKED IN'].date(), shift_a_end) - row['CLOCKED IN']).seconds / 3600
            return round(shift_a, 2)
    else:
        if time_in >= shift_boundary:
            return 0
        else:
            shift_a_end = datetime.combine(row['CLOCKED IN'].date(), shift_boundary)
            shift_a = (shift_a_end - row['CLOCKED IN']).seconds / 3600
            return round(shift_a, 2)
    return 0


def calculate_shift_b(row, shift_boundary):
    if pd.isna(row['CLOCKED IN']) or pd.isna(row['CLOCKED OUT']):
        return 0

    time_out = row['CLOCKED OUT'].time()
    time_in = row['CLOCKED IN'].time()

    if row['CLOCKED IN'].date() != row['CLOCKED OUT'].date():
        midnight = datetime.combine(row['CLOCKED IN'].date(), datetime.min.time()) + timedelta(days=1)
        shift_b_start = max(shift_boundary, time_in)
        shift_b = (midnight - datetime.combine(row['CLOCKED IN'].date(), shift_b_start)).seconds / 3600
        shift_b += (row['CLOCKED OUT'] - midnight).seconds / 3600
        return round(shift_b, 2)
    else:
        if time_out > shift_boundary:
            shift_b_start = max(shift_boundary, time_in)
            shift_b = (datetime.combine(row['CLOCKED OUT'].date(), time_out) - datetime.combine(
                row['CLOCKED IN'].date(), shift_b_start)).seconds / 3600
            return round(shift_b, 2)
        return 0


# === Main Processing ===
def process_shifts(df):
    df['date'] = df['CLOCKED IN'].dt.strftime("%m/%d/%Y")
    df['time_in'] = df['CLOCKED IN'].dt.strftime("%I:%M %p")
    df['time_out'] = df['CLOCKED OUT'].dt.strftime("%I:%M %p")
    df['shift_a'] = df.apply(calculate_shift_a, axis=1, args=(SHIFT_BOUNDARY,))
    df['shift_b'] = df.apply(calculate_shift_b, axis=1, args=(SHIFT_BOUNDARY,))
    # we want create a new  row for each shift. the shift_a and shift_b columns will be the duration of the shift. this will go into the time_by_shift_df

    return df


def read_and_prepare(file_path, location):
    df = pd.read_csv(file_path)

    # Remove rows where FIRST NAME ↑ is "Total" or blank
    df = df[df['FIRST NAME ↑'].notna() & (df['FIRST NAME ↑'] != "Total")]

    # Drop rows missing time info
    df = df.dropna(subset=['CLOCKED IN', 'CLOCKED OUT'])

    try:
        df['CLOCKED IN'] = pd.to_datetime(df['CLOCKED IN'], format=TIME_FORMAT)
        df['CLOCKED OUT'] = pd.to_datetime(df['CLOCKED OUT'], format=TIME_FORMAT)
    except Exception as e:
        print(f"Error parsing dates in {location} file: {e}")
        raise

    df['location'] = location
    return df


def get_clean_shift_data():
    # Load and clean both dataframes
    df_monroe = read_and_prepare(INPUT_FILES['Monroe'], 'Monroe')
    df_buford = read_and_prepare(INPUT_FILES['Buford'], 'Buford')

    # Combine and process
    df_combined = pd.concat([df_monroe, df_buford], ignore_index=True)
    df_processed = process_shifts(df_combined)

    return df_processed


def main():
    df = get_clean_shift_data()
    df.to_excel(OUTPUT_FILE,index=False)
    print(f"✅ Processed shift data written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
