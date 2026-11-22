"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "241AEC014"
FIRST_NAME = "Ahmet"
LAST_NAME = "KAMCICI"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate flight CSV files, store them as JSON and run queries."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", dest="input_file", metavar="FILE", help="parse one CSV file")
    source.add_argument("-d", dest="input_folder", metavar="FOLDER", help="parse all CSV files in a folder")
    source.add_argument("-j", dest="json_file", metavar="FILE", help="load an existing JSON database")
    parser.add_argument("-a", dest="airports", metavar="FILE", help="airport list file")
    parser.add_argument("-o", dest="output", metavar="FILE", help="output path for the JSON database")
    parser.add_argument("-q", dest="query_file", metavar="FILE", help="JSON file with queries")
    parser.add_argument("-r", dest="response_folder", metavar="FOLDER", default=".", help="folder for the response file")
    return parser


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.json_file is None and args.airports is None:
        parser.error("-a is required with -i and -d")
    if args.json_file is not None and args.output is not None:
        parser.error("-o cannot be used with -j")
    return args


def _read_json(path: str):
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


def _write_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def _csv_paths(folder: str) -> list[str]:
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"folder not found: {folder}")
    names = sorted(
        name
        for name in os.listdir(folder)
        if name.endswith(".csv") and os.path.isfile(os.path.join(folder, name))
    )
    if not names:
        raise FileNotFoundError(f"no .csv files in folder: {folder}")
    return [os.path.join(folder, name) for name in names]


def _load_database(path: str) -> list[dict]:
    data = _read_json(path)
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError(f"{path} is not a JSON array of objects")
    return data


def _attach_handler(logger: logging.Logger, log_path: str) -> logging.Handler:
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    logger.addHandler(handler)
    return handler


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    # TODO: parse arguments with argparse (-i, -d, -j, -a, -o, -q, -r).
    # TODO: load or parse the data, write the database and errors.log.
    # TODO: run the queries and write the response file.
    # Remember: remove and close the logging handler before returning,
    # also when returning early because of an error (use try/finally).
    try:
        args = _parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    logger = logging.getLogger("flight_parser")
    handler = None
    try:
        if args.json_file is not None:
            db = _load_database(args.json_file)
        else:
            db_path = args.output or "db.json"
            airports = load_airports(args.airports)
            if args.input_file is not None:
                paths = [args.input_file]
            else:
                paths = _csv_paths(args.input_folder)
            log_dir = os.path.dirname(os.path.abspath(db_path))
            handler = _attach_handler(logger, os.path.join(log_dir, "errors.log"))
            db, errors = parse_files(paths, airports)
            for message in errors:
                logger.warning(message)
            logger.info("valid rows: %d, invalid rows: %d", len(db), len(errors))
            _write_json(db_path, db)
            print(f"Valid flights: {len(db)}, invalid rows: {len(errors)}")

        if args.query_file is not None:
            queries = _read_json(args.query_file)
            if not isinstance(queries, (dict, list)):
                raise ValueError(f"{args.query_file} must hold a query object or an array")
            responses = run_queries(db, queries)
            stamp = datetime.now().strftime("%Y%m%d_%H%M")
            name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json"
            _write_json(os.path.join(args.response_folder, name), responses)
    except (OSError, ValueError) as exc:
        print("Error: " + " ".join(str(exc).split()), file=sys.stderr)
        return 1
    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())