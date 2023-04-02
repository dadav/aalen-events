#!/usr/bin/env python3

import sys
import requests
from icalendar import Calendar, Event


CALENDAR_URL = 'https://www.aalen.de/api/EventApiRules.php'


def fetch_events_json() -> dict:
    """
    Fetches the events in json format.
    Raises an error if something goes wrong.
    """
    res = requests.get(CALENDAR_URL, timeout=30)
    res.raise_for_status()
    return res.json()


def json_to_ical(json_data: dict) -> Calendar:
    """
    Converts the given json events to ical events.

    Returns a calendar.
    """
    cal = Calendar()

    for jevent in json_data:
        event = Event()
        rule_data = jevent['rule'].split('\n')
        assert len(rule_data) == 2
        start, rule = rule_data
        event.add('title', jevent['title'])
        event.add('dstart', start.split(':')[1])
        event.add('rrule', rule)
        cal.add_component(event)

    return cal


def main() -> int:
    """
    Main routine.

    returns 0 if everything went well and >0 if something failed.
    """
    events_json = fetch_events_json()
    events_ics = json_to_ical(events_json)
    print(events_ics.to_ical().decode('utf-8'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
