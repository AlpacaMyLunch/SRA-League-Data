from classes.sector import Sector
from classes.time_utilities import seconds_to_pretty_time, tally_times, pretty_time_to_seconds
from classes.print_utilities import colored


class Lap:
    pretty_time: str
    sectors: list
    number: int
    valid: bool
    seconds: float

    def __init__(self, number: int):
        self.pretty_time = ''
        self.sectors = []
        self.number = number
        self.seconds = 0
        self.valid = True


    def force_update_total_seconds(self, seconds: float):
        """
        The tally from add_sector is sometimes off by 0.001
        Rounding.

        Temp fix: use this to force a total lap time in seconds
        """

        self.seconds = seconds
        self.pretty_time = seconds_to_pretty_time(self.seconds)

    def add_sector(self, sector: Sector):
        """
        Add a sector to this lap
        """

        self.sectors.append(sector)

        # Even if we add the sectors out of order
        # Make sure the array has them in proper order
        self.sectors.sort(key=lambda x: x.number, reverse=False)

        sector_times = []
        for sector in self.sectors:
            sector_times.append(sector.seconds)
        self.pretty_time = tally_times(sector_times)
        self.seconds = pretty_time_to_seconds(self.pretty_time)


    def invalidate(self):
        """
        Set the current lap as invalid
        """
        self.valid = False

    def compare(self, lap) -> float:
        """
        Compare this lap's time to another lap's time.
        Return the difference in seconds
        """

        return round(self.seconds - lap.seconds, 3)


    def print(self):
        print(self.text())

    def text(self) -> str:
        """
        Return a string representation of this lap
        """

        output = f'Lap {self.number}\n'
        for sector in self.sectors:
            output = f'{output}{sector.text()}\n'
        
        output = f'{output}Total: {self.pretty_time}'

        return output
        
        

    def return_sector(self, sector_number: int) -> Sector:
        """
        Return a sector from this lap based on sector number
        """

        for sector in self.sectors:
            if sector.number == sector_number:
                return sector
        return None

    
    def json(self) -> dict:
        """
        Return a JSON representation of this lap
        """

        output = {
            'number': self.number,
            'time': self.pretty_time,
            'valid': self.valid,
            'seconds': self.seconds,
            'sectors': []
        }

        for sector in self.sectors:
            output['sectors'].append(sector.json())

        return output

