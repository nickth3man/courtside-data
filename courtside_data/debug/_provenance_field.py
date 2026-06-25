"""Field-level provenance records.

Per-field classification of how a Pydantic row-model field's final value
relates to the raw parser row, the source table, the schema defaults, and
the validators that ran. Also exposes the small helpers used to compute
the per-field ``provenance_reason`` constant.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import AliasChoices, AliasPath
from pydantic_core import PydanticUndefined

from courtside_data.debug._provenance_constants import (
    _DASH_OR_SENTINEL_VALUES,
    PROVENANCE_DEBUG_UNAVAILABLE,
    PROVENANCE_PARSER_EMITTED_VALUE,
    PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN,
    PROVENANCE_SCHEMA_DEFAULT_USED,
    PROVENANCE_SOURCE_CELL_BLANK,
    PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL,
    PROVENANCE_SOURCE_COLUMN_ABSENT,
    PROVENANCE_SOURCE_VALUE_PRESENT,
    PROVENANCE_UNKNOWN,
    PROVENANCE_VALIDATOR_COERCED_TO_NONE,
    PROVENANCE_VALIDATOR_TRANSFORMED_VALUE,
    PROVENANCE_WORKFLOW_PARSER_METADATA_UNAVAILABLE,
    PROVENANCE_WORKFLOW_PARSER_VALUE,
    ProvenanceReason,
)
from courtside_data.debug._provenance_types import (
    ProvenanceContext,
    SourceCell,
    SourceTableSnapshot,
)


def accepted_input_keys(field_name: str, field_info: Any, *, include_field_name: bool = True) -> list[str]:
    """Return the flat parser keys Pydantic will accept for a model field."""
    keys: list[str] = []

    def add(value: object) -> None:
        if isinstance(value, str) and value not in keys:
            keys.append(value)

    alias = getattr(field_info, "validation_alias", None)
    if isinstance(alias, str):
        add(alias)
    elif isinstance(alias, AliasChoices):
        for choice in alias.choices:
            if isinstance(choice, str):
                add(choice)
            elif isinstance(choice, AliasPath) and len(choice.path) == 1:
                add(str(choice.path[0]))
    elif isinstance(alias, AliasPath) and len(alias.path) == 1:
        add(str(alias.path[0]))

    if include_field_name:
        add(field_name)
    return keys


def expected_model_source_keys(row_model: Any) -> list[str]:
    keys: list[str] = []
    for field_name, field_info in row_model.model_fields.items():
        for key in accepted_input_keys(field_name, field_info, include_field_name=False) or [field_name]:
            if key not in keys:
                keys.append(key)
    return keys


def build_field_provenance_records(
    *,
    endpoint_name: str | None,
    endpoint_params: Mapping[str, Any] | None,
    row_model: Any,
    raw_rows: Sequence[Mapping[str, Any]],
    validated_rows: Sequence[Any],
    kept_row_indices: Sequence[int],
    context: ProvenanceContext | None,
    workflow: bool,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    snapshot = context.source_snapshot if context is not None else None

    for validated, raw_index in zip(validated_rows, kept_row_indices, strict=False):
        parser_row = raw_rows[raw_index] if raw_index < len(raw_rows) else {}
        for field_name, field_info in row_model.model_fields.items():
            records.append(
                _field_record(
                    endpoint_name=endpoint_name,
                    endpoint_params=endpoint_params,
                    row_model=row_model,
                    field_name=field_name,
                    field_info=field_info,
                    parser_row=parser_row,
                    raw_row_index=raw_index,
                    validated=validated,
                    snapshot=snapshot,
                    workflow=workflow,
                )
            )
    return records


def _field_record(
    *,
    endpoint_name: str | None,
    endpoint_params: Mapping[str, Any] | None,
    row_model: Any,
    field_name: str,
    field_info: Any,
    parser_row: Mapping[str, Any],
    raw_row_index: int,
    validated: Any,
    snapshot: SourceTableSnapshot | None,
    workflow: bool,
) -> dict[str, Any]:
    aliases = accepted_input_keys(field_name, field_info)
    source_aliases = accepted_input_keys(field_name, field_info, include_field_name=False) or [field_name]
    matched_key = next((key for key in aliases if key in parser_row), None)
    pydantic_input_present = matched_key is not None
    pydantic_input_value = parser_row.get(matched_key) if matched_key is not None else None
    final_value = getattr(validated, field_name, None)
    schema_default_used = not pydantic_input_present and _field_has_default(field_info)
    source_key = _matched_source_key(source_aliases, snapshot)
    source_column_present: bool | None
    source_cell: SourceCell | None = None
    if snapshot is None:
        source_column_present = None
    elif source_key is None:
        source_column_present = False
    else:
        source_column_present = True
        source_cell = snapshot.cell(raw_row_index, source_key)

    validator_coerced_to_none = pydantic_input_present and final_value is None and not _is_blank(pydantic_input_value)
    validator_transformed = (
        pydantic_input_present and final_value is not None and _value_changed(pydantic_input_value, final_value)
    )
    provenance_reason = _classify_field_reason(
        workflow=workflow,
        source_column_present=source_column_present,
        source_cell=source_cell,
        pydantic_input_present=pydantic_input_present,
        pydantic_input_value=pydantic_input_value,
        final_value=final_value,
        schema_default_used=schema_default_used,
        validator_coerced_to_none=validator_coerced_to_none,
        validator_transformed=validator_transformed,
    )

    return {
        "endpoint_name": endpoint_name,
        "params": dict(endpoint_params or {}),
        "row_index": raw_row_index,
        "field_name": field_name,
        "model_field_name": field_name,
        "row_model": getattr(row_model, "__name__", None),
        "validation_alias": source_aliases,
        "accepted_input_keys": aliases,
        "matched_input_key": matched_key,
        "source_table_id": snapshot.source_table_id if snapshot is not None else None,
        "source_column_present": source_column_present,
        "source_data_stat": source_cell.data_stat if source_cell is not None else source_key,
        "source_header_text": source_cell.header_text if source_cell is not None else None,
        "source_cell_raw": source_cell.raw_text if source_cell is not None else None,
        "parsed_row_value": pydantic_input_value,
        "pydantic_input_present": pydantic_input_present,
        "pydantic_input_value": pydantic_input_value,
        "final_value": final_value,
        "schema_default_used": schema_default_used,
        "validator_coerced_to_none": validator_coerced_to_none,
        "validator_transformed": validator_transformed,
        "validator_transformation_reason": PROVENANCE_VALIDATOR_TRANSFORMED_VALUE if validator_transformed else None,
        "provenance_reason": provenance_reason,
    }


def _classify_field_reason(
    *,
    workflow: bool,
    source_column_present: bool | None,
    source_cell: SourceCell | None,
    pydantic_input_present: bool,
    pydantic_input_value: Any,
    final_value: Any,
    schema_default_used: bool,
    validator_coerced_to_none: bool,
    validator_transformed: bool,
) -> ProvenanceReason:
    if workflow:
        if pydantic_input_present:
            return PROVENANCE_WORKFLOW_PARSER_VALUE
        if schema_default_used:
            return PROVENANCE_SCHEMA_DEFAULT_USED
        return PROVENANCE_WORKFLOW_PARSER_METADATA_UNAVAILABLE

    if source_column_present is False:
        return PROVENANCE_SOURCE_COLUMN_ABSENT
    if source_column_present is True and not pydantic_input_present:
        return PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN
    if not pydantic_input_present:
        if schema_default_used:
            return PROVENANCE_SCHEMA_DEFAULT_USED
        if source_column_present is None:
            return PROVENANCE_DEBUG_UNAVAILABLE
        return PROVENANCE_UNKNOWN

    if source_cell is not None and final_value is None:
        if _is_blank(source_cell.raw_text):
            return PROVENANCE_SOURCE_CELL_BLANK
        if _is_dash_or_sentinel(source_cell.raw_text):
            return PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL
    if final_value is None and _is_blank(pydantic_input_value):
        return PROVENANCE_SOURCE_CELL_BLANK
    if final_value is None and _is_dash_or_sentinel(pydantic_input_value):
        return PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL
    if validator_coerced_to_none:
        return PROVENANCE_VALIDATOR_COERCED_TO_NONE
    if validator_transformed:
        return PROVENANCE_VALIDATOR_TRANSFORMED_VALUE
    if source_column_present is None:
        return PROVENANCE_PARSER_EMITTED_VALUE
    return PROVENANCE_SOURCE_VALUE_PRESENT


def _field_has_default(field_info: Any) -> bool:
    if getattr(field_info, "default", PydanticUndefined) is not PydanticUndefined:
        return True
    return getattr(field_info, "default_factory", None) is not None


def _matched_source_key(source_aliases: Sequence[str], snapshot: SourceTableSnapshot | None) -> str | None:
    if snapshot is None:
        return None
    source_keys = snapshot.source_keys
    return next((key for key in source_aliases if key in source_keys), None)


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    return str(value).replace("\xa0", " ").strip() == ""


def _is_dash_or_sentinel(value: Any) -> bool:
    return str(value).replace("\xa0", " ").strip().casefold() in _DASH_OR_SENTINEL_VALUES


def _value_changed(input_value: Any, final_value: Any) -> bool:
    if input_value == final_value:
        return False
    return str(input_value).strip() != str(final_value).strip()
