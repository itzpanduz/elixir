# exlixir work team class is a utility static method class that will take in a
# start and end dateime and return what team  datetime a
from datetime import datetime, time

from enum import Enum

from pandas.io.formats.style_render import TypedDict
# we want workteam enum for the shifts
# alpha and bravo are the two shifts
from zoneinfo import ZoneInfo
SHIFT_BOUNDARY = datetime.strptime("6:30 PM", '%I:%M %p').time()


class TeamType(str, Enum):
    a = "alpha"
    b = "bravo"

class TeamDay(TypedDict):
    start_date: datetime
    end_date: datetime


class WorkTeamDay():
    def __init__(self, start_date: datetime | None = None, end_date: datetime | None = None):
        self.team_a: None | TeamDay = None
        self.team_b: None | TeamDay = None

        if start_date and end_date:
            self.team_a = self.get_team_hours(start_date, end_date, TeamType.a)
            self.team_b = self.get_team_hours(start_date, end_date, TeamType.b)
        else:
            raise Exception(f"start and end date must be provided {start_date} - {end_date}")

    @staticmethod
    def get_boundary_time( date_time: datetime) -> datetime:
        # given a datetime return the same datetime but with the time set to 6:30 pm
        boundary_df= datetime.combine(date_time.date(), SHIFT_BOUNDARY)
        boundary_df = boundary_df.replace(tzinfo=ZoneInfo("America/New_York"))
        return boundary_df

    def get_team_hours(self,start_date: datetime, end_date: datetime, shift_type: TeamType) -> TeamDay | None:
        # given a start and end datetime and a shift type return the team day hours that
        #  land within the boundary time. team a is before boundary time and team b is after
        # start date is before boundary time  then we have a value for team a other none
        # if end date is after boundary time then we have a value for team b other none
        shift_boundary_dt = WorkTeamDay.get_boundary_time(start_date)

        # user wants to get the hours for team a
        if shift_type == TeamType.a:
            # if start date is after the boudary then return none
            if start_date > shift_boundary_dt:
                return None

            # the max end date for team_a is the boundary time,
            # if the end_date is beyond the boundary use the boundary time
            # otherwise use the end date
            team_a_end = end_date
            if end_date > shift_boundary_dt:
                team_a_end = shift_boundary_dt

            # return team_a times
            return TeamDay(start_date = start_date, end_date = team_a_end)


        if shift_type == TeamType.b:
            # if end date is before the boudary then return none
            if end_date < shift_boundary_dt:
                return None
            # the earliest start date for team b is the boundary time,
            # if the start_date is before the boundary use the boundary time
            # otherwise use the start date
            team_b_start = start_date
            if start_date < shift_boundary_dt:
                team_b_start = shift_boundary_dt

            return TeamDay(start_date = team_b_start, end_date = end_date)

        return None


    @staticmethod
    def get_team_by_time( time: datetime) -> TeamType | None:
        # given a time return the shift type that lands within the boundary time
        if time < WorkTeamDay.get_boundary_time(time):
            return TeamType.a
        if time > WorkTeamDay.get_boundary_time(time):
            return TeamType.b
        return None
