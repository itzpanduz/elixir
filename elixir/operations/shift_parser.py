from typing import TypedDict
from elixir.quantic import QunaticShiftData
from datetime import datetime
from elixir.operations.work_team import WorkTeamDay
import pytz
# elixir shift class to ingest the shift data from the quantic system and parse it
# we will use the data to create the ExlixirShift dict
from zoneinfo import ZoneInfo
eastern = ZoneInfo("America/New_York")


class ElixirShift(TypedDict):
    shift_type: str # this can only be alpha or bravo
    start_date: datetime
    end_date: datetime
    first_name: str
    last_name: str
    shift_status: str
    location: str

# maximum lenght of shift allowed before we throw an error
SHIFT_LENGTH_MAX = 17


# exception thrown when length of shift is greater than SHIFT_LENGTH_MAX
class ElixirShiftLengthError(Exception):
    def __init__(self, user_name: str, shift_start:datetime, shift_end:datetime , shift_location: str):
        shift_length_hours = (shift_end - shift_start).total_seconds() / 3600
        shift_start_date = shift_start.strftime("%m/%d/%y")
        formatted_message = f"User {user_name} started a shift at {shift_start_date} with a total shift length of {shift_length_hours} hours at {shift_location}"
        self.message = formatted_message
        super().__init__(self.message)


class ElixirShiftParser:
    def __init__(self, qunatic_shift_data: list[QunaticShiftData], location: str):
        if not location:
            raise Exception("Location is required")
        self.location = location
        self.shift_data = qunatic_shift_data
        self.parsed_shifts: list[ElixirShift] = []
        self.parse_shifts()


    def _calculate_shift_length(self, clocked_in_str: str, clocked_out_str: str) -> int:
             """Calculates the shift length in minutes."""
             try:
                clocked_in = datetime.strptime(clocked_in_str, "%m-%d-%y %I:%M %p")
                clocked_out = datetime.strptime(clocked_out_str, "%m-%d-%y %I:%M %p")
                shift_length_minutes = (clocked_out - clocked_in).total_seconds() / 60
                return int(shift_length_minutes)
             except ValueError:
                 print("Error: Invalid date/time format. Skipping shift length calculation.")
                 return 0  # Or handle the error appropriately, e.g., raise an exception

    def _is_total_row(self, shift: QunaticShiftData) -> bool:
        """Checks if a shift row is a total row.
            Total rows are aggreated totals for each user and date range
        """
        # if the shift doesn't have a clocked in and clocked out date, skip it because these rows are total rows
        return not shift.get("clocked_in") and not shift.get("clocked_out")




    def _handle_bad_entries(self, shift: QunaticShiftData):
        """ user's shouldn't be clocked in in the data that is imported
            we will take action here to notify and warn the admin of
            any shifts that are not in the 'Clocked In' status

           another cas is when the shift length is greater than 16 hours

           Lets raise and error for this """

        user_name = shift.get("first_name") + " " + shift.get("last_name")
        # clocked_in and clocked_out are ISO 8601 format strings
        clocked_in_dt = datetime.fromisoformat(shift.get("clocked_in"))
        clocked_out_dt = datetime.fromisoformat(shift.get("clocked_out"))

        # Normalize to Eastern Time
        if clocked_in_dt.tzinfo is None:
            clocked_in_dt = clocked_in_dt.replace(tzinfo=eastern)
        else:
            clocked_in_dt = clocked_in_dt.astimezone(eastern)

        if clocked_out_dt.tzinfo is None:
            clocked_out_dt = clocked_out_dt.replace(tzinfo=eastern)
        else:
            clocked_out_dt = clocked_out_dt.astimezone(eastern)

        if shift.get("status") == "Clocked In":
            # TODO: notify admin of clocked in shift
            print(f"User {user_name} is clocked in")
            pass

        # throw an error if the shift doesn't have a clocked in and clocked out time
        if not clocked_in_dt or not clocked_out_dt:
            raise Exception(f"Error: Shift {user_name} has no clocked in or clocked out time.")

        shift_length = (clocked_out_dt - clocked_in_dt).total_seconds() / 3600

        if shift_length > SHIFT_LENGTH_MAX:
            raise ElixirShiftLengthError(user_name, shift_start=clocked_in_dt, shift_end=clocked_out_dt, shift_location=self.location)


    def parse_shifts(self):
        parsed_shifts = []
        for shift in self.shift_data:
            # this is a total row, skip it
            if self._is_total_row(shift):
                continue


            # handle clocked in
            self._handle_bad_entries(shift)


            # splits this into a workteams a or b
            start_datetime = datetime.fromisoformat(shift.get("clocked_in"))
            end_datetime = datetime.fromisoformat(shift.get("clocked_out"))

            if start_datetime.tzinfo is None:
                start_datetime = start_datetime.replace(tzinfo=eastern)
            else:
                start_datetime = start_datetime.astimezone(eastern)

            if end_datetime.tzinfo is None:
                end_datetime = end_datetime.replace(tzinfo=eastern)
            else:
                end_datetime = end_datetime.astimezone(eastern)

            work_team_shifts =WorkTeamDay(start_date=start_datetime, end_date=end_datetime)

            if work_team_shifts.team_a:
                shift_a = {
                    "first_name": shift.get("first_name"),
                    "last_name": shift.get("last_name"),
                    "start_date": work_team_shifts.team_a.get("start_date"),
                    "end_date": work_team_shifts.team_a.get("end_date"),
                    "shift_status": shift.get("status"),
                    "shift_type": "a",
                    "location": self.location,
                }
                parsed_shifts.append(shift_a)

            if work_team_shifts.team_b:
                shift_b = {
                    "first_name": shift.get("first_name"),
                    "last_name": shift.get("last_name"),
                    "start_date": work_team_shifts.team_b.get("start_date"),
                    "end_date": work_team_shifts.team_b.get("end_date"),
                    "shift_status": shift.get("status"),
                    "shift_type": "b",
                    "location": self.location,
                }
                parsed_shifts.append(shift_b)

        self.parsed_shifts = parsed_shifts
        return self.parsed_shifts

    def get_shifts_by_date(self, date: datetime) -> list[ElixirShift]:
        """Returns a list of shifts for a specific date."""
        shifts: list[ElixirShift] = []
        for shift in self.parsed_shifts:
            if shift.get("start_date") == date:
                shifts.append(shift)
        return shifts
