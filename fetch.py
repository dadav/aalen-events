#!/usr/bin/env python3

import sys
import requests
from datetime import timedelta
from icalendar import Calendar, Event, vRecur, vCalAddress, vDatetime

CALENDAR_URL = "https://www.aalen.de/api/EventApiRules.php"


class ExitCodes:
    OK: int = 0
    ERR: int = 1


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
    cal.add("prodid", "-//Aalen2ics//https://github.com/dadav/aalen2ics//")
    cal.add("version", "2.0")

    for jevent in sorted(json_data, key=lambda i: i["id"]):
        event = Event()
        rule_data = jevent["rule"].split("\n")
        if len(rule_data) != 2:
            continue
        start, rule = [x.split(":", maxsplit=1)[1] for x in rule_data]
        rule = vRecur.from_ical(rule)

        if "title" in jevent:
            event.add("summary", jevent["title"])

        event.add("dtstart", vDatetime.from_ical(start, timezone="Europe/Berlin"))
        event.add("rrule", rule)
        if "url" in jevent:
            event.add("url", jevent["url"])
            event.add("description", jevent["url"])

        if "location" in jevent:
            event.add("location", jevent["location"])

        if "organiser" in jevent:
            event.add("organizer", vCalAddress.from_ical(jevent["organiser"]))

        if "timeStart" in jevent and "timeEnd" in jevent:
            try:
                duration = timedelta(
                    hours=int(jevent["timeEnd"].split(":")[0]),
                    minutes=int(jevent["timeEnd"].split(":")[1]),
                ) - timedelta(
                    hours=int(jevent["timeStart"].split(":")[0]),
                    minutes=int(jevent["timeStart"].split(":")[1]),
                )
                event.add("duration", duration)
            except Exception:
                pass

        cal.add_component(event)

    return cal


def main() -> int:
    """
    Main routine.

    returns 0 if everything went well and >0 if something failed.
    """
    out = sys.argv[1]

    events_json = fetch_events_json()
    events_ics = json_to_ical(events_json)

    with open(out, "wb") as icsfile:
        icsfile.write(events_ics.to_ical())

    return ExitCodes.OK


if __name__ == "__main__":
    sys.exit(main())
