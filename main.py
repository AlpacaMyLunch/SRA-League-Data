from cmd import Cmd
from classes.data_utilities import json_to_file, return_all_saved_drivers, save_driver, load_driver, save_session, sort_array_of_dicts, load_session, parse_arguments
from classes.print_utilities import colored, print_side_by_side, replace_print
from classes.http_utilities import get_session_list, get_session_details, get_division_drivers, post_leaderboard
from classes.time_utilities import pretty_time_to_seconds, seconds_to_pretty_time, min_max
from classes.driver import Driver
from classes.session import Session
DEFAULT_PROMPT = colored(' [*] SRA >> ', color='cyan', attributes=['bold'])

def main():




    drivers = return_all_saved_drivers()

    # for driver in drivers:
    #     assessment = driver.self_assessment(do_print=False)

    #     if assessment['summary']['best']['score'] >= 3.5:
    #         driver.print()
    #         print(assessment['summary']['best'])
    #         driver.self_assessment(do_print=True)


    # exit()


                

    class Terminal(Cmd):
        prompt = DEFAULT_PROMPT
        selected_driver = None

        def default(self, args):
            pass

        def do_exit(self, args):
            exit()

        def do_list(self, args):
            """
            List tracked drivers
            """
            output = []



        def do_laps_per_day(self, args):



            if self.selected_driver:

                lpd = self.selected_driver.laps_per_day()
                first_item = list(lpd.keys())[0]
                print(f'{colored(lpd[first_item], "blue")} laps on {first_item}')


            else:

                tracker = []
                for driver in drivers:
                    lpd = driver.laps_per_day()
                    date = list(lpd.keys())[0]
                    laps = lpd[date]

                    tracker.append({
                        'driver': driver,
                        'laps': laps,
                        'date': date
                    })

                tracker = sort_array_of_dicts(tracker, 'laps')

                msg_output = []
                for driver in tracker:
                    msg_output.append(
                        f"{driver['driver'].name}\n{driver['laps']} on {driver['date']}\n"
                    )

                print_side_by_side(msg_output, line_len=35)

        def do_sessions(self, args):
            
            if not self.selected_driver:
                print('Please select a driver')
                return

            track = ''
            car = ''
            wet = False
            type = ''
            for arg in args.split(' '):
                if arg[:6] == 'track:':
                    track = arg[6:]
                elif arg[:4] == 'car:':
                    car = arg[4:]
                elif arg == 'wet':
                    wet = True
                elif arg[:5] == 'type:':
                    type = arg[5:]


            self.selected_driver.session_summary(track=track, car=car, type=type, wet=wet)
            

        def do_select(self, args):
            """
            Select a tracked driver.
            """

            args = args.lower()
            possible_drivers = []
            for driver in drivers:
                if driver.division:
                    if args in driver.name.lower():
                        possible_drivers.append(driver)


            if len(possible_drivers) == 0:
                print(f"No matches found in the current season's drivers for '{args}'")
            elif len(possible_drivers) == 1:
                self.selected_driver = possible_drivers[0]
                self.prompt = DEFAULT_PROMPT.replace('SRA', f'{self.selected_driver.name} ({self.selected_driver.division})')
                self.selected_driver.print()
            else:
                msg = []
                for driver in possible_drivers:
                    msg.append(
                        f'{driver.name} ({driver.division})\n'
                    )

                print_side_by_side(msg)
            

        def do_assessment(self, args):
            if self.selected_driver:
                self.selected_driver.self_assessment(do_print=True)

            else:
                assessments = []

                for driver in drivers:
                    assessment = driver.self_assessment(do_print=False)
                    assessments.append({
                        'driver': driver,
                        'best': round(assessment['summary']['best']['score'], 2),
                        'average': round(assessment['summary']['average']['score'], 2)
                    })

                
                best = sort_array_of_dicts(assessments, 'best')
                average = sort_array_of_dicts(assessments, 'average')

                msg_output = []

                best_msg = f"{colored('BEST LAP', 'green')}\n"
                pos = 1
                driver_count = 0
                prev_score = 99999
                for driver in best:
                    driver_count += 1
                    if driver['best'] != prev_score:
                        prev_score = driver['best']
                        pos = driver_count
                    best_msg = f'{best_msg}#{pos} {driver["driver"].name} - {driver["best"]}\n'
                    
                msg_output.append(best_msg)

                avg_msg = f"{colored('AVERAGE LAP', 'green')}\n"
                pos = 1
                driver_count = 0
                prev_score = 99999
                for driver in average:
                    driver_count += 1
                    if driver['average'] != prev_score:
                        prev_score = driver['average']
                        pos = driver_count

                    avg_msg = f'{avg_msg}#{pos} {driver["driver"].name} - {driver["average"]}\n'

                msg_output.append(avg_msg)

                print_side_by_side(msg_output, line_len=45)



                
        def do_export_ids(self, args):
            """
            Exports an array of dicts
            user id with user name
            """
            pass


        def do_update(self, args):
            """
            Update data from webpage
            """

            if args == 'force':
                force = True
            else:
                force = False


            divs = ['pro', 'am', 'rookie']
            drivers_with_divisions = []
            for div in divs:
                replace_print(f'Gathering the {div} division...')
                drivers_with_divisions += get_division_drivers(div)
            replace_print(' ' * 50)
            print('\n')
            for driver in drivers:
                for d in drivers_with_divisions:
                    if driver.name == d['driver']:
                        d['steam id'] = driver.id
            # json_to_file('drivers.json', drivers_with_divisions)


            for d in drivers_with_divisions:
                for driver in drivers:
                    if driver.name == d['driver']:
                        driver.division = d['division']
                        driver.team = d['team']
                        driver.division_number = d['division number']
                        driver.car = d['car']
                        driver.car_number = d['number']
                        break

            class UpToDate(Exception): pass
            no_more_pages = False
            page = 0
            try:
                while True:
                    sessions = get_session_list(page)
                    replace_print(f'working on page {page}...')
                    if len(sessions) == 0:
                        break
                    for session in sessions:
                        details = load_session(session['id'])

                        # if we already have it don't go further
                        if details and not force:
                            no_more_pages = True

                        if details == None:
                            details = get_session_details(session['href'])
                            save_session(details, session['id'])

                        for participant in details['participants']:
                            participant = details['participants'][participant]
                            id = participant['driver id']
                            add = False
                            division = None
                            division_number = None
                            team = None
                            car_number = None

                            for driver in drivers_with_divisions:
                                if participant['driver'] == driver['driver']:
                                    division = driver['division']
                                    division_number = driver['division number']
                                    team = driver['team']
                                    car_number = driver['number']
                                    car = driver['car']

                                    add = True
                                    break

                            for driver in drivers:
                                if driver.id == id:
                                    driver.add_session(participant)
                                    driver.save()
                                    add = False
                                    break
                            if add:
                                new_driver = Driver(participant)
                                new_driver.division = division
                                new_driver.division_number = division_number
                                new_driver.team = team
                                new_driver.car = car
                                new_driver.car_number = car_number
                                new_driver.add_session(participant)
                                new_driver.save()
                                drivers.append(new_driver)
                    page += 1
                    if no_more_pages:
                        raise UpToDate
            except UpToDate:
                pass

            print('\nUpdate complete.\n')



        def do_note(self, notes):
            """
            Set notes for a selected driver
            """

            if self.selected_driver:
                self.selected_driver.update_notes(notes=notes)
                self.selected_driver.print()


        def do_leaderboard(self, args: str):
            tracks = []
            data = {}
            output = []

            post_msgs = []
            result_limit = 999

            args = parse_arguments(args)

            post = False

            if 'div' in args:
                division_specific = int(args['div'])
            else:
                division_specific = None

            if 'track' in args:
                track_specific = args['track']
            else:
                track_specific = None

            if 'team' in args:
                team_specific = args['team']
            else:
                team_specific = ''

            if 'car' in args:
                car_specific = args['car']
            else:
                car_specific = ''

            if 'top' in args:
                result_limit = int(args['top'])
            
            if 'type' in args:
                session_type = args['type']
            else:
                session_type = ''

            if 'post' in args:
                if args['post'] == 'yes':
                    verify = input('Are you sure you wish to POST to the online leaderboard? Y / N?  ')
                    if verify == 'Y':
                        post = True
                        print(colored('WILL POST TO ONLINE LEADERBOARD', 'green'))
                    else:
                        post = False
                        print(colored('WILL ***NOT*** POST TO ONLINE LEADERBOARD', 'red'))



            
            highlight_names = []
            wet = False
            sort_on_average_time = False
            for arg in args['generic']:
                if arg == 'wet':
                    wet = True
                elif arg == 'avg':
                    sort_on_average_time = True
                else:
                    highlight_names.append(arg)

            



            for driver in drivers:
                for session in driver.sessions:
                    if session.track not in tracks:
                        tracks.append(session.track)

            for track in tracks:
                post_data = {
                    'track': {
                        'name': track,
                        'is_wet': int(wet)
                    },
                    'drivers': [

                    ]
                }
                if track_specific == None or track == track_specific:
                    data[track] = []
                    for driver in drivers:
                        if driver.division != None:
                            if division_specific == None or driver.division_number == division_specific:
                                if team_specific.lower() in driver.team.lower():
                                    summary = driver.track_summary(track, wet=wet, car=car_specific, type=session_type)
                                    if summary:
                                        if sort_on_average_time:
                                            if summary['best average lap']:
                                                sortable = pretty_time_to_seconds(summary['best average lap'])
                                            else:
                                                sortable = None
                                        else:
                                            sortable = summary['best lap'].seconds

                                        if sortable:
                                            data[track].append({
                                                'driver': driver.name,
                                                'first name': driver.first_name,
                                                'last name': driver.last_name,
                                                'short name': driver.short_name,
                                                'steam id': driver.id,
                                                'division': driver.division,
                                                'best': summary['best lap'],
                                                'sortable': sortable,
                                                'average': summary['best average lap'],
                                                'car': summary['car'],
                                                'car id': summary['car id'],
                                                'date': summary['date'],
                                                'type': summary['type']
                                            })
                    data[track] = sort_array_of_dicts(data[track], 'sortable', reverse=False)
                    pos = 1
                    for driver in data[track]:
                        
                        post_data['drivers'].append(
                            {
                                'rank': pos,
                                'first_name': driver['first name'],
                                'last_name': driver['last name'],
                                'short_name': driver['short name'],
                                'steam_id': driver['steam id'],
                                'car_id': driver['car id'],
                                'lap_time': int(driver['best'].seconds * 1000),
                                'sector_1': int(driver['best'].sectors[0].seconds * 1000),
                                'sector_2': int(driver['best'].sectors[1].seconds * 1000),
                                'sector_3': int(driver['best'].sectors[2].seconds * 1000)
                            }
                        )
                        pos += 1

                    # json_to_file(f'POST-{track} - wet{wet}.json', post_data)
                    
                    if post:
                        p = post_leaderboard(post_data)
                        post_msgs.append(f'POST for {track} - {p} response\n')


            
            for track in data:
                track_data = data[track]
                new_output = f'{colored(track, "green")}\n'
                position = 1
                for driver in track_data:
                    name_color = 'blue'
                    if len(highlight_names) > 0:
                        for highlight in highlight_names:
                            if highlight in driver['driver'].lower():
                                name_color = 'yellow'
                                
                                new_output = f'{new_output}#{position} {colored(driver["driver"], name_color)}\n{driver["car"]}\n{driver["best"].pretty_time} | {driver["average"]}\n\n'
                                break
                    else:
                        new_output = f'{new_output}#{position} {colored(driver["driver"], name_color)}\n{driver["car"]}\n{driver["best"].pretty_time} | {driver["average"]}\n\n'
                    position += 1
                    if position > result_limit:
                        break
                    
                if len(new_output.split('\n')) > 2:
                    output.append(new_output)

            print_side_by_side(output, line_len=50, dynamic_height=True, organize_lengths=True)
            
            if post:
                print_side_by_side(post_msgs, line_len=45)


        def do_teams(self, args):
            teams = {}

            for driver in drivers:
                team = driver.team
                if team not in teams:
                    teams[team] = []
                teams[team].append(driver)

            output = []
            for team in teams:
                temp = f'{colored(team, "green")}\n'
                for driver in teams[team]:
                    temp = f'{temp}  {driver.name} ({driver.division})\n'
                output.append(f'{temp}\n')

            print_side_by_side(output)

                



    terminal = Terminal(Cmd)
    terminal.cmdloop()







if __name__ == '__main__':
    main()