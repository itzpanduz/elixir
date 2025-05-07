# create a class for quantic csv import
# we will take in a csv file and map data fields from it
# there is a shift csv and a tip csv
# we will create a class for each of these csvs to  parase the data using seperate mappid dictionaries
import re
import csv
from datetime import datetime, tzinfo  # Import datetime for time calculations
from typing import TypedDict
from zoneinfo import ZoneInfo
import zoneinfo

class QuanticParseError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class BaseCsvParser:  # Base class to share common functionalities
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.timezone = ZoneInfo("America/New_York")  # Initialize timezone object
        self.data = self.parse_csv()

    def _parse_quantive_datetime(self, date_time_str: str) -> str:
        """Parses a QuantiC date/time string into an ISO 8601 format."""
        try:
            date_time = datetime.strptime(date_time_str, "%m-%d-%y %I:%M %p")
            # Localize the datetime object to the specified timezone
            localized_date_time = date_time.replace(tzinfo=self.timezone)
            # return ISO 8601 format with timezone
            iso_format = localized_date_time.isoformat()
            return iso_format
        except ValueError:
            raise QuanticParseError(f"Invalid date/time format: {date_time_str} expected format: MM-DD-YY HH:MM AM/PM")


    def clean_header(self, header):
        """Cleans a single header string using regex to create snake_case."""
        cleaned_header = re.sub(r"[^a-zA-Z0-9\s]", " ", header).strip()
        # replace consecutive spaces with a single space
        cleaned_header = re.sub(r"\s+", " ", cleaned_header)
        # replace spaces with underscores
        cleaned_header = re.sub(r"\s+", "_", cleaned_header).lower()
        return cleaned_header

    def parse_csv(self):
        """Parses the CSV file with generic logic, to be customized by subclasses."""
        data = []
        try:
            with open(self.csv_file, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                header = next(reader, None)
                if not header:
                    print(f"Error: CSV file is empty or has no header: {self.csv_file}")
                    return []

                standardized_header = [self.clean_header(h) for h in header]
                header_indices = {h: i for i, h in enumerate(standardized_header)}

                for row in reader:
                    if not row:
                        continue
                    row_data = {}
                    for i, col in enumerate(row):
                        header_key = standardized_header[i]
                        col_value = col.strip()
                        # try to parse the date/time if it's in the format MM-DD-YY HH:MM AM/PM as it should
                        if "-" in col_value and (":"  in col_value):
                            col_value = self._parse_quantive_datetime(col_value)
                        row_data[header_key] = col_value
                    data.append(row_data)
            return data
        except FileNotFoundError:
            print(f"Error: File not found: {self.csv_file}")
            return []
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []




# Shift Data Typed Dictionary
class QunaticShiftData(TypedDict):
    first_name: str
    last_name: str
    role: str
    day: str
    clocked_in: str
    clocked_out: str
    c_in_c_out: str
    hourly_rate: str
    hours: str
    tip: str
    declared_tip: str
    status: str

class QunanticShiftCsvParser(BaseCsvParser): # Subclass for the shift CSV
    def __init__(self, csv_file):
        super().__init__(csv_file)  # Initialize the base class
        self.employee_name_key = "first_name" # for access to the employee name
        self.employee_last_name_key = "last_name" # for access to the employee name
        self.hours_key = "hours" # for access to the hours
        self.tip_key = "tip" # for access to the tip


    def get_all_data(self) -> list[QunaticShiftData]:
        """Returns a list of all data in the CSV."""
        data: list[QunaticShiftData] = []
        for row in self.data:
            data.append(row)
        return data

    def get_employee_data(self, first_name, last_name) -> list[QunaticShiftData]:
        """Filters and returns data for a specific employee."""
        employee_data: list[QunaticShiftData] = []
        for row in self.data:
            if row.get(self.employee_name_key) == first_name and row.get(self.employee_last_name_key) == last_name:
                employee_data.append(row)
        return employee_data

    def calculate_total_hours(self, first_name, last_name) -> float:
        """Calculates the total hours worked by an employee."""
        total_hours: float = 0
        employee_data: list[QunaticShiftData] = self.get_employee_data(first_name, last_name)
        for row in employee_data:
            try:
                hours_str: str = row.get(self.hours_key, "")
                if hours_str:
                    total_hours += float(hours_str)
            except ValueError:
                print(f"Warning: Invalid hours value for {first_name} {last_name}: {row.get(self.hours_key)}")
        return total_hours

    def calculate_total_tips(self, first_name, last_name) -> float:
        """Calculates the total tips earned by an employee."""
        total_tips: float = 0
        employee_data: list[QunaticShiftData] = self.get_employee_data(first_name, last_name)
        for row in employee_data:
            try:
                tip_str: str = row.get(self.tip_key, "").replace("$", "")
                if tip_str:
                    total_tips += float(tip_str)
            except ValueError:
                print(f"Warning: Invalid tip value for {first_name} {last_name}: {row.get(self.tip_key)}")
        return total_tips

    def get_all_employees(self) -> list[tuple[str, str]]:
        """Returns a list of unique employee names."""
        employees: set[tuple[str, str]] = set()
        for row in self.data:
            first_name: str = row.get(self.employee_name_key)
            last_name: str = row.get(self.employee_last_name_key)
            if first_name and last_name:
                employees.add((first_name, last_name))
        return list(employees)


# Tip Data Typed Dictionary
class QuanticTipData(TypedDict):
    ref: str
    datetime: str
    employee_name: str
    terminal: str
    cc_info: str
    service_area: str
    pay_type: str
    tip: str


class QuanticTipCsvParser(BaseCsvParser):  # Subclass for the tips CSV
    def __init__(self, csv_file):
        super().__init__(csv_file)  # Initialize the base class
        self.employee_name_key = "employee_name" # for access to the employee name
        self.hours_key = None # there is no hours column in this data
        self.tip_key = "tip" # for access to the tip

    def get_all_data(self) -> list[QuanticTipData]:
        """Returns a list of all data in the CSV."""
        data: list[QuanticTipData] = []
        for row in self.data:
            data.append(row)
        return data

    def get_employee_data(self, employee_name: str) -> list[QuanticTipData]:
        """Filters and returns data for a specific employee."""
        employee_data: list[QuanticTipData] = []
        for row in self.data:
            if row.get(self.employee_name_key) == employee_name:
                employee_data.append(row)
        return employee_data

    def calculate_total_tips(self, employee_name: str) -> float:
        """Calculates the total tips earned by an employee."""
        total_tips: float = 0
        employee_data: list[QuanticTipData] = self.get_employee_data(employee_name)
        for row in employee_data:
            try:
                tip_str: str = row.get(self.tip_key, "").replace("$", "")
                if tip_str:
                    total_tips += float(tip_str)
            except ValueError:
                print(f"Warning: Invalid tip value for {employee_name}: {row.get(self.tip_key)}")
        return total_tips

    def get_all_employees(self) -> list[str]:
        """Returns a list of unique employee names."""
        employees: set[str] = set()
        for row in self.data:
            employee_name: str = row.get(self.employee_name_key)
            if employee_name:
                employees.add(employee_name)
        return list(employees)


if __name__ == '__main__':
    shift_csv_file = 'data/buford/time/b_time_33125.csv'  # Replace with your shift CSV file path
    tip_csv_file = 'data/buford/tips/b_tip_3_31.csv'  # Replace with your tip CSV file path

    print("Running quantic_parsers.py")

    # print first 10 rows of shift data
    shift_data = QunanticShiftCsvParser(shift_csv_file)

    for row in shift_data.data[:10]:
        print(row)

    # print first 10 rows of tip data
    tip_data = QuanticTipCsvParser(tip_csv_file)

    for row in tip_data.data[:10]:
        print(row)
