#!/usr/bin/env python3

import urllib.request
import json
from typing import *
from dateutil import parser
from datetime import datetime
from time import sleep


API_TOKEN: str = "TODO"  # like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" (hex)
ORIGIN_ID: str = "TODO" # like: "0000000" (dec)
DESTINATION_ID: str = "TODO" # like: "0000000" (dec)

API_REQUEST_TRIP: str = f"https://www.rmv.de/hapi/trip?originId={ORIGIN_ID}&destId={DESTINATION_ID}&accessId={API_TOKEN}&format=json"
API_REQUEST_DEP: str = f"https://www.rmv.de/hapi/departureBoard?id={ORIGIN_ID}&direction={DESTINATION_ID}&accessId={API_TOKEN}&format=json" #&time=23%3A59


def get_json_data(source_url: str):
    with urllib.request.urlopen(source_url) as url:
        data: str = url.read().decode()
    return json.loads(data)


def filter_data_trip(data, exclude_destinations: Set[str] = []) -> Iterable[Tuple[float, str, str]]:
    for element in data['Trip']:
        option = element['LegList']['Leg'][0]
        try:
            time = time_converter(option['Origin']['date'], option['Origin']['time'])
        except ValueError:
            # ignore negative time deltas (departures in the past are irrelevant)
            continue

        line_name = option['Product']['line']
        destination = option['direction']

        if destination not in exclude_destinations:
            yield time, line_name, destination


def filter_data_dep(data, exclude_destinations: Set[str] = []) -> Iterable[Tuple[float, str, str]]:
    for element in data['Departure']:
        try:
            time = time_converter(element['date'], element['time'])
        except ValueError:
            # ignore negative time deltas (departures in the past are irrelevant)
            continue

        line_name = element['Product']['line']
        destination = element['direction'].split(None, 1)[1]

        if destination not in exclude_destinations:
            yield time, line_name, destination


def time_converter(rmv_date: str, rmv_time: str) -> float:
    rmv_date_time = f"{rmv_date} {rmv_time}"
    time_offset = parser.parse(rmv_date_time) - datetime.now()
    if time_offset.days < 0:
        raise ValueError('Given time is in the past')
    else:
        return float(time_offset.seconds)


def print_to_console(data: List[Tuple[float, str, str]], num_entries: int = 5) -> None:
    print("---------------")
    for time, line, destination in data[:num_entries]:
        minutes = time/60
        print(f"{minutes:3.0f}\t\t{line}\t\t{destination}")
    print("---------------")
