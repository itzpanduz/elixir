from csv import writer
import json
from numpy._core.numeric import outer
from numpy._typing import _BoolLike_co
import xlsxwriter
from xlsxwriter.worksheet import Worksheet

from elixir.operations import ElixirOperations
import pandas as pd
from zoneinfo import ZoneInfo
eastern = ZoneInfo("America/New_York")


buford_ops = ElixirOperations(location="Buford")
monroe_ops = ElixirOperations(location="Monroe")

all_tips = buford_ops.tips + monroe_ops.tips
all_shifts = buford_ops.shifts + monroe_ops.shifts



users_during_shifts = buford_ops.get_workers()
print(users_during_shifts)

# tips_df = pd.DataFrame(all_tips)
# shifts_df = pd.DataFrame(all_shifts)

# # Convert 'start_date' and 'date_time' to datetime objects in EST if they aren't already
# shifts_df['start_date'] = pd.to_datetime(shifts_df['start_date']).dt.tz_convert(eastern)
# shifts_df['end_date'] = pd.to_datetime(shifts_df['end_date']).dt.tz_convert(eastern)
# tips_df['tip_date'] = pd.to_datetime(tips_df['tip_date']).dt.tz_convert(eastern)

# # create column for shift length in min using the end date and start date columns
# shifts_df['minutes_worked'] = (shifts_df['end_date'] - shifts_df['start_date']).dt.total_seconds() / 60
# # create column for shift length in hours using the end date and start date columns
# shifts_df['hours_worked'] = round(shifts_df['minutes_worked'] / 60 , 2)


# # Create a 'date' column in both DataFrames with just the year, month, and day
# shifts_df['date'] = shifts_df['start_date'].dt.date
# tips_df['date'] = tips_df['tip_date'].dt.date

# # Assuming each shift and tip record has a 'location' attribute
# # we want sums of the tip_amounts by date and location for tips
# daily_tips_df = tips_df.groupby(['date', 'location', 'shift_type']).agg({'tip_amount': 'sum'}).reset_index() # reset index to make location a column

# # we want sum of the hours by date and location for shifts, we need to get
# daily_shifts_df = shifts_df.groupby(['date', 'location', 'shift_type']).agg({'minutes_worked': 'sum'}).reset_index() # reset index to make location a column

# # Merge the two dataframes on date and location
# daily_rates_df = pd.merge(daily_shifts_df, daily_tips_df, on=['date', 'location', 'shift_type'], how='left')

# # Calculate the rate. Handle potential division by zero.
# daily_rates_df['hourly_tip_rate'] = daily_rates_df.apply(lambda row: row['tip_amount'] / (row['minutes_worked']/60) if row['minutes_worked'] > 0 else 0, axis=1)


# # Strip timezone before writing to Excel because Excel is old and grump an dcan't handle timeszones wihtout throwing a tantrum.
# #
# shifts_df['start_date'] = shifts_df['start_date'].dt.tz_localize(None)
# shifts_df['end_date'] = shifts_df['end_date'].dt.tz_localize(None)
# tips_df['tip_date'] = tips_df['tip_date'].dt.tz_localize(None)

# # Write test to Excel to validate
# output_file = 'test_functions.xlsx'

# with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
#     shifts_df.to_excel(writer, sheet_name='shifts-331', index=False, header=True)
#     tips_df.to_excel(writer, sheet_name='tips-331', index=False, header=True)
#     daily_rates_df.to_excel(writer, sheet_name='rates-331', index=False, header=True)
