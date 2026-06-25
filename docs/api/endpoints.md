# Endpoints

The `courtside_data.endpoints` module is the declarative registry that
drives both the public `courtside_data.client.*` functions and the
generated CLI subcommand tree. Each entry in
[`ENDPOINTS`][courtside_data.endpoints.ENDPOINTS] is a
[`EndpointSpec`][courtside_data.endpoints.EndpointSpec] dataclass
capturing the URL template, the table locator strategy, the CSV column
contract, the Pydantic row model (if any), the optional column
projection, and the HTTP-status to domain-error mapping.
`TableEndpoint` is retained as a backwards-compatible alias for
`EndpointSpec`; both names are importable from
`courtside_data.endpoints`.

The same registry feeds `GenericEndpointHandler.fetch_table` for
generic-table endpoints (`EndpointKind.GENERIC_TABLE`) and
`execute_workflow` for workflow endpoints (`EndpointKind.WORKFLOW`).
Dispatch is driven by `endpoint.kind`; the legacy `custom` flag is a
read-only compatibility property derived from it (`True` ⇔ `WORKFLOW`).

## Status code constants

::: courtside_data.endpoints.NOT_FOUND
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

::: courtside_data.endpoints.NOT_FOUND_OR_SERVER_ERROR
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

## The `EndpointSpec` dataclass

The full spec for one endpoint. The `error_mappings` method is the
per-call binding that turns a row of `EndpointSpec.error_status_codes`
into a domain-specific exception.

::: courtside_data.endpoints.EndpointSpec
    options:
      show_root_heading: true
      show_root_full_path: false
      members:
        - path
        - params
        - table_id
        - fallback_table_ids
        - commented_table_id
        - use_header_fallback
        - transaction_list_fallback
        - exclude_summary_rows
        - metadata
        - kind
        - row_model
        - projection
        - csv_columns
        - error
        - error_params
        - error_status_codes
        - min_year
        - max_year
        - value_column
        - error_mappings

## `TableEndpoint` alias

`TableEndpoint` is a deprecated backwards-compatible alias for
[`EndpointSpec`][courtside_data.endpoints.EndpointSpec]. Both names are
importable from `courtside_data.endpoints`. New code should use
`EndpointSpec`; `TableEndpoint` is preserved so existing imports
continue to work.

::: courtside_data.endpoints.TableEndpoint
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

## Internal spec builders

These helpers exist to keep the registry terse: `_season`, `_team`, and
`_player` fill in the most common `error` / `error_params` / `min_year`
defaults for endpoints scoped to a single season, a single team, or a
single player respectively.

::: courtside_data.endpoints._endpoint
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

::: courtside_data.endpoints._season
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

::: courtside_data.endpoints._team
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

::: courtside_data.endpoints._player
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

## The `ENDPOINTS` registry

The full dict that the runner, the client, and the CLI all consume. Use
the `list` subcommand (`courtside-data list`) for a live listing.

::: courtside_data.endpoints.ENDPOINTS
    options:
      show_root_heading: true
      show_root_full_path: false
