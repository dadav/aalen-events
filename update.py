#!/usr/bin/env python3

import sys
import requests
from typing import Dict
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
        title = item["title"].replace("'", '"')
        url = item.get("url", "")
        location = item.get("location", "")
        image = item["image"]["thumb_600px"] if item["image"] else "/images/platzhalter.png"
        category = item["category"]["title"] if item["category"] else "Keine"
        organiser = item.get("organiser", "")
        featured = item["highlight"] or item["topevent"]
        canceled = item.get("canceled", "")
        starttime = item["timeStart"] if item["timeValid"] else "00:00"
        endtime = item["timeEnd"] if item["timeValid"] else "23:59"

        for event_date in event_dates:
            post_path = (
                output / str(event_date.year) / str(event_date.month) / str(event_date.day) / f"{slugify(title)}.md"
            )
            if post_path.exists() and not overwrite:
                continue

            post_path.parent.mkdir(exist_ok=True, parents=True)

            content = f"[Mehr Details]({url})"

            with open(post_path, "wt") as p:
                event_txt = (
                    "---\n"
                    f"title: '{title}'\n"
                    f"author: '{organiser}'\n"
                    f"thumbnail: '{image}'\n"
                    "categories:\n"
                    f"  - '{category}'\n"
                    f"date: {event_date.isoformat()}\n"
                    f"featured: {featured}\n"
                    f"canceled: {canceled}\n"
                    f"location: '{location}'\n"
                    f"starttime: '{starttime}'\n"
                    f"endtime: '{endtime}'\n"
                    f"expireDate: '{endtime}'\n"
                    "---\n"
                    f"{content}"
                )

                p.write(event_txt)


def main() -> int:
    """
    Main routine.

    returns 0 if everything went well and >0 if something failed.
    """
    output = Path(sys.argv[1])
    output.mkdir(exist_ok=True, parents=True)

    create_posts(output, fetch_events_json())

    return ExitCodes.OK


if __name__ == "__main__":
    sys.exit(main())
