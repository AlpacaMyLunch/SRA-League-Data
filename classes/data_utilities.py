import json
import pickle
import shlex

from os import path, listdir, remove
from bs4 import BeautifulSoup
DRIVER_PICKLE_DIR = './data/drivers/'
SESSION_CACHE_DIR  = './data/sessions/'

def sort_array_of_dicts(array: list, field: str, reverse: bool = True):
    """
    Take an array of dicts and sort the array based on a key:value present in the dicts
    """

    return sorted(array, key=lambda d: d[field], reverse=reverse)


def parse_arguments(args):
    """
    Converts a string of arguments into a dict

    ex:
    leaderboard track:zolder wet avg 15 div:1 car:m4 team:"missed apex racing"
    
    becomes...

    {
        'track': 'zolder',
        'div': '1',
        'car': 'm4',
        'team': 'missed apex racing',
        'generic': [
            'avg',
            '15',
            'wet'
        ]
    }
    """

    args = shlex.split(args)

    output = {
        'generic': []
    }
    # arg[:6] == 'track:':

    for arg in args:
        if ':' in arg:
            arg = arg.split(':')
            output[arg[0]] = arg[1]
        else:
            output['generic'].append(arg)


    return output






def percentage(part, whole) -> float:
    """
    Returns a percentage based on 'x out of y'
    """
    return (round(100 * float(part)/float(whole), 1))

def milliseconds_to_seconds(milliseconds: int) -> float:
    """
    Converts 63587 milliseconds to 63.587 seconds
    """
    return milliseconds / 1000

#### Data Parsing

def parse_session_list(html: str, base_url: str) -> list:


    soup = BeautifulSoup(html, 'html.parser')

    session_table = soup.find('table', class_='table table-bordered table-striped mt-2')
    rows = session_table.find_all('tr', class_='row-link')

    output = []

    for row in rows:
        data = row.find_all('td')
        date_time = data[0].string.strip()
        session_type = data[1].string.strip()
        track = data[2].string.strip()
        participants = data[3].find('small').string

        if participants:
            participants = participants.split(', ')
            for participant in participants:
                participant = participant.replace('é', 'e')
            href = row.attrs['data-href']
            output.append(
                {
                    'date': date_time,
                    'type': session_type,
                    'track': track,
                    'participants': participants,
                    'href': f'{base_url}{href}',
                    'id': href.split('/')[2]
                }
            )

    return output


def parse_session_json(session: dict) -> dict:

    laps = session['laps']
    penalties = session['penalties']
    type = session['sessionType']
    track = session['trackName']
    date = session['Date']
    wet = session['sessionResult']['isWetSession']
    session_file = session['SessionFile']
    leaderboard = session['sessionResult']['leaderBoardLines']
    finish_position = 1

    participants = {}
    for participant in leaderboard:
        id = participant['car']['carId']
        participants[id] = {}
        participants[id]['type'] = type
        participants[id]['track'] = track
        participants[id]['date'] = date
        participants[id]['wet'] = wet
        participants[id]['session id'] = session_file
        participants[id]['car'] = convert_car_id_to_name(participant['car']['carModel'])
        participants[id]['car id'] = participant['car']['carModel']
        participants[id]['finish position'] = finish_position
        finish_position += 1
        first_driver = participant['car']['drivers'][0]
        if len(participant['car']['drivers']) > 1:
            # Don't feel like handling this right now.  Skip these sessions.
            return {
                'participants': {},
                'type': type,
                'track': track,
                'date': date,
                'wet': wet,
                'session id': session_file
            }
        participants[id]['driver'] = f'{first_driver["firstName"]} {first_driver["lastName"]}'
        participants[id]['first name'] = first_driver["firstName"]
        participants[id]['last name'] = first_driver["lastName"]
        participants[id]['short name'] = first_driver["shortName"]
        
        participants[id]['driver id'] = first_driver['playerId']
        participants[id]['number'] = participant['car']['raceNumber']
        participants[id]['missing pitstops'] = participant['missingMandatoryPitstop']
        participants[id]['best lap'] = milliseconds_to_seconds(participant['timing']['bestLap'])
        participants[id]['best sectors'] = {}
        for sect in range(1, 4):
            participants[id]['best sectors'][f'sector {sect}'] = milliseconds_to_seconds(participant['timing']['bestSplits'][sect - 1])

        participants[id]['penalties'] = []
        for penalty in penalties:
            if penalty['carId'] == id:
                participants[id]['penalties'].append(penalty)

        participants[id]['laps'] = []
        for lap in laps:
            if int(lap['carId']) == int(id):
                lap_data = {
                    'valid': lap['isValidForBest'],
                    'time': milliseconds_to_seconds(lap['laptime']),
                    'sectors': {}
                }
                for sect in range(1, 4):
                    lap_data['sectors'][f'sector {sect}'] = milliseconds_to_seconds(lap['splits'][sect - 1])
                participants[id]['laps'].append(lap_data)



    pop_list = []
    for participant in participants:
        if len(participants[participant]['laps']) == 0:
            pop_list.append(participant)

    for participant in pop_list:
        participants.pop(participant, None)
    
    return {
        'participants': participants,
        'type': type,
        'track': track,
        'date': date,
        'wet': wet,
        'session id': session_file
    }

        



