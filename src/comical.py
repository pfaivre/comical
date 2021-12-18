__title__ = 'comical'
__copyright__ = 'Copyright 2021 Pierre Faivre'
__version__ = "0.1.0"

import argparse
import os.path
import sys
from datetime import date, datetime
from typing import Optional

import pandas
import pytz
from icalendar import Calendar
from icalendar.prop import vText
from pandas import DataFrame
from tabulate import tabulate


def load_ics(file_name: str) -> DataFrame:
    with open(file_name, "r") as f:
        content = f.read()
        cal = Calendar.from_ical(content)

    table = []

    for component in cal.walk():
        if component.name == "VEVENT":
            properties = component.property_items()

            dict_component = {}
            for prop in properties:
                prop_name = prop[0]

                # These are not actual properties
                if prop_name in ("BEGIN", "END"):
                    continue

                try:
                    if "CATEGORIES" == prop_name:
                        # CATEGORIES properties have their own way of getting extracted
                        value = component.get(prop_name).to_ical()
                    else:
                        value = component.decoded(prop_name)
                except (KeyError) as ex:
                    # KeyError can happen when the property is embedded un a sub-component like VALARM
                    # We are excluding them for now
                    # TODO: Handle VALARM components
                    pass

                if isinstance(component.get(prop_name), vText):
                    value = value.decode("utf-8")  # TODO: take the encoding of the source file

                # Convert dates to datetimes to allow comparisons
                elif isinstance(value, date) and not isinstance(value, datetime):
                    value = datetime.combine(value, datetime.min.time())
                    timezone = pytz.timezone("UTC")
                    value = timezone.localize(value)

                dict_component[prop_name] = value

            table.append(dict_component)

    return DataFrame(table)


def load_csv(file_name: str) -> DataFrame:
    try:
        df = pandas.read_csv(file_name)
    except pandas.errors.ParserError as ex:
        raise ValueError(f"Unable to read {file_name}: {ex}")

    return df

def load_json(file_name: str) -> DataFrame:
    try:
        df = pandas.read_json(file_name)
    except ValueError as ex:
        raise ValueError(f"Unable to read {file_name}: {ex}")

    return df


def load(file_name: str) -> DataFrame:
    """Loads file into a DataFrame.
    
    Args:
        file_name: path to a file. Can be an ICS file or a CSV or Json listing icalendar events.

    Note:
        Dates will be converted to datetime.
    """
    extension = os.path.splitext(file_name)[1]

    if not os.path.exists(file_name) or not os.path.isfile(file_name):
        raise ValueError(f"File {file_name} is not found")

    if ".ics" == extension:
        df = load_ics(file_name)
    elif ".csv" == extension:
        df = load_csv(file_name)
    elif ".json" == extension:
        df = load_json(file_name)
    else:
        raise NotImplementedError(f"Read {extension} file type")
            
    return df


def select(df: DataFrame, columns: list) -> DataFrame:
    """Limit the DataFrame to the selected columns.

    Args:
        columns: List of columns names to keep.
    """
    return df[columns]


def order_by(df: DataFrame, columns: list) -> DataFrame:
    """Sorts the DataFrame by the given columns

    Args:
        columns: list of columns to sort on, from left to right.
    """
    return df.sort_values(by=columns)


def output_csv(df: DataFrame) -> str:
    """Returns a CSV representation of the DataFrame."""
    return df.to_csv(index=False)


def output_json(df: DataFrame) -> str:
    """Returns a Json representation of the DataFrame."""
    return df.to_json(orient="records", date_format="iso")


def output_pretty(df: DataFrame, columns: Optional[dict] = None) -> str:
    """Returns a human readable table from the data frame."""
    return tabulate(df, headers="keys", showindex=False)


def output_ics(df: DataFrame) -> str:
    # TODO: Export to ICS file format
    raise NotImplementedError("Export to ICS file type")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file.", required=True)
    parser.add_argument("-f", "--format", help="Output format.", 
        choices=["pretty", "csv", "json", "ics"], default="pretty")
    parser.add_argument("--select", help="Comma separated names of columns to select in the output.")
    parser.add_argument("--order-by", help="Comma separated names of properties to sort the ouptut on.")
    args = parser.parse_args()
    
    df = load(args.input)

    if args.order_by:
        df = order_by(df, args.order_by.split(","))

    if args.select:
        df = select(df, args.select.split(","))
    elif "pretty" == args.format:
        # For usability, pretty format defaults to selecting only DTSTART and SUMMARY
        df = select(df, ["DTSTART", "SUMMARY"])

    if ("pretty" == args.format):
        result = output_pretty(df)
    elif ("csv" == args.format):
        result = output_csv(df)
    elif ("json" == args.format):
        result = output_json(df)
    elif ("ics" == args.format):
        result = output_ics(df)

    print(result)


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as ex:
        print(f"Error, feature not supported: {ex}", file=sys.stderr)
        exit(1)
    except Exception as ex:
        print(f"Error: {ex}", file=sys.stderr)
        exit(1)
