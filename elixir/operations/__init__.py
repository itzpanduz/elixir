# under the elixir/operations directory we will be able to import in a csv from the quantic system
# the csv will also have a operations location.
# We will have sperate methods for each csv
# there will be a folder named data that will have sub folders for shits and tip named that respectively
# we will have a class for each of these csvs to  parase the data using seperate mappied dictionaries

from datetime import datetime
import json
from typing import TypedDict
from elixir.quantic import QuanticTipCsvParser, QunanticShiftCsvParser, QuanticTipData, QunaticShiftData
from elixir.operations.shift_parser import ElixirShiftParser, ElixirShift
from elixir.operations.tip_parser import ElixirTipParser, ElixirTip
import os


class ElixirOperations:
    def __init__(self, location: str = "buford"):
        self.location = location.lower()
        self.shifts: list[ElixirShift] = []
        self.tips: list[ElixirTip] = []

        self.process_time()
        self.process_tips()


    def get_workers(self, start_date_range:datetime| None =None, end_date_range: datetime | None = None) -> list[str]:
        """Returns a unique list of workers on shifts
        optional datetime range"""
        # get a distinct list of workers on shifts
        workers = []
        for shift in self.shifts:
            # skip if shift isn't in the date range
            if start_date_range and shift.get("start_date") < start_date_range:
                continue
            if end_date_range and shift.get("end_date") > end_date_range:
                continue
            worker_name = f"{shift.get('first_name','')} {shift.get('last_name','')}"
            workers.append(worker_name)

        return list(set(workers))

    def get_csv_paths(self, csv_type: str = 'time'):
        # csv type is either time or tips
        # the location of the file after the data folder has the site location
        # e.g. data/buford/tipsb_time_33125.csv
        # we would  return buford as the site location
        if csv_type not in ['time', 'tips']:
            raise ValueError(f"Invalid csv_type: {csv_type}. Must be 'time' or 'tips'.")
        location_name = self.location.lower()
        csv_type = csv_type.lower()
        csv_directory = os.path.join('data', location_name, csv_type)
        # get all the csv files in the directory
        directory_files = os.listdir(csv_directory)
        # filter out the files that are not csvs
        csv_files = [file for file in directory_files if file.endswith('.csv')]
        # want to return the full path to the csv files
        csv_files_paths = [os.path.join(csv_directory, file) for file in csv_files]
        # return the list of csv files
        return csv_files_paths


    def process_time(self) -> list[ElixirShift]:
        # the default location is buford thie is the folder after data that holds
        # the data for time and tips
        # get all the csv files in the directory
        csv_files = self.get_csv_paths( "time")
        all_time_data = []
        # loop through each csv file
        for csv_file in csv_files:
            # create a new instance of the QunaticShiftCsv class
            shift_csv_list = QunanticShiftCsvParser(csv_file).get_all_data()
            # append the data to the all_time_data list
            all_time_data.extend(shift_csv_list)

        print(f"process time data length {len(all_time_data)}")

        self.shifts = ElixirShiftParser(all_time_data, self.location).parse_shifts() or []
        return self.shifts


    def process_tips(self) -> list[ElixirTip]:
        # the data for time and tips
        # get all the csv files in the directory
        csv_files = self.get_csv_paths("tips")
        all_tip_data = []
        # loop through each csv file
        for csv_file in csv_files:
            # create a new instance of the QunaticShiftCsv class
            tip_csv_list = QuanticTipCsvParser(csv_file).get_all_data()
            # append the data to the all_time_data list
            all_tip_data.extend(tip_csv_list)

        print(f"process tips data length {len(all_tip_data)}")

        self.tips = ElixirTipParser(all_tip_data, self.location).parse_tips() or []
        return self.tips


# Example Usage:
# if __name__ == '__main__':
#     time_data = ElixirOperations().process_time()
#     for time in time_data[:10]:
#         print(json.dumps(time, indent=4))

#     tip_data = ElixirOperations().process_tips()
#     for tip in tip_data[:10]:
#         print(json.dumps(tip, indent=4))
