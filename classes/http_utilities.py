import requests
import time

from bs4 import BeautifulSoup
from classes.print_utilities import colored
from classes.data_utilities import load_session, parse_session_list, parse_session_json, json_from_file

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
BASE_URL = 'https://simracingalliance.emperorservers.com'
BASE_URL_DIV_3 = 'https://accsm.simracingalliance.com'

CONFIG_DATA = json_from_file('./config/config.json')

def get_session_details(href: str) -> dict:
    
    href = href.replace('/results/', '/results/download/')
    url = f'{href}.json'

    req = http_request(url)

    data = req.json()
    return parse_session_json(data)





def get_division_drivers(div: str='pro') -> list:
    """
    Returns a list containing information for the specified division's drivers.
    Pro, Pro/Am, Am and Rookie
    """

    if 'pro' in div:
        url = 'https://simracingalliance.emperorservers.com/championship/cfd5922d-0a13-437e-95c4-07653e3b372a'
    elif div == 'am':
        url = 'https://simracingalliance.emperorservers.com/championship/8b417822-6481-45af-891c-524bfc35faac'
    elif div == 'rookie':
        url = 'https://accsm.simracingalliance.com/championship/552b0acf-5aae-401c-81de-d4fbba2f679e'

    req = http_request(url)
    data = req.text

    soup = BeautifulSoup(data, 'html.parser')
    output = []

    tables = soup.find_all('table', class_='table table-bordered table-striped')
    if len(tables) == 2:
        registration_table = tables[0]
    elif len(tables) > 2:
        registration_table = tables[3]

    registration_table = registration_table.find_all('tr')
    for row in registration_table[1:]:
        items = row.find_all('td')
        number = items[0].contents[0].string.strip()
        team = items[1].contents[0].string.strip()
        car = items[2].contents[0].string.strip()
        driver = items[3].string

        if 'pro' in div:
            division_number = 1
        elif div == 'am':
            division_number = 2
        elif div == 'rookie':
            division_number = 3

        output.append({
            'number': number,
            'car': car,
            'team': team,
            'driver': driver,
            'division': div,
            'division number': division_number
        })

    return output


def get_session_list(page: int=0) -> list:
    """
    Returns a list of sessions
    https://simracingalliance.emperorservers.com/results?page=4
    https://accsm.simracingalliance.com/results?page=4
    """

    output = []
    for b_url in [BASE_URL, BASE_URL_DIV_3]:

        url = f'{b_url}/results?page={page}'
        req = http_request(url)

        if req.status_code != 404:
            html = req.text
            output += parse_session_list(html, b_url)


    return output

    


def post_leaderboard(payload: dict):

    url = CONFIG_DATA['leaderboard_post_url']
    header = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    req = requests.post(url, json=payload, headers=header)
    return req.status_code



def http_request(url: str) -> requests.get:
    headers = {
        "User-Agent": USER_AGENT
        }
    
    attempts = 0
    while True:
        try:
            attempts += 1
            req = requests.get(url, headers=headers)
            if req.ok:
                return req

            if req.status_code == 404:
                return req

        except:
            time.sleep(attempts * 0.5)

        if attempts > 5:
            print(colored(f'    ... problems with http requests on {url}', 'red'))
            print('')