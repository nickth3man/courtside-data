"""Tests for the EndpointMetadata taxonomy and its integration with EndpointSpec."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Any

import pytest
from courtside_data.endpoints import (
    ENDPOINTS,
    EndpointDomain,
    EndpointFeature,
    EndpointKind,
    EndpointMetadata,
    EndpointScope,
    EndpointSpec,
    ParserShape,
    RequestShape,
    _endpoint,
    _player,
    _season,
    _team,
)
from courtside_data.schemas._base import BRRow

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_metadata() -> EndpointMetadata:
    return EndpointMetadata(
        domain=EndpointDomain.TEAMS,
        kind=EndpointKind.GENERIC_TABLE,
        scope=EndpointScope.TEAM_SEASON,
        request_shape=RequestShape.SINGLE_REQUEST,
        parser_shape=ParserShape.TABLE,
    )


class _TestRow(BRRow):
    value: str = ""


def _endpoint_spec(
    *,
    path: str = "/foo/bar.html",
    metadata: EndpointMetadata | None = None,
    **overrides: Any,
) -> EndpointSpec:
    return EndpointSpec(
        path=path,
        row_model=_TestRow,
        metadata=metadata or _minimal_metadata(),
        **overrides,
    )


# ---------------------------------------------------------------------------
# EndpointMetadata is frozen (slots dataclass)
# ---------------------------------------------------------------------------


class TestEndpointMetadataFrozen:
    def test_cannot_set_attribute(self) -> None:
        meta = _minimal_metadata()
        attr = "domain"
        with pytest.raises(FrozenInstanceError):
            setattr(meta, attr, EndpointDomain.LEAGUE)

    def test_cannot_delete_attribute(self) -> None:
        meta = _minimal_metadata()
        with pytest.raises(FrozenInstanceError):
            delattr(meta, "domain")

    def test_is_hashable(self) -> None:
        meta = _minimal_metadata()
        assert hash(meta) == hash(meta)
        assert {meta} == {meta}


# ---------------------------------------------------------------------------
# EndpointMetadata equality and defaults
# ---------------------------------------------------------------------------


class TestEndpointMetadataEquality:
    def test_equal_instances(self) -> None:
        a = _minimal_metadata()
        b = _minimal_metadata()
        assert a == b

    def test_features_default_to_empty_frozenset(self) -> None:
        meta = _minimal_metadata()
        assert meta.features == frozenset()
        assert isinstance(meta.features, frozenset)

    def test_with_features(self) -> None:
        meta = EndpointMetadata(
            domain=EndpointDomain.LEAGUE,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE, EndpointFeature.EXCLUDE_SUMMARY_ROWS}),
        )
        assert EndpointFeature.COMMENTED_TABLE in meta.features
        assert EndpointFeature.EXCLUDE_SUMMARY_ROWS in meta.features
        assert len(meta.features) == 2

    def test_features_frozenset_is_immutable(self) -> None:
        meta = _minimal_metadata()
        method = "add"
        with pytest.raises((AttributeError, TypeError)):
            getattr(meta.features, method)(EndpointFeature.COMMENTED_TABLE)


# ---------------------------------------------------------------------------
# StrEnum values are plain strings
# ---------------------------------------------------------------------------


class TestEnumValues:
    def test_endpoint_kind_values_are_strings(self) -> None:
        assert EndpointKind.GENERIC_TABLE == "generic_table"
        assert EndpointKind.WORKFLOW == "workflow"

    def test_endpoint_domain_values_are_strings(self) -> None:
        assert EndpointDomain.LEAGUE == "league"
        assert EndpointDomain.TEAMS == "teams"
        assert EndpointDomain.PLAYERS == "players"

    def test_endpoint_scope_values_are_strings(self) -> None:
        assert EndpointScope.SEASON == "season"
        assert EndpointScope.TEAM_SEASON == "team_season"
        assert EndpointScope.PLAYER == "player"

    def test_request_shape_values_are_strings(self) -> None:
        assert RequestShape.SINGLE_REQUEST == "single_request"
        assert RequestShape.MULTI_REQUEST == "multi_request"

    def test_parser_shape_values_are_strings(self) -> None:
        assert ParserShape.TABLE == "table"
        assert ParserShape.COMMENTED_TABLE == "commented_table"
        assert ParserShape.BRACKET == "bracket"

    def test_endpoint_feature_values_are_strings(self) -> None:
        assert EndpointFeature.COMMENTED_TABLE == "commented_table"
        assert EndpointFeature.EXCLUDE_SUMMARY_ROWS == "exclude_summary_rows"
        assert EndpointFeature.ENUM_PARAM_COERCION == "enum_param_coercion"


# ---------------------------------------------------------------------------
# EndpointSpec accepts metadata
# ---------------------------------------------------------------------------


class TestEndpointSpecAcceptsMetadata:
    def test_metadata_and_row_model_are_required(self) -> None:
        spec_type: Any = EndpointSpec
        with pytest.raises(TypeError):
            spec_type(path="/foo/bar.html")

    def test_metadata_can_be_set(self) -> None:
        meta = _minimal_metadata()
        ep = _endpoint_spec(metadata=meta)
        assert ep.metadata is meta

    def test_table_endpoint_with_metadata_is_frozen(self) -> None:
        meta = _minimal_metadata()
        ep = _endpoint_spec(metadata=meta)
        attr = "metadata"
        with pytest.raises(FrozenInstanceError):
            setattr(ep, attr, None)

    def test_table_endpoint_equality_with_same_metadata(self) -> None:
        meta = _minimal_metadata()
        ep1 = _endpoint_spec(metadata=meta)
        ep2 = _endpoint_spec(metadata=meta)
        assert ep1 == ep2

    def test_table_endpoint_inequality_with_different_metadata(self) -> None:
        meta1 = _minimal_metadata()
        meta2 = EndpointMetadata(
            domain=EndpointDomain.LEAGUE,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        )
        ep1 = _endpoint_spec(metadata=meta1)
        ep2 = _endpoint_spec(metadata=meta2)
        assert ep1 != ep2


# ---------------------------------------------------------------------------
# Dispatch kind
# ---------------------------------------------------------------------------


class TestKindProperty:
    """``kind`` drives dispatch."""

    def test_kind_reflects_metadata_kind(self) -> None:
        meta = _minimal_metadata()
        ep = _endpoint_spec(metadata=meta)
        assert ep.kind is EndpointKind.GENERIC_TABLE

    def test_workflow_metadata_makes_kind_workflow(self) -> None:
        meta = EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.DATE,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        )
        ep = _endpoint_spec(metadata=meta)
        assert ep.kind is EndpointKind.WORKFLOW

    def test_generic_table_metadata_keeps_kind_generic(self) -> None:
        ep = _endpoint_spec(metadata=_minimal_metadata())
        assert ep.kind is EndpointKind.GENERIC_TABLE

    def test_kind_is_consistent_with_metadata_across_registry(self) -> None:
        for name, ep in ENDPOINTS.items():
            assert ep.kind is ep.metadata.kind, name


# ---------------------------------------------------------------------------
# Factories preserve metadata
# ---------------------------------------------------------------------------


class TestFactoriesPreserveMetadata:
    """Each factory must forward ``metadata=`` to the underlying EndpointSpec."""

    def test_endpoint_factory_preserves_metadata(self) -> None:
        meta = _minimal_metadata()
        from courtside_data.errors import InvalidSeason

        ep = _endpoint(
            "/foo/{season_end_year}.html",
            params=("season_end_year",),
            error=InvalidSeason,
            error_params=("season_end_year",),
            row_model=_TestRow,
            metadata=meta,
        )
        assert ep.metadata is meta

    def test_endpoint_factory_requires_metadata_and_row_model(self) -> None:
        from courtside_data.errors import InvalidSeason

        endpoint_factory: Any = _endpoint
        with pytest.raises(TypeError):
            endpoint_factory(
                "/foo/{season_end_year}.html",
                params=("season_end_year",),
                error=InvalidSeason,
                error_params=("season_end_year",),
            )

    def test_season_factory_preserves_metadata(self) -> None:
        meta = EndpointMetadata(
            domain=EndpointDomain.LEAGUE,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        )
        ep = _season("/leagues/NBA_{season_end_year}_per_game.html", row_model=_TestRow, metadata=meta)
        assert ep.metadata is meta

    def test_season_factory_requires_metadata_and_row_model(self) -> None:
        season_factory: Any = _season
        with pytest.raises(TypeError):
            season_factory("/leagues/NBA_{season_end_year}_per_game.html")

    def test_team_factory_preserves_metadata(self) -> None:
        meta = EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        )
        ep = _team("/teams/{team_abbreviation}/{season_end_year}.html", row_model=_TestRow, metadata=meta)
        assert ep.metadata is meta

    def test_team_factory_requires_metadata_and_row_model(self) -> None:
        team_factory: Any = _team
        with pytest.raises(TypeError):
            team_factory("/teams/{team_abbreviation}/{season_end_year}.html")

    def test_player_factory_preserves_metadata(self) -> None:
        meta = EndpointMetadata(
            domain=EndpointDomain.PLAYERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.PLAYER,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        )
        ep = _player(
            "/players/{player_identifier[0]}/{player_identifier}.html",
            row_model=_TestRow,
            metadata=meta,
        )
        assert ep.metadata is meta

    def test_player_factory_requires_metadata_and_row_model(self) -> None:
        player_factory: Any = _player
        with pytest.raises(TypeError):
            player_factory("/players/{player_identifier[0]}/{player_identifier}.html")


# ---------------------------------------------------------------------------
# Existing ENDPOINTS registry still works
# ---------------------------------------------------------------------------


class TestEndpointsRegistryUnaffected:
    def test_endpoints_dict_is_non_empty(self) -> None:
        assert len(ENDPOINTS) > 0

    def test_all_endpoints_have_metadata_after_backfill(self) -> None:
        for name, ep in ENDPOINTS.items():
            assert ep.metadata.domain is not None, f"Missing metadata domain on {name!r}"

    def test_endpoints_are_tableendpoint_instances(self) -> None:
        for ep in ENDPOINTS.values():
            assert isinstance(ep, EndpointSpec)

    def test_endpoints_still_importable_from_package(self) -> None:
        from courtside_data.endpoints import ENDPOINTS as _ENDPOINTS

        assert _ENDPOINTS is ENDPOINTS