def convert_car_id_to_name(car_id):
    car_id = str(car_id)

    car_dict = {
        '31': 'Audi R8 LMS GT3 evo II',
        '16': 'Lamborghini Huracan Evo (2019)',
        '23': 'Porsche 911 II GT3 R (2019)',
        '22': 'McLaren 720S GT3 (Special)',
        '21': 'Honda NSX Evo (2019)',
        '8': 'Bentley Continental GT3 (2018)',
        '30': 'BMW M4 GT3',
        '20': 'AMR V8 Vantage (2019)',
        '24': 'Ferrari 488 GT3 Evo 2020',
        '0': 'Porsche 991 GT3',
        '1': 'Mercedes AMG GT3',
        '2': 'Ferrari 488 GT3',
        '3': 'Audi R8 GT3 2015',
        '4': 'Lamborghini Huracan GT3',
        '5': 'McLaren 650s GT3',
        '6': 'Nissan GT-R Nismo GT3 2018',
        '7': 'BMW M6 GT3',
        '9': 'Porsche 991 II GT3 Cup',
        '10': 'Nissan GT-R Nismo GT3 2015',
        '11': 'Bentley Continental GT3 2015',
        '12': 'Aston Martin Vantage V12 GT3',
        '13': 'Lamborghini Gallardo R-EX',
        '14': 'Emil Frey Jaguar G3',
        '15': 'Lexus RC F GT3',
        '17': 'Honda NSX GT3',
        '18': 'Lamborghini Huracan SuperTrofeo',
        '19': 'Audi R8 LMS Evo 2019',
        '25': 'Mercedes AMG GT3 2020',
        '50': 'Alpine A110 GT4',
        '51': 'Aston Martin Vantage GT4',
        '52': 'Audi R8 LMS GT4',
        '53': 'BMW M4 GT4',
        '55': 'Chevrolet Camaro GT4',
        '56': 'Ginetta G55 GT4',
        '57': 'KTM X-Bow GT4',
        '58': 'Maserati MC GT4',
        '59': 'McLaren 570S GT4',
        '60': 'Mercedes AMG GT4',
        '61': 'Porsche 718 Cayman GT4',
        '29': 'Lamborghini Huracán Super Trofeo EVO2',
        '26': 'Ferrari 488 GT3 Challenge Evo'
    }

    if car_id in car_dict:
        return car_dict[car_id]
    else:
        return car_id




####  File save / load
def json_from_file(file_name):
    with open(file_name) as json_file:
        json_data = json.load(json_file)
    return json_data
    
    
    
def json_to_file(file_name, json_data):
    with open(file_name, 'w') as out_file:
        json.dump(json_data, out_file)


def pickle_save(file_name, data):
    pickle.dump(data, open(file_name, 'wb'))

def pickle_load(file_name):
    output = None
    if path.exists(file_name):
        output = pickle.load(open(file_name, 'rb'))

    return output


def save_driver(driver):
    file_name = f'{DRIVER_PICKLE_DIR}{driver.id}.pkl'
    pickle_save(file_name, driver)


def load_driver(id: str):
    file_name = f'{DRIVER_PICKLE_DIR}{id}'

    output = pickle_load(file_name)

    return output


def save_session(session, id):
    file_name = f'{SESSION_CACHE_DIR}{id}.json'
    json_to_file(file_name, session)


def load_session(id):
    file_name = f'{SESSION_CACHE_DIR}{id}.json'
    if path.exists(file_name):
        return json_from_file(file_name)
    else:
        return None

def return_all_saved_drivers():
    """
    Returns an array with all saved drivers
    """

    output = []
    for file_name in listdir(DRIVER_PICKLE_DIR):
        if '.pkl' in file_name:
            output.append(load_driver(file_name))

    return output

def delete_driver(driver):
    """
    Deletes a driver's pickle file
    """

    remove(f'{DRIVER_PICKLE_DIR}{driver.id}.pkl')

