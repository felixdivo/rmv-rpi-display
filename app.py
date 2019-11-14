#!/usr/bin/env python3

from threading import Thread
from time import sleep

from rmv_api import get_json_data, API_REQUEST_DEP, filter_data_dep, print_to_console


def main(show_on_display: bool = True):

    if show_on_display:
        from display import Display2in9
        display = Display2in9()

        def update_time_loop():
            while True:
                display.update_time()

        global thread  # this keeps it from getting GC'ed
        thread = Thread(target=update_time_loop)
        thread.daemon = True
        thread.start()

    while True:
        try:
            data = get_json_data(API_REQUEST_DEP)
            exclusion = set()  # empty in this example
            lines = list(filter_data_dep(data, exclude_destinations=exclusion))  # or filter_data_trip(data)

        except Exception as e:
            # do an update to not break the display
            lines = [(-1.0, "Err", str(e))]
            print(f"Error getting/parsing the JSON data from the RMV API:\n{e}")

        else:
            print_to_console(lines)

        if show_on_display:
            display.set_lines_of_text(lines)

        sleep(30.0)  # in seconds


if __name__ == '__main__':
    sleep(30) # wait for the internet connection to be established
    main(show_on_display=True)
