"""CSV column contracts for standings Basketball-Reference endpoints.

Covers the conference-division standings and the day-by-day standings tables.
The ``standings`` endpoint is a custom route that produces typed values from
the legacy parser, while ``standings_by_date`` flows through the generic
table pipeline and produces raw ``data-stat``-keyed string dicts.
"""

STANDINGS_COLUMNS_NAMES = [
    "team",
    "wins",
    "losses",
    "division",
    "conference",
]

STANDINGS_BY_DATE_COLUMN_NAMES = [
    "conference",
    "date",
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
    "tenth",
    "eleventh",
    "twelfth",
    "thirteenth",
    "fourteenth",
    "fifteenth",
]
