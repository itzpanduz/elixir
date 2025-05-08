# 🧪 Elixir Payroll + Tip Allocation Pipeline

This project parses shift and tip CSV exports from the Quantic system, assigns employees to Alpha/Bravo shifts, and calculates wages and allocated tips based on predefined hourly rates and tip eligibility. Final outputs include detailed payroll calculations and summary reports.

---

## 📁 Project Structure

elixir/
├── data/
│ ├── buford/
│ │ ├── time/ # Quantic shift CSVs for Buford
│ │ └── tips/ # Quantic tip CSVs for Buford
│ ├── monroe/
│ │ ├── time/ # Quantic shift CSVs for Monroe
│ │ └── tips/ # Quantic tip CSVs for Monroe
│ └── ... # Historical validation files
│
├── elixir/
│ ├── operations/ # Parsing + payroll logic
│ │ ├── payroll_utils.py # Payroll and compensation calculations
│ │ ├── shift_parser.py # Parses raw shifts
│ │ ├── tip_parser.py # Parses raw tips
│ │ └── work_team.py # Splits workday into shift types
│ ├── quantic/ # Quantic CSV ingestion + datetime formatting
│ ├── reports/ # Aggregated summary DataFrames
│ │ └── summary_dataframes.py
│ ├── outputs/ # Final output files (Excel)
│ └── tests/ # Validation scripts + test files
│
├── scripts/ # CSV cleanup tools
│ ├── clean_time.py
│ ├── clean_tips.py
│ └── calc_tipout.py
│
├── main.py # Entrypoint for running a payroll period
├── README.md # You’re looking at it

---

## 📊 What This Does

1. Loads `.csv` data from the `data/` directory
2. Parses and standardizes timestamps using EST
3. Assigns Alpha/Bravo shift types using `work_team.py`
4. Merges hourly tip rates with employee shift data
5. Calculates:
   - **Wages** using hardcoded employee hourly rates
   - **Tips** using hourly tip rate x hours worked
   - **Total compensation**
6. Outputs:
   - Detailed payroll sheet per employee per shift, with added `clock_in` and `clock_out` columns displaying the start and end times of each shift.
   - Aggregated summary by employee
   - Source summary DataFrames used in calculation

---

## 🧠 How to Use

### 🛠 Run the Pipeline

```bash
python main.py
```

This will:

Parse all files in data/{site}/time/ and data/{site}/tips/
Generate summary and payroll outputs
Save a report to /elixir/outputs/
📤 Output File Example
Filename: payroll_outputs_20250508.xlsx
Sheets:
payroll_calc – shift-level earnings, with added `clock_in` and `clock_out` columns displaying the start and end times in `HH:MM AM/PM` format.
payroll_summary – totals by employee
shifts_summary, tips_summary, rates_summary – core DataFrames

🧾 Adding New Data

Drop CSV files into one of:
data/buford/time/
data/buford/tips/
data/monroe/time/
data/monroe/tips/

Naming convention (optional but helpful):
btime_422.csv → Buford shifts for Apr 22
mtip_422.csv → Monroe tips for Apr 22

Run the pipeline again: python main.py

🛠️ Future Improvements

Date range filtering (pay period selection)
Shift anomaly flags (e.g., missing clock-outs, excessive duration)
Streamlit dashboard for summaries
Configurable employee comp table
