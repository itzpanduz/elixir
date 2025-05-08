import pandas as pd
from zoneinfo import ZoneInfo
from elixir.operations import ElixirOperations
from elixir.reports.summary_dataframes import get_summary_dataframes

# --- Constants ---
eastern = ZoneInfo("America/New_York")

# Static employee compensation data (for now hardcoded)
EMPLOYEE_COMPENSATION = {
    "Chad":      {"rate": 0.00, "tips": False},
    "Colleen":   {"rate": 0.00, "tips": False},
    "Ryan":      {"rate": 0.00, "tips": False},
    "Alyssa":    {"rate": 0.00, "tips": False},
    "Bennet":    {"rate": 12.00, "tips": True},
    "Joanna":    {"rate": 12.00, "tips": True},
    "Kathryn":   {"rate": 12.00, "tips": True},
    "Melanie":   {"rate": 12.00, "tips": True},
    "Nate":      {"rate": 15.00, "tips": True},
    "Pam":       {"rate": 12.00, "tips": True},
    "Patrick":   {"rate": 12.00, "tips": True},
    "Samantha":  {"rate": 12.00, "tips": True},
    "Sarah Beth":{"rate": 15.00, "tips": True},
    "Caroline":  {"rate": 12.00, "tips": True},
    "Lauren":    {"rate": 12.00, "tips": True},
    "Laura":     {"rate": 12.00, "tips": True},
    "Becca":     {"rate": 12.00, "tips": True},
    "Keri":      {"rate": 12.00, "tips": True},
    "Haley":     {"rate": 12.00, "tips": True},
    "Vanessa":   {"rate": 12.00, "tips": True},
}

def get_payroll_calculations():
    # Load parsed summary DataFrames
    shifts_df, tips_df, daily_rates_df = get_summary_dataframes()

    # Convert datetime and extract date
    datetime_cols = ['start_date', 'end_date']
    for col in datetime_cols:
        shifts_df[col] = pd.to_datetime(shifts_df[col])
    shifts_df['clock_in'] = shifts_df['start_date'].dt.strftime('%I:%M %p')
    shifts_df['clock_out'] = shifts_df['end_date'].dt.strftime('%I:%M %p')
    shifts_df['date'] = shifts_df['start_date'].dt.date

    # Calculate hours worked per shift
    shifts_df['hours_worked'] = (shifts_df['end_date'] - shifts_df['start_date']).dt.total_seconds() / 3600

    # Add wage rate and tip eligibility
    shifts_df['wage_rate'] = shifts_df['first_name'].map(lambda x: EMPLOYEE_COMPENSATION.get(x, {}).get('rate', 0))
    shifts_df['tips_eligible'] = shifts_df['first_name'].map(lambda x: EMPLOYEE_COMPENSATION.get(x, {}).get('tips', False))

    # Calculate wages
    shifts_df['wages'] = shifts_df['hours_worked'] * shifts_df['wage_rate']

    # Merge in tip rate
    shifts_df = pd.merge(
        shifts_df,
        daily_rates_df[['date', 'location', 'shift_type', 'hourly_tip_rate']],
        on=['date', 'location', 'shift_type'],
        how='left'
    )

    # Calculate shift_tip
    shifts_df['shift_tip'] = shifts_df.apply(
        lambda row: row['hours_worked'] * row['hourly_tip_rate'] if row['tips_eligible'] else 0,
        axis=1
    )

    # Calculate total compensation
    shifts_df['total_comp'] = shifts_df['wages'] + shifts_df['shift_tip']

    # Payroll calculation detail
    payroll_calc_df = shifts_df[[
        'first_name', 'last_name', 'date','clock_in','clock_out', 'location', 'shift_type',
        'hours_worked', 'wage_rate', 'wages', 'shift_tip', 'total_comp'
    ]]

    # Payroll summary by employee
    payroll_summary_df = payroll_calc_df.groupby(['first_name', 'last_name']).agg(
        total_hours=('hours_worked', 'sum'),
        total_wages=('wages', 'sum'),
        total_tips=('shift_tip', 'sum'),
        total_comp=('total_comp', 'sum')
    ).reset_index()

    return payroll_calc_df, payroll_summary_df

# --- Run and display results ---
if __name__ == "__main__":
    payroll_calc_df, payroll_summary_df = get_payroll_calculations()

    print("\n--- Payroll Calculation Detail ---")
    print(payroll_calc_df.head())

    print("\n--- Payroll Summary ---")
    print(payroll_summary_df.head())
