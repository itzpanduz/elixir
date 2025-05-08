# summary_dataframes.py

import pandas as pd
from elixir.operations import ElixirOperations
from zoneinfo import ZoneInfo

eastern = ZoneInfo("America/New_York")

def get_summary_dataframes():
    buford_ops = ElixirOperations(location="Buford")
    monroe_ops = ElixirOperations(location="Monroe")

    all_tips = buford_ops.tips + monroe_ops.tips
    all_shifts = buford_ops.shifts + monroe_ops.shifts

    tips_df = pd.DataFrame(all_tips)
    shifts_df = pd.DataFrame(all_shifts)

    shifts_df['start_date'] = pd.to_datetime(shifts_df['start_date']).dt.tz_convert(eastern)
    shifts_df['end_date'] = pd.to_datetime(shifts_df['end_date']).dt.tz_convert(eastern)
    tips_df['tip_date'] = pd.to_datetime(tips_df['tip_date']).dt.tz_convert(eastern)

    shifts_df['minutes_worked'] = (shifts_df['end_date'] - shifts_df['start_date']).dt.total_seconds() / 60
    shifts_df['hours_worked'] = round(shifts_df['minutes_worked'] / 60, 2)

    shifts_df['date'] = shifts_df['start_date'].dt.date
    tips_df['date'] = tips_df['tip_date'].dt.date

    daily_tips_df = tips_df.groupby(['date', 'location', 'shift_type']).agg({'tip_amount': 'sum'}).reset_index()
    daily_shifts_df = shifts_df.groupby(['date', 'location', 'shift_type']).agg({'minutes_worked': 'sum'}).reset_index()

    daily_rates_df = pd.merge(daily_shifts_df, daily_tips_df, on=['date', 'location', 'shift_type'], how='left')
    daily_rates_df['hourly_tip_rate'] = daily_rates_df.apply(
        lambda row: row['tip_amount'] / (row['minutes_worked']/60) if row['minutes_worked'] > 0 else 0, axis=1
    )

    # Strip tz info before returning (or leave in if downstream logic needs it)
    shifts_df['start_date'] = shifts_df['start_date'].dt.tz_localize(None)
    shifts_df['end_date'] = shifts_df['end_date'].dt.tz_localize(None)
    tips_df['tip_date'] = tips_df['tip_date'].dt.tz_localize(None)

    return shifts_df, tips_df, daily_rates_df
