"""``TableEndpoint`` dataclass and factory helpers used to build the ``ENDPOINTS`` dict.

The registry (:mod:`courtside_data.endpoints._registry`) stays focused on
its per-domain wiring and the per-endpoint ``output.columns``/``schemas``
imports; the shared spec type and factories live here.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from courtside_data.endpoints._error_mapping import NOT_FOUND
from courtside_data.errors import (
    InvalidPlayer,
    InvalidSeason,
    InvalidTeam,
)

if TYPE_CHECKING:
    from courtside_data.endpoints._metadata import EndpointMetadata
    from courtside_data.endpoints._workflow import WorkflowSpec
    from courtside_data.schemas._base import BRRow


@dataclass(frozen=True, slots=True)
class TableEndpoint:
    """Spec for one generic table endpoint.

    Table lookup order in ``HTTPService.fetch_table``:
    1. ``table_id`` via a CSS ``table#<id>`` query (if set),
    2. ``fallback_table_ids`` via CSS ``table#<id>`` queries (if set),
    3. ``commented_table_id`` via :func:`extract_commented_table` (if set),
    4. transaction-list fallback (if ``transaction_list_fallback``),
    5. otherwise an empty result.
    """

    path: str
    # Ordered call-parameter names; defines the positional argument order of
    # the generated HTTPService delegates and client functions.
    params: tuple[str, ...] = ()
    table_id: str | None = None
    fallback_table_ids: tuple[str, ...] = ()
    commented_table_id: str | None = None
    use_header_fallback: bool = False
    transaction_list_fallback: bool = False
    exclude_summary_rows: bool = False
    # True for endpoints with a bespoke HTTPService method (e.g. multi-request);
    # fetch_table() must not be used for these.
    custom: bool = False
    # If set, the runner validates each extracted row with this BRRow subclass
    # via the Pydantic pipeline. Endpoints with row_model=None use the
    # dict-based coerce_data/validate_rows path instead.
    row_model: type[BRRow] | None = None
    # When set, fetch_table() projects each row down to exactly these keys
    # (missing keys become empty strings).
    projection: tuple[str, ...] | None = None
    csv_columns: Sequence[str] | None = None
    error: type[Exception] | None = None
    error_params: tuple[str, ...] = ()
    error_status_codes: tuple[int, ...] = NOT_FOUND
    # Valid ``season_end_year`` range enforced by the contract test. None
    # means "no constraint declared"; the default ``min_year=1947`` on
    # :func:`_season` covers most league endpoints. Set per-endpoint when BR
    # rejects years outside a narrower window (e.g. per-100-possessions
    # was introduced in 1974). Runtime validation is intentionally NOT added
    # — this metadata is consumed by ``tests/test_manifest_param_contract.py``
    # to prevent offline fixtures from drifting below the live floor.
    min_year: int | None = None
    max_year: int | None = None
    # When True, ``fetch_table()`` renames the rightmost non-text column of
    # each row to ``value`` after extraction. Used by the leaders endpoints
    # whose stat column header rotates with the active category (e.g. ``per``,
    # ``pts``, ``ast``). See :meth:`GenericTable._normalize_value_column`.
    value_column: bool = False
    # Optional taxonomy descriptor. Describes the endpoint's intended shape
    # without affecting runtime behaviour. Endpoints are annotated
    # incrementally; ``None`` means "not yet described".
    metadata: EndpointMetadata | None = None
    # Optional documentation-only workflow descriptor for custom endpoint
    # handlers. Dispatch does not consume this field.
    workflow: WorkflowSpec | None = None

    def error_mappings(self, params: dict[str, object]) -> dict[int, Callable[[], Exception]] | None:
        """Build the per-call ``{status_code: exception_factory}`` mapping."""
        if self.error is None:
            return None
        error = self.error
        bound = {name: params[name] for name in self.error_params}

        def factory() -> Exception:
            return error(**bound)

        return dict.fromkeys(self.error_status_codes, factory)


def _endpoint(
    path: str,
    *,
    params: tuple[str, ...],
    error: type[Exception] | None,
    error_params: tuple[str, ...],
    error_status_codes: tuple[int, ...] = NOT_FOUND,
    table_id: str | None = None,
    fallback_table_ids: tuple[str, ...] = (),
    commented_table_id: str | None = None,
    use_header_fallback: bool = False,
    transaction_list_fallback: bool = False,
    exclude_summary_rows: bool = False,
    custom: bool = False,
    row_model: type[BRRow] | None = None,
    projection: tuple[str, ...] | None = None,
    csv_columns: Sequence[str] | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    value_column: bool = False,
    metadata: EndpointMetadata | None = None,
    workflow: WorkflowSpec | None = None,
) -> TableEndpoint:
    return TableEndpoint(
        path=path,
        params=params,
        table_id=table_id,
        fallback_table_ids=fallback_table_ids,
        commented_table_id=commented_table_id,
        use_header_fallback=use_header_fallback,
        transaction_list_fallback=transaction_list_fallback,
        exclude_summary_rows=exclude_summary_rows,
        custom=custom,
        row_model=row_model,
        projection=projection,
        csv_columns=csv_columns,
        error=error,
        error_params=error_params,
        error_status_codes=error_status_codes,
        min_year=min_year,
        max_year=max_year,
        value_column=value_column,
        metadata=metadata,
        workflow=workflow,
    )


# Default floor for the league-wide season endpoints. 1947 is the first
# BAA/NBA season Basketball-Reference tracks for the historical tables
# (per-game, totals, per-36); per-100-possessions was introduced in 1974
# and overrides this with ``min_year=1974`` at its registration.
_DEFAULT_SEASON_MIN_YEAR = 1947


def _season(path: str, params: tuple[str, ...] = ("season_end_year",), **overrides: Any) -> TableEndpoint:
    defaults: dict[str, Any] = {"min_year": _DEFAULT_SEASON_MIN_YEAR}
    defaults.update(overrides)
    return _endpoint(
        path,
        params=params,
        error=InvalidSeason,
        error_params=("season_end_year",),
        **defaults,
    )


def _team(
    path: str, params: tuple[str, ...] = ("team_abbreviation", "season_end_year"), **overrides: Any
) -> TableEndpoint:
    return _endpoint(
        path,
        params=params,
        error=InvalidTeam,
        error_params=("team_abbreviation",),
        **overrides,
    )


def _player(path: str, params: tuple[str, ...] = ("player_identifier",), **overrides: Any) -> TableEndpoint:
    return _endpoint(
        path,
        params=params,
        error=InvalidPlayer,
        error_params=("player_identifier",),
        **overrides,
    )
