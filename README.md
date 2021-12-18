# comical

Command line icalendar utility.

This program can manage icalendar data from and to ICS, CSV an Json files.

## Examples

Quick view of an ICS file:
```bash
$ comical --input samples/calendar_test.ics
DTSTART                    SUMMARY
-------------------------  ---------
2021-07-20 20:00:00+00:00  Event 2
2021-07-14 17:00:00+00:00  Event 1
```

Select properties from a calendar events, sort them and ouptut them in a CSV file:
```bash
$ comical --input samples/calendar_test.ics --select DTSTART,SUMMARY,LOCATION --order-by DTSTART,DTEND --format csv > mycalendar.csv

$ cat mycalendar.csv
DTSTART,SUMMARY,LOCATION
2021-07-14 17:00:00+00:00,Event 1,"Place de la Bastille, Paris"
2021-07-20 20:00:00+00:00,Event 2,
```

Loads a CSV into an ICS file (not supported yet):
```bash
$ comical --input mycalendar.csv --format ics > mycalendar.ics
```

## Parameters

`--input` File to read

`--select PROPERTIES_NAMES` Comma separated list of properties to extract from the input file. Defaults depends to format

`--order-by PROPERTIES_NAMES` Comma separated list of properties to sort on the result

`--format {pretty,csv,json,ics}` Output format. Defaults to pretty

`-h --help` Output some help and exit

## Development status

This is still under heavy development and compatibility is likely to break in the future.

- [x] Load an ICS file to a DataFrame
- [x] Outut to CSV or Json
- [x] Output to a pretty table
- [x] Order by list of columns
- [x] Load CSV and Json
- [ ] Output to ICS format
- [ ] Proper module architecture
- [ ] Detect input file encoding for vText properties
- [ ] Support for descending order by
- [ ] Unit tests
- [ ] Handle VALARM components
- [ ] Proper error management
- [ ] Load multiple files
- [ ] --where parameter to filter the events
- [ ] config.cfg for package creation, linting and tests
- [ ] Programmable pipeline

# Disclaimer

This program offers no warranty. See license for details.

Please note data read from the input file is interpreted and might undego transfomation.

# License

Copyright © 2021 Pierre Faivre. This is free software, and may be redistributed under the terms specified in the LICENSE file.
