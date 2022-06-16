from datetime import datetime

from classes.data_utilities import sort_array_of_dicts


LAPTIME_REFERENCES = {

    "barcelona": {
        "alien": "01:43.000",
        "pro": "01:44.500",
        "proam": "01:45.600",
        "am": "01:46.800",
        "rookie": "01:48.300"
    },
    "mount_panorama": {
        "alien": "02:00.400",
        "pro": "02:02.100",
        "proam": "02:03.400",
        "am": "02:04.700",
        "rookie": "02:06.500"
    },
    "brands_hatch": {
        "alien": "01:22.700",
        "pro": "01:23.800",
        "proam": "01:24.700",
        "am": "01:25.600",
        "rookie": "01:26.900"
    },
    "donington": {
        "alien": "01:25.900",
        "pro": "01:27.100",
        "proam": "01:28.000",
        "am": "01:29.000",
        "rookie": "01:30.300"
    },
    "hungaroring": {
        "alien": "01:42.700",
        "pro": "01:44.100",
        "proam": "01:45.300",
        "am": "01:46.400",
        "rookie": "01:47.900"
    },
    "imola": {
        "alien": "01:40.600",
        "pro": "01:42.000",
        "proam": "01:43.100",
        "am": "01:44.200",
        "rookie": "01:45.700"
    },
    "kyalami": {
        "alien": "01:40.100",
        "pro": "01:41.500",
        "proam": "01:42.600",
        "am": "01:43.700",
        "rookie": "01:45.200"
    },
    "laguna_seca": {
        "alien": "01:21.700",
        "pro": "01:22.800",
        "proam": "01:23.700",
        "am": "01:24.600",
        "rookie": "01:25.900"
    },
    "misano": {
        "alien": "01:33.200",
        "pro": "01:34.500",
        "proam": "01:35.500",
        "am": "01:36.600",
        "rookie": "01:38.000"
    },
    "monza": {
        "alien": "01:47.300",
        "pro": "01:48.800",
        "proam": "01:50.000",
        "am": "01:51.200",
        "rookie": "01:52.800"
    },
    "nurburgring": {
        "alien": "01:53.600",
        "pro": "01:55.200",
        "proam": "01:56.400",
        "am": "01:57.700",
        "rookie": "01:59.400"
    },
    "oulton_park": {
        "alien": "01:32.700",
        "pro": "01:34.000",
        "proam": "01:35.000",
        "am": "01:36.000",
        "rookie": "01:37.400"
    },
    "paul_ricard": {
        "alien": "01:53.600",
        "pro": "01:55.200",
        "proam": "01:56.400",
        "am": "01:57.700",
        "rookie": "01:59.400"
    },
    "silverstone": {
        "alien": "01:56.900",
        "pro": "01:58.500",
        "proam": "01:59.800",
        "am": "02:01.100",
        "rookie": "02:02.900"
    },
    "snetterton": {
        "alien": "01:45.300",
        "pro": "01:46.800",
        "proam": "01:48.000",
        "am": "01:49.100",
        "rookie": "01:50.700"
    },
    "spa": {
        "alien": "02:17.100",
        "pro": "02:19.000",
        "proam": "02:20.500",
        "am": "02:22.000",
        "rookie": "02:24.100"
    },
    "suzuka": {
        "alien": "01:58.700",
        "pro": "02:00.400",
        "proam": "02:01.700",
        "am": "02:03.000",
        "rookie": "02:04.800"
    },
    "zandvoort": {
        "alien": "01:34.300",
        "pro": "01:35.600",
        "proam": "01:36.600",
        "am": "01:37.600",
        "rookie": "01:39.100"
    },
    "zolder": {
        "alien": "01:27.400",
        "pro": "01:28.600",
        "proam": "01:29.600",
        "am": "01:30.500",
        "rookie": "01:31.900"
    }
}
    

def categorize_laptime(track: str, laptime) -> str:
    """
    Takes a laptime (pretty laptime or float seconds) and categorizes the laptime
    (pro, proam, alien, etc.) based on track
    """

    track_times = LAPTIME_REFERENCES[track]
    if laptime == None:
        return None

    if type(laptime) == str:
        laptime = pretty_time_to_seconds(laptime)

    if laptime < (pretty_time_to_seconds(track_times['alien']) - 4):
        return 'GOD'
    elif laptime <= pretty_time_to_seconds(track_times['alien']):
        return 'Alien'
    elif laptime <= pretty_time_to_seconds(track_times['pro']):
        return 'Pro'
    elif laptime <= pretty_time_to_seconds(track_times['proam']):
        return 'ProAm'
    elif laptime <= pretty_time_to_seconds(track_times['am']):
        return 'AM'
    elif laptime > pretty_time_to_seconds(track_times['am']):
        return 'Rookie'

    return None




