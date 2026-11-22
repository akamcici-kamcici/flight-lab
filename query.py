"""Running queries against the flight database."""

import re
from datetime import datetime

_RECORD_KEYS = (
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
)
_STRING_KEYS = ("flight_id", "origin", "destination")
_DATETIME_KEYS = ("departure_datetime", "arrival_datetime")
_NUMBER_KEYS = ("price", "min_price")
_ALLOWED_KEYS = set(
    _STRING_KEYS + _DATETIME_KEYS + _NUMBER_KEYS + ("sort_by", "order", "limit")
)
_DATETIME_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}")


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_datetime(value: object) -> bool:
    if not isinstance(value, str) or not _DATETIME_RE.fullmatch(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        return False
    return True


def _is_valid(query: object) -> bool:
    if not isinstance(query, dict):
        return False
    if not set(query).issubset(_ALLOWED_KEYS):
        return False
    for key, value in query.items():
        if key in _STRING_KEYS:
            if not isinstance(value, str):
                return False
        elif key in _DATETIME_KEYS:
            if not _is_datetime(value):
                return False
        elif key in _NUMBER_KEYS:
            if not _is_number(value):
                return False
        elif key == "sort_by":
            if not isinstance(value, str) or value not in _RECORD_KEYS:
                return False
        elif key == "order":
            if value not in ("asc", "desc"):
                return False
        elif key == "limit":
            if not isinstance(value, int) or isinstance(value, bool):
                return False
            if value < 0:
                return False
    if "order" in query and "sort_by" not in query:
        return False
    return True


def _matches(record: dict, query: dict) -> bool:
    for key in _STRING_KEYS:
        if key in query and record[key] != query[key]:
            return False
    departure = query.get("departure_datetime")
    if departure is not None and record["departure_datetime"] < departure:
        return False
    arrival = query.get("arrival_datetime")
    if arrival is not None and record["arrival_datetime"] > arrival:
        return False
    maximum = query.get("price")
    if maximum is not None and record["price"] > maximum:
        return False
    minimum = query.get("min_price")
    if minimum is not None and record["price"] < minimum:
        return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not _is_valid(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = [record for record in db if _matches(record, query)]

    if "sort_by" in query:
        sort_key = query["sort_by"]
        matches = sorted(
            matches,
            key=lambda record: record[sort_key],
            reverse=query.get("order", "asc") == "desc",
        )

    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        return [run_query(db, queries)]
    return [run_query(db, query) for query in queries]