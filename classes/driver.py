
from classes.session import Session
from classes.lap import Lap 
from classes.data_utilities import json_to_file, milliseconds_to_seconds, save_driver, sort_array_of_dicts
from classes.time_utilities import seconds_to_pretty_time, categorize_laptime
from classes.print_utilities import print_side_by_side, rank_to_color, colored

class Driver:
    name: str
    first_name: str
    last_name: str
    short_name: str
    id: str
    wins: int
    division: str
    division_number: int
    podiums: int
    poles: int
    team: str
    sessions: list
    notes: str
    car: str
    car_number: int


    def __init__(self, data: dict):
        self.name = data['driver']
        self.first_name = ''
        self.last_name = ''
        self.short_name = ''
        self.id = data['driver id']
        self.division = None
        self.division_number = None
        self.wins = 0
        self.podiums = 0
        self.poles = 0
        self.team = ''
        self.sessions = []
        self.notes = ''

    def update_notes(self, notes: str):
        self.notes = notes

    def print(self):
        print(f'{self.name} ({self.division})')
        print(self.team)
        print(f'Wins: {self.wins}, Podiums: {self.podiums}, Poles: {self.poles}')
        print(self.notes)


    def add_session(self, session: dict):

        if not session_exists(session, self.sessions):
            if self.first_name == '':
                self.first_name = session['first name']
                self.last_name = session['last name']
                self.short_name = session['short name']
            new_session = Session(session)
            if new_session.type == 'R':
                if new_session.finish <= 3:
                    self.podiums += 1
                if new_session.finish == 1:
                    self.wins += 1
            elif new_session.type == 'Q':
                if new_session.finish == 1:
                    self.poles += 1
            self.sessions.append(new_session)

    def session_summary(self, track: str='', wet: bool=False, car: str='', type: str=''):
        """
        Print a summary of the driver's sessions.
        Able to specify a track, car, session type or wet conditions.
        Default is dry, any track any car any session type 
        """

        matching_sessions = []

        for session in self.sessions:
            if track.lower() in session.track.lower():
                if car.lower() in session.car.lower():
                    if wet == session.wet:
                        if type.lower() in session.type.lower():
                            matching_sessions.append(session)


        output = []
        for session in matching_sessions:
            wet_msg = ''
            if session.wet:
                wet_msg = f" ({colored('wet', 'blue')})"
            msg = f'{colored(session.track, "green")} {session.date[:10]} {session.id} {wet_msg}\n'
            msg = f'{msg}{len(session.laps)} laps | {session.car}\n'

            best_lap_seconds = None
            if 'best lap' in session.analysis:
                try:
                    best_lap_seconds = session.analysis['best lap'].seconds
                except:
                    pass

            
            msg = f"{msg}Best: {seconds_to_pretty_time(best_lap_seconds)}, Average: {seconds_to_pretty_time(session.analysis['average']['time'])}\n\n"
            output.append(msg)

        
        print_side_by_side(output, line_len=45)



    def self_assessment(self, do_print: bool = True):
        """
        Check this driver's lap times against the reference lap times
        """

        points = {
            'Alien': 5,
            'Pro': 4,
            'ProAm': 3,
            'AM': 2,
            'Rookie': 1
        }



        tracks = []
        for session in self.sessions:
            if session.valid_lap_count > 0:
                if session.track not in tracks:
                    tracks.append(session.track)

        assessment = {
            'tracks': {},
            'summary': {
                'best': {
                    'score': 0,
                    'rank': ''
                },
                'average': {
                    'score': 0,
                    'rank': ''
                }
            }
        }


        has_lap = {
            'best': 0,
            'average': 0
        }
        for track in tracks:
            summary = self.track_summary(track)


            if summary:
                # print(track)
                best_categorization = categorize_laptime(track, summary['best lap'].seconds)
                average_categorization = categorize_laptime(track, summary['best average lap'])

                if best_categorization:
                    has_lap['best'] += 1
                    assessment['summary']['best']['score'] += points[best_categorization]

                if average_categorization:
                    has_lap['average'] += 1
                    assessment['summary']['average']['score'] += points[average_categorization]

                assessment['tracks'][track] = {
                    'best lap': best_categorization,
                    'best average lap': average_categorization
                }


        for type in ['best', 'average']:
            if has_lap[type] > 0:
                assessment['summary'][type]['score'] = assessment['summary'][type]['score'] / has_lap[type]
                if assessment['summary'][type]['score'] >= 4.5:
                    assessment['summary'][type]['rank'] = 'Alien'
                elif assessment['summary'][type]['score'] >= 3.5:
                    assessment['summary'][type]['rank'] = 'Pro'
                elif assessment['summary'][type]['score'] >= 2.5:
                    assessment['summary'][type]['rank'] = 'ProAm'
                elif assessment['summary'][type]['score'] >= 1.5:
                    assessment['summary'][type]['rank'] = 'AM'
                elif assessment['summary'][type]['score'] < 1.5:
                    assessment['summary'][type]['rank'] = 'Rookie'


        if not do_print:
            return assessment


        tracks = assessment['tracks']
        summary = assessment['summary']

        track_msg_output = []
        for track in tracks:
            new_entry = []
            if tracks[track]["best lap"]:
                new_entry.append(f'Best: {colored(tracks[track]["best lap"], rank_to_color(tracks[track]["best lap"]))}')

            if tracks[track]['best average lap']:
                new_entry.append(f'Avg: {colored(tracks[track]["best average lap"], rank_to_color(tracks[track]["best average lap"]))}')

            if len(new_entry) > 0:
                track_msg_output.append(
                    f'{colored(track, "blue")}\n{", ".join(new_entry)}\n\n'
                )

        print_side_by_side(track_msg_output)

        print(f"   {colored('Summary', 'blue')}")

        summary_best = summary['best']['rank']
        summary_avg = summary['average']['rank']

        print(f'   Ranking based on best lap times:    {colored(summary_best, rank_to_color(summary_best))}')
        print(f'   Ranking based on average lap times: {colored(summary_avg, rank_to_color(summary_avg))}')
        print('\n\n')


    def track_summary(self, track: str, type: str='', wet: bool=False, car: str=''):
        """
        Dict containing a summary of this driver's performance at a specific track.
        Optional:  Specify session type (R, Q, FP)
        """

        output = {
            'best lap': None,
            'best average lap': 99999,
            'car': '',
            'car id': '',
            'date': '',
            'type': ''
        }
        for session in self.sessions:
            if session.valid_lap_count > 0:
                if session.track == track:
                    if type == '' or type.lower() == session.type.lower():
                        if car.lower() in session.car.lower():
                            if session.wet == wet:



                                if output['best lap'] == None:
                                    if 'best lap' in session.analysis:
                                        output['best lap'] = session.analysis['best lap']
                                        output['car'] = session.car
                                        output['car id'] = session.car_id
                                        output['date'] = session.date
                                        output['type'] = session.type

                                elif 'best lap' in session.analysis:
                                    if session.analysis['best lap'].seconds < output['best lap'].seconds:
                                        output['best lap'] = session.analysis['best lap']
                                        output['car'] = session.car
                                        output['car id'] = session.car_id
                                        output['date'] = session.date
                                        output['type'] = session.type


                                    if session.analysis['average']['time']:
                                        if session.analysis['average']['time'] < output['best average lap']:
                                            output['best average lap'] = session.analysis['average']['time']

        if output['best lap'] == None:
            return None

        if output['best average lap'] == 99999:
            output['best average lap'] = None


        if 'best average lap' in output:
            output['best average lap'] = seconds_to_pretty_time(output['best average lap'])


        
        return output



    def laps_per_day(self):
        """
        Returns how many laps the driver completed each day.
        Sorted from most laps -> least laps
        """

        output = {}

        for session in self.sessions:
            day = session.date[:10]
            if day not in output:
                output[day] = 0

            output[day]+= len(session.laps)


        output = dict(
            sorted(
                output.items(), key=lambda item: item[1], reverse=True
            )
        )

        return output
        

            

    def save(self):
        save_driver(self)

def session_exists(session: dict, sessions: list):
    for existing_session in sessions:
        if existing_session.id == session['session id']:
            if existing_session.car == session['car']:
                if existing_session.finish == session['finish position']:
                    return True
                
                    


    return False