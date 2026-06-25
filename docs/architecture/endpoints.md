# Endpoint Runtime

`courtside_data.endpoints.ENDPOINTS` is the source of truth for endpoint behavior. Each entry is an `EndpointSpec` with URL shape, params, table hints, output columns, error mapping, optional row model, `EndpointMetadata`, and, for workflow endpoints, a `WorkflowSpec`.

## EndpointMetadata

`EndpointMetadata` describes the endpoint's domain and runtime shape:

- `domain` drives grouping in docs, fixture reporting, and debug probe summaries.
- `kind` is the dispatch switch. `generic_table` routes through `GenericEndpointHandler.fetch_table`; `workflow` routes through `parsing.workflows.execute_workflow`.
- `scope`, `request_shape`, `parser_shape`, and `features` describe parameters, fanout, parser shape, diagnostics, and fallback behavior for tests and tooling.

The deprecated `EndpointSpec.custom` property is a compatibility alias for `endpoint.kind is EndpointKind.WORKFLOW`. New code should read `endpoint.kind`.

## WorkflowSpec

Workflow endpoints declare an ordered `WorkflowSpec`. Runtime dispatch enters `WorkflowEndpointHandler`, looks up native step handlers for the endpoint, and executes the `WorkflowStep.id` values in order. Tests assert every `EndpointKind.WORKFLOW` endpoint has a workflow spec and native handler coverage for every declared step.

`CustomEndpointHandler` and `dispatch_custom_endpoint` are retained for compatibility and legacy output comparisons. They are not used for normal execution of registered workflow endpoints.

## Generic Table Path

Generic table endpoints set `EndpointMetadata.kind = EndpointKind.GENERIC_TABLE` and do not declare a workflow spec. The runner calls `GenericEndpointHandler.fetch_table`, which uses `EndpointSpec` table metadata such as `table_id`, `fallback_table_ids`, `commented_table_id`, `transaction_list_fallback`, projection, and value-column normalization. The parsed dict rows then go through the Pydantic row model pipeline when `row_model` is set.

## Workflow Path

Workflow endpoints set `EndpointMetadata.kind = EndpointKind.WORKFLOW` and declare `WorkflowSpec`. The runner performs metadata-driven enum coercion for endpoints marked with `EndpointFeature.ENUM_PARAM_COERCION`, then calls the workflow executor. Workflow steps can fetch one or more pages, branch on redirects/status, parse page-specific structures, merge rows, and emit parser diagnostics. Their output still returns to the same validation, debug-envelope, and output formatting pipeline as generic table endpoints.

## Compatibility Aliases

These names are intentionally retained:

- `TableEndpoint` is an alias of `EndpointSpec`.
- `EndpointSpec.custom` mirrors `EndpointKind.WORKFLOW`.
- `CUSTOM_ENDPOINTS` aliases the workflow endpoint registry.
- `CustomEndpointHandler`, `dispatch_custom_endpoint`, and `custom_service_dispatch` remain available for compatibility imports, trace consumers, and tests that compare legacy parser output.
