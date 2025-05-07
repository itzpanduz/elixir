import csv
from datetime import datetime, time
import pandas as pd

# === Config ===
SHIFT_CUTOFF = time(18, 30)  # 6:30 PM
INPUT_FILES = {
    'Monroe': 'data/m_tip_3_31.csv',
    'Buford': 'data/b_tip_3_31.csv'
}
EXPORT_PREFIX = 'data/processed_tips_'


# === CSV Reading and Cleaning ===
def read_and_parse_tips(csv_path):
    rows = []
    with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["REF#"] != "TOTAL":
                rows.append(row)
    return rows


def enrich_tip_rows(rows):
    for row in rows:
        parsed_dt = datetime.strptime(row["DATE/TIME"], '%m-%d-%y %I:%M %p')
        row["day"] = parsed_dt.strftime("%A")
        row["date"] = parsed_dt.strftime("%m/%d/%Y")
        row["time"] = parsed_dt.strftime("%H:%M")
        row["12_time"] = parsed_dt.strftime("%I:%M %p")
        row["iso_dt"] = parsed_dt.isoformat()
        row["shift"] = "B" if parsed_dt.time() > SHIFT_CUTOFF else "A"

        row["SHIFTNDATE"] = f"{parsed_dt.strftime('YYY-MM-DD')}_{row['shift']}"
    return rows


# === Main Processing Function ===
def get_clean_tip_data():
    rows_m = enrich_tip_rows(read_and_parse_tips(INPUT_FILES['Monroe']))
    rows_b = enrich_tip_rows(read_and_parse_tips(INPUT_FILES['Buford']))
    combined_rows = rows_m + rows_b

    for row in combined_rows:
        tip = row.get("TIP")
        row["TIP"] = tip.replace("$", "").strip()
        row["TIP"] = float(row["TIP"])
        # convert date to datetime
        date = row.get("date")
        row["date"] = datetime.strptime(date, "%m/%d/%Y")

    df = pd.DataFrame(combined_rows)
    return df

def process_tip_data():
    df = get_clean_tip_data()

    df = df.groupby(['date', 'shift']).agg(
        total_tips=('TIP', 'sum'),
        # total_a_tips=('TIP', lambda x: calculate_tips_by_shift(tips_df[tips_df['date'] == x.name], 'A')),
        # total_b_tips=('TIP', lambda x: calculate_tips_by_shift(tips_df[tips_df['date'] == x.name], 'B'))
    )
    print(df)
    # now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    # output_path = f"{EXPORT_PREFIX}{now}.xlsx"
    #
    # df.to_excel(output_path, index=False)
    # print(f"✅ Processed tip data written to: {output_path}")

# === Entry Point ===
if __name__ == "__main__":
    process_tip_data()
