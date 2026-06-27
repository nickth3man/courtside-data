"""``EndpointSpec`` dataclass and factory helpers used to build the ``ENDPOINTS`` dict.

The registry (:mod:`courtside_data.endpoints._registry`) stays focused on
its per-domain wiring and the per-endpoint ``output.columns``/``schemas``
imports; the shared spec type and factories live here.

"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from courtside_data._frozen import frozen_slot
from courtside_data.endpoints._error_mapping import NOT_FOUND
from courtside_data.endpoints._metadata import EndpointKind
from courtside_data.errors import (
    InvalidPlayer,
    InvalidSeason,
    InvalidTeam,
)

if TYPE_CHECKING:
    from courtside_data.endpoints._metadata import EndpointMetadata
    from courtside_data.endpoints._workflow import WorkflowSpec
    from courtside_data.schemas._base import BRRow


@frozen_slot
class EndpointSpec:
    """Registry spec for one endpoint.

    Table lookup order in ``HTTPService.fetch_table``:
    1. ``table_id`` via a CSS ``table#<id>`` query (if set),
    2. ``fallback_table_ids`` via CSS ``table#<id>`` queries (if set),
    3. ``commented_table_id`` via :func:`extract_commented_table` (if set),
    4. transaction-list fallback (if ``transaction_list_fallback``),
    5. otherwise an empty result.
    """

    path: str
    # Every registered endpoint must declare the Pydantic row model that
    # validates extracted rows before output formatting.
    row_model: type[BRRow]
    # Taxonomy descriptor. Drives runtime dispatch: workflow endpoints route
    # through the workflow executor; generic-table endpoints route through
    # the generic fetch-table pipeline.
    metadata: EndpointMetadata
    # Ordered call-parameter names; defines the positional argument order of
    # the generated HTTPService delegates and client functions.
    params: tuple[str, ...] = ()
    table_id: str | None = None
    fallback_table_ids: tuple[str, ...] = ()
    commented_table_id: str | None = None
    use_header_fallback: bool = False
    transaction_list_fallback: bool = False
    exclude_summary_rows: bool = False
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
    # Optional executable workflow descriptor. Dispatch consumes
    # ``metadata.kind`` to select the workflow executor, then the executor
    # walks this ordered step spec.
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

    @property
    def kind(self) -> EndpointKind:
        """Resolved dispatch kind for this endpoint.

        Runtime dispatch, parameter coercion, and generic-table guards read
        this field directly.
        """
        return self.metadata.kind


def _endpoint(
    path: str,
    *,
    params: tuple[str, ...],
    error: type[Exception] | None,
    error_params: tuple[str, ...],
    row_model: type[BRRow],
    metadata: EndpointMetadata,
    error_status_codes: tuple[int, ...] = NOT_FOUND,
    table_id: str | None = None,
    fallback_table_ids: tuple[str, ...] = (),
    commented_table_id: str | None = None,
    use_header_fallback: bool = False,
    transaction_list_fallback: bool = False,
    exclude_summary_rows: bool = False,
    projection: tuple[str, ...] | None = None,
    csv_columns: Sequence[str] | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    value_column: bool = False,
    workflow: WorkflowSpec | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        path=path,
        row_model=row_model,
        metadata=metadata,
        params=params,
        table_id=table_id,
        fallback_table_ids=fallback_table_ids,
        commented_table_id=commented_table_id,
        use_header_fallback=use_header_fallback,
        transaction_list_fallback=transaction_list_fallback,
        exclude_summary_rows=exclude_summary_rows,
        projection=projection,
        csv_columns=csv_columns,
        error=error,
        error_params=error_params,
        error_status_codes=error_status_codes,
        min_year=min_year,
        max_year=max_year,
        value_column=value_column,
        workflow=workflow,
    )


# Default floor for the league-wide season endpoints. 1947 is the first
# BAA/NBA season Basketball-Reference tracks for the historical tables
# (per-game, totals, per-36); per-100-possessions was introduced in 1974
# and overrides this with ``min_year=1974`` at its registration.
_DEFAULT_SEASON_MIN_YEAR = 1947


def _season(path: str, params: tuple[str, ...] = ("season_end_year",), **overrides: Any) -> EndpointSpec:
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
) -> EndpointSpec:
    return _endpoint(
        path,
        params=params,
        error=InvalidTeam,
        error_params=("team_abbreviation",),
        **overrides,
    )


def _player(path: str, params: tuple[str, ...] = ("player_identifier",), **overrides: Any) -> EndpointSpec:
    return _endpoint(
        path,
        params=params,
        error=InvalidPlayer,
        error_params=("player_identifier",),
        **overrides,
    )
