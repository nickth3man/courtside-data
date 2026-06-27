"""Validation pipelines for the client runtime.

Private subpackage (leading underscore). The modules here hold the row
validation path and its supporting drop-reason helpers:

- :mod:`courtside_data.client._pipelines.pydantic` — row_model validation
  with :class:`SchemaDriftError` wrapping and projection.

Output formatting stays in :mod:`courtside_data.client._runtime`; each
pipeline returns ``(data, csv_column_names)`` and the runner dispatches
to the debug envelope or :func:`_format_output` based on flags.
"""
