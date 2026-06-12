"""Inherited parsing stack for the original (pre-registry) endpoints.

The classes in here serve the handful of endpoints that predate the
``courtside_data.endpoints`` registry: standings, box scores, schedule,
play-by-play, season totals, and search. They produce richer typed values
(domain enums, computed fields) through dedicated page objects
(``legacy.html``) and chains of small parsers (``legacy.parsers``).

New endpoints should not add to this package — declare a
:class:`~courtside_data.endpoints.TableEndpoint` in the registry and let
``courtside_data.tables.GenericTable`` handle extraction instead.
"""
