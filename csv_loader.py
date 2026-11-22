"""Reading CSV files into flight records and error messages."""

import csv
import os

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records: list[dict] = []
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()

    for path in paths:
        file_name = os.path.basename(path)
        with open(path, encoding="utf-8-sig") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                if line_number == 1:
                    continue
                line = raw_line.rstrip("\r\n")
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                try:
                    fields = next(csv.reader([line]))
                except csv.Error:
                    errors.append(f"{file_name}:{line_number}: WRONG_FIELD_COUNT | {line}")
                    continue

                code = validate_row(fields, airports)
                if code is not None:
                    errors.append(f"{file_name}:{line_number}: {code} | {line}")
                    continue

                record = to_record(fields)
                key = (record["flight_id"], record["departure_datetime"])
                if key in seen:
                    errors.append(f"{file_name}:{line_number}: DUPLICATE_FLIGHT | {line}")
                    continue

                seen.add(key)
                records.append(record)

    return records, errors