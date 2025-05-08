# elixir/main.py

import pandas as pd
from datetime import datetime
from elixir.operations.payroll_utils import get_payroll_calculations
from elixir.reports.summary_dataframes import get_summary_dataframes
import os

# Create output folder if it doesn't exist
output_dir = os.path.join("elixir", "outputs")
os.makedirs(output_dir, exist_ok=True)

# Get today's date for filename
today_str = datetime.today().strftime("%Y%m%d")
output_path = os.path.join(output_dir, f"payroll_outputs_{today_str}.xlsx")

# Get payroll and summary data
payroll_calc_df, payroll_summary_df = get_payroll_calculations()
shifts_df, tips_df, daily_rates_df = get_summary_dataframes()

# Write to Excel
with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
    payroll_calc_df.to_excel(writer, sheet_name="payroll_detail", index=False)
    payroll_summary_df.to_excel(writer, sheet_name="payroll_summary", index=False)
    shifts_df.to_excel(writer, sheet_name="shifts", index=False)
    tips_df.to_excel(writer, sheet_name="tips", index=False)
    daily_rates_df.to_excel(writer, sheet_name="daily_rates", index=False)

print(f"✅ Payroll export complete: {output_path}")
