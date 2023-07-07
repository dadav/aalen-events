#!/usr/bin/env python3

import sys
import requests
from typing import Dict
from datetime import timedelta
from dateutil.rrule import rrulestr
from pathlib import Path
from slugify import slugify

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


def create_posts(output: Path, data: Dict, overwrite: bool = False):
    for item in sorted(data, key=lambda i: i["id"]):
        event_dates = rrulestr(item["rule"])
        title = item["title"]
        url = item["url"]
        location = item["location"]
        image = item["image"]["thumb_1230px"] if item["image"] else None
        category = item["category"]["title"] if item["category"] else None
        organiser = item["organiser"]

        for event_date in event_dates:
            post_path = (
                output / str(event_date.year) / str(event_date.month) / str(event_date.day) / f"{slugify(title)}.md"
            )
            if post_path.exists() and not overwrite:
                continue

            post_path.parent.mkdir(exist_ok=True, parents=True)

            with open(post_path, "wt") as p:
                p.write(
                    f"---\ntitle: '{title}'\nauthor: '{organiser}'\ncategories:\n - '{category}'\ndate: {event_date}\n---"
                )


def main() -> int:
    """
    Main routine.

    returns 0 if everything went well and >0 if something failed.
    """
    output = Path(sys.argv[1])
    output.mkdir(exist_ok=True, parents=True)

    posts = create_posts(output, fetch_events_json())

    return ExitCodes.OK


if __name__ == "__main__":
    sys.exit(main())
