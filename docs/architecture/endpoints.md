# Endpoint Runtime

`courtside_data.endpoints.ENDPOINTS` is the source of truth for endpoint behavior. Each entry is an `EndpointSpec` with URL shape, params, table hints, output columns, error mapping, row model, and `EndpointMetadata`; workflow endpoints also declare a `WorkflowSpec`.

## EndpointMetadata

`EndpointMetadata` describes the endpoint's domain and runtime shape:

- `domain` drives grouping in docs, fixture reporting, and debug probe summaries.
- `kind` is the dispatch switch. `generic_table` routes through `GenericEndpointHandler.fetch_table`; `workflow` routes through `parsing.workflows.execute_workflow`.
- `scope`, `request_shape`, `parser_shape`, and `features` describe parameters, fanout, parser shape, diagnostics, and fallback behavior for tests and tooling.

## WorkflowSpec

Workflow endpoints declare an ordered `WorkflowSpec` with typed `WorkflowStepKind` values. Runtime dispatch enters `WorkflowEndpointHandler`, validates the endpoint's explicit native `WorkflowExecutionBinding`, and executes the `WorkflowStep.id` values in order. Tests assert every `EndpointKind.WORKFLOW` endpoint has a workflow spec, native binding, exact step coverage, and matching result key.

## Generic Table Path

Generic table endpoints set `EndpointMetadata.kind = EndpointKind.GENERIC_TABLE` and do not declare a workflow spec. The runner calls `GenericEndpointHandler.fetch_table`, which uses `EndpointSpec` table metadata such as `table_id`, `fallback_table_ids`, `commented_table_id`, `transaction_list_fallback`, projection, and value-column normalization. The parsed dict rows then go through the endpoint's Pydantic row model pipeline.

## Workflow Path

Workflow endpoints set `EndpointMetadata.kind = EndpointKind.WORKFLOW` and declare `WorkflowSpec`. The runner performs metadata-driven enum coercion for endpoints marked with `EndpointFeature.ENUM_PARAM_COERCION`, then calls the workflow executor. Workflow steps can fetch one or more pages, branch on redirects/status, parse page-specific structures, merge rows, and emit parser diagnostics. Their output still returns to the same validation, debug-envelope, and output formatting pipeline as generic table endpoints.

## Removed Legacy Surface

The standardized endpoint surface no longer exports the previous alias layer.
Use `EndpointSpec`, `EndpointKind`, `WORKFLOW_ENDPOINTS`,
`workflow_execution_bindings()`, `workflow_service_dispatch`,
`endpoint_domain`, and `endpoint_kind` directly.