def milliseconds_to_seconds(milliseconds: int) -> float:
    """
    Converts 63587 milliseconds to 63.587 seconds
    """
    return float(milliseconds / 1000)

def pretty_time_to_seconds(pretty_time: str) -> float:
    """
    Takes a pretty format time (Min:Sec.Mill) and 
    converts to seconds
    """

    dissected = dissect_time(pretty_time)
    minutes = dissected['minutes']
    seconds = dissected['seconds']
    milliseconds = dissected['milliseconds']


    total_seconds = (minutes * 60) + seconds + milliseconds_to_seconds(milliseconds)

    return total_seconds


def dissect_time(time) -> dict:
    """
    Take a time (pretty time or seconds) and return the different elements
    2:18.500 
    becomes
    {
        'minutes': 2,
        'seconds': 18,
        'milliseconds': 500
    }
    """
    if type(time) == float:
        time = seconds_to_pretty_time(time)

    colon_split = time.split(":")

    minutes = int(colon_split[0])

    period_split = colon_split[1].split('.')

    seconds = int(period_split[0])

    if len(period_split) == 2:
        milliseconds = int(period_split[1])
        # milliseconds = float(milliseconds / 1000)
    else:
        milliseconds = 0

    
    return {
        'minutes': minutes,
        'seconds': seconds,
        'milliseconds': milliseconds
    }


def seconds_to_pretty_time(seconds: float) -> str:
    """
    Takes a float representing seconds and converts to
    a pretty time Min:Sec.Milliseconds
    """

    if seconds == None:
        return None

    minutes, seconds = divmod(seconds, 60)
    minutes = int(minutes)
    seconds = round(seconds, 3)
    
    if '.' in str(seconds):
        milliseconds = str(seconds).split('.')[1]
    else:
        milliseconds = '000'


    if minutes < 10:
        minutes = f'0{minutes}'
    if seconds < 10:
        seconds = f'0{seconds}'

    if len(milliseconds) == 1:
        seconds = f'{seconds}00'
    elif len(milliseconds) == 2:
        seconds = f'{seconds}0'

    return f'{minutes}:{seconds}'

def compare_times(time_1: str, time_2: str):
    """
    Returns the difference between two times in seconds.
    Accepts Minutes:Seconds.milliseconds
    00:35.927
    """

    if type(time_1) != str:
        time_1 = seconds_to_pretty_time(time_1)
    if type(time_2) != str:
        time_2 = seconds_to_pretty_time(time_2)

    t1 = datetime.strptime(time_1, '%M:%S.%f')
    t2 = datetime.strptime(time_2, '%M:%S.%f')

    diff = t2 - t1

    return diff.total_seconds()

def tally_times(times: list) -> str:
    """
    Take a list of times and return total (in pretty_time format)
    """
    minutes = 0
    seconds = 0
    milliseconds = 0

    for time in times:
        dissected = dissect_time(time)
        minutes += dissected['minutes']
        seconds += dissected['seconds']
        milliseconds += dissected['milliseconds']

    total_seconds = (minutes * 60) + seconds + milliseconds_to_seconds(milliseconds)

    return seconds_to_pretty_time(total_seconds)
    

def min_max(time_list: list): 
    """
    Return min and max times from a list of times
    """

    if len(time_list) == 0:
        return {
            'min': '00:00.000',
            'max': '00:00.000'
        }

    times = []
    for time in time_list:
        if type(time) == float:
            secs = time
            time = seconds_to_pretty_time(time)
        else:
            secs = pretty_time_to_seconds(time)
        times.append(
            {
                'time': time,
                'seconds': secs
            }
        )

    times = sort_array_of_dicts(times, 'seconds')
    return {
        'min': times[-1]['time'],
        'max': times[0]['time']
    }

def date_to_epoch(date_string: str):
    """
    Convert a date/time to epoch
    Useful for sorting
    """

    dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    epoch = dt.timestamp()
    return int(epoch)

def average_time(time_list: list) -> float:
    """
    Takes a list of times (pretty times or float seconds)
    Returns an average time in seconds
    """

    if len(time_list) == 0:
        return 0

    seconds = 0
    for t in time_list:
        if type(t) == float:
            seconds += t
        elif type(t) == str:
            seconds += pretty_time_to_seconds(t)

    return round(seconds / len(time_list), 3)





