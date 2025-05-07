from typing import TypedDict, List, Dict
from datetime import datetime
from elixir.operations.work_team import WorkTeamDay, TeamType
from dateutil import parser  # For more robust date parsing
from elixir.quantic import QuanticTipData  # Import the type
from zoneinfo import ZoneInfo
eastern = ZoneInfo("America/New_York")

class ElixirTip(TypedDict):
    tip_date: datetime
    tip_amount: float
    shift_type: str  # "a" or "b"
    location: str


class ElixirTipParser:
    def __init__(self, quantic_tip_data: List[QuanticTipData], location: str):
        if not location:
            raise ValueError("Location is required")
        self.location = location
        self.quantic_tip_data = quantic_tip_data  # Changed from csv_file_path
        self.parsed_tips: List[ElixirTip] = []
        self.parse_tips()

    def _is_total_row(self, row: QuanticTipData) -> bool:
        """ Checks if row a total row used to calculate totals for dataset"""
        if isinstance(row.get('ref'), str) and "TOTAL" in row.get('ref'):
            return True
        return False



    def _extract_tip_amount(self, tip_str: str) -> float:
        try:
            # Remove any non-numeric characters and convert to float
            return float(tip_str.replace('$', '').strip())
        except (ValueError, TypeError):
            print(f"Warning: Could not parse tip amount: {tip_str}. Skipping.")
            return 0.0  # Or handle the error as appropriate

    def parse_tips(self):
        parsed_tips: List[ElixirTip] = []

        if not self.quantic_tip_data:  # Check if the input data is empty
            return []

        for tip_data in self.quantic_tip_data:  # Iterate through QuanticTipData objects

            # Skip rows that have TOTAL in first col
            if self._is_total_row(tip_data):
                continue

            date_time_str = tip_data.get("date_time")
            if not date_time_str:
                continue
            try:
                tip_dt = datetime.fromisoformat(date_time_str)
                if tip_dt.tzinfo is None:
                    tip_dt = tip_dt.replace(tzinfo=eastern)
                else:
                    tip_dt = tip_dt.astimezone(eastern)
            except ValueError:
                print(f"Warning: Invalid ISO date string: {date_time_str}")
                continue


            employee_name = str(tip_data.get('employee_name', '')).strip()
            tip_amount_str = str(tip_data.get('tip', ''))
            tip_amount = self._extract_tip_amount(tip_amount_str)


            # Determine the shift type (a or b) using WorkTeamDay
            tip_team_type = WorkTeamDay.get_team_by_time(tip_dt)
            shift_type = None
            if tip_team_type == TeamType.a:
                shift_type = "a"
            if tip_team_type == TeamType.b:
                shift_type = "b"

            # Only build the ElixirTip if tip_dt and shift_type are valid
            if shift_type:
                tip: ElixirTip = {
                    "tip_date": tip_dt,
                    "tip_amount": tip_amount,
                    "shift_type": shift_type,
                    "location": self.location,
                }
                parsed_tips.append(tip)

        self.parsed_tips = parsed_tips
        return self.parsed_tips

    def get_tips_by_date(self, date: datetime) -> List[ElixirTip]:
        """Returns a list of tips for a specific date."""
        tips_for_date: List[ElixirTip] = []
        for tip in self.parsed_tips:
            if tip.get("tip_date").date() == date.date():  # Compare dates only
                tips_for_date.append(tip)
        return tips_for_date

    def get_tips_by_shift(self, shift_type: str) -> List[ElixirTip]:
        """Returns a list of tips for a specific shift type ('a' or 'b')."""
        if shift_type not in ("a", "b"):
            raise ValueError("Invalid shift type.  Must be 'a' or 'b'.")

        tips_for_shift: List[ElixirTip] = []
        for tip in self.parsed_tips:
            if tip["shift_type"] == shift_type:
                tips_for_shift.append(tip)
        return tips_for_shift
