from classes.sector import Sector
from classes.lap import Lap
from classes.print_utilities import print_side_by_side

from classes.time_utilities import average_time, milliseconds_to_seconds, categorize_laptime, min_max





class Session:
    type: str
    date: str
    track: str
    wet: bool
    car: str
    car_id: int
    number: int
    missing_pitstop: int
    laps: list
    valid_lap_count: int
    penalties: list
    start: int
    finish: int
    analysis: dict
    id: str

    def __init__(self, data: dict):
        self.type = data['type']
        self.date = data['date']
        self.track = data['track']
        self.wet = bool(data['wet'])
        self.id = data['session id']
        self.car = data['car']
        self.car_id = data['car id']
        self.missing_pitstop = data['missing pitstops']
        self.number = data['number']
        self.analysis = {}
        # self.analysis['best lap'] = data['best lap']
        # self.analysis['best sectors'] = data['best sectors']
        self.valid_lap_count = 0
        self.finish = data['finish position']
        self.penalties = data['penalties']



        # add laps
        self.laps = []
        for lap_data in data['laps']:
            new_lap = Lap(1 + len(self.laps))
            for sect in range(1, 4):
                new_lap.add_sector(
                    Sector(
                        lap_data['sectors'][f'sector {sect}'], sect - 1
                    )
                )


            # Temp fix for the add_sector tally sometimes being off by 0.001
            new_lap.force_update_total_seconds(lap_data['time'])

            laptime_category = categorize_laptime(self.track, new_lap.seconds)
            if laptime_category == 'GOD' or lap_data['valid'] == False:
                new_lap.invalidate()
            else:
                self.valid_lap_count += 1

            self.laps.append(new_lap)

        
        


        self.analysis['average'] = find_average_time(self.laps)
        best_lap = None
        for lap in self.laps:
            if lap.valid:
                if best_lap == None:
                    best_lap = lap
                
                elif lap.seconds < best_lap.seconds:
                    best_lap = lap

            
        
        self.analysis['best lap'] = best_lap

            # if lap.seconds == data['best lap']:
            #     self.analysis['best lap'] = lap
            #     break



    def json(self):
        """
        JSON output
        """

        output = {
            'date': self.date,
            'session id': self.id,
            'type': self.type,
            'track': self.track,
            'wet': self.wet,
            'car': self.car,
            'number': self.number,
            'analysis': {},
            'penalties': self.penalties,
            'laps': []
        }

        for key in self.analysis:
            item = self.analysis[key]
            if type(item) in (str, int, float):
                output['analysis'][key] = item
            elif type(item) == Lap:
                output['analysis'][key] = item.json()


        for lap in self.laps:
            output['laps'].append(lap.json())

        return output




def find_average_time(laps: list, sliding_window_size: int = 5):
    """
       Returns an average time based on (sliding_window_size) consecuitive valid laps
       * Does not count lap 1
    """

    best_average_time = None
    best_average_laps = []



    for i in range(1, len(laps)):#, sliding_window_size):
        evaluate_laps = laps[i:i+sliding_window_size]

        # Are all of them valid?

        if len(evaluate_laps) == sliding_window_size:
            all_valid = True
            for lap in evaluate_laps:
                if not lap.valid:
                    all_valid = False
                    break

            if all_valid:
                time_list = []
                for lap in evaluate_laps:
                    time_list.append(lap.seconds)
                avg_time = average_time(time_list)
               

                if best_average_time == None:
                    best_average_time = avg_time
                    best_average_laps = evaluate_laps
                else:
                    if avg_time < best_average_time:
                        best_average_time = avg_time
                        best_average_laps = evaluate_laps

    
    output = {
        'time': best_average_time,
        'laps': []
    }

    if best_average_time:
        for lap in best_average_laps:
            output['laps'].append(lap.json())
            


    return output