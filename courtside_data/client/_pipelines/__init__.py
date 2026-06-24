"""Validation pipelines for the client runtime.

Private subpackage (leading underscore). The two modules here hold the
two validation paths:

- :mod:`courtside_data.client._pipelines.pydantic` — row_model validation
  with :class:`SchemaDriftError` wrapping and projection.
- :mod:`courtside_data.client._pipelines.legacy` — the dict-based path
  that coerces/validates raw values for endpoints without a Pydantic
  row model.

Output formatting stays in :mod:`courtside_data.client._runtime`; each
pipeline returns ``(data, csv_column_names)`` and the runner dispatches
to the debug envelope or :func:`_format_output` based on flags.
"""
