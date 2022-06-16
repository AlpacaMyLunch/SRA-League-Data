from classes.time_utilities import pretty_time_to_seconds, seconds_to_pretty_time

class Sector:
    pretty_time: str
    number: int
    seconds: float

    def __init__(self, time, number: int):

        # Pretty formatted time
        if type(time) == str:
            self.pretty_time = time
        else:
            self.pretty_time = seconds_to_pretty_time(time)

        # Sector number.  1, 2 or 3
        self.number = number

        if type(time) == str:
            self.seconds = pretty_time_to_seconds(self.pretty_time)
        else:
            self.seconds = time

    def print(self):
        print(self.text())

    def text(self) -> str:
        """
        Returns a string representation of this sector
        Sector 1: 00:32.104
        """
        return f'Sector {self.number}: {self.pretty_time}'

    def json(self) -> dict:
        """
        Returns a JSON representation of this sector
        """
        return {
            'time': self.pretty_time,
            'number': self.number,
            'seconds': self.seconds
        }

    def compare(self, sector) -> float:
        """
        Compares the time between this sector an another
        Returns the difference in seconds
        """

        return round(self.seconds - sector.seconds, 3)