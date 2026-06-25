"""Tests for the EndpointMetadata taxonomy and its integration with EndpointSpec."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

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
    def test_metadata_defaults_to_none(self) -> None:
        ep = EndpointSpec(path="/foo/bar.html")
        assert ep.metadata is None

    def test_metadata_can_be_set(self) -> None:
        meta = _minimal_metadata()
        ep = EndpointSpec(path="/foo/bar.html", metadata=meta)
        assert ep.metadata is meta

    def test_table_endpoint_with_metadata_is_frozen(self) -> None:
        meta = _minimal_metadata()
        ep = EndpointSpec(path="/foo/bar.html", metadata=meta)
        attr = "metadata"
        with pytest.raises(FrozenInstanceError):
            setattr(ep, attr, None)

    def test_table_endpoint_equality_with_same_metadata(self) -> None:
        meta = _minimal_metadata()
        ep1 = EndpointSpec(path="/foo/bar.html", metadata=meta)
        ep2 = EndpointSpec(path="/foo/bar.html", metadata=meta)
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
        ep1 = EndpointSpec(path="/foo/bar.html", metadata=meta1)
        ep2 = EndpointSpec(path="/foo/bar.html", metadata=meta2)
        assert ep1 != ep2


# ---------------------------------------------------------------------------
# Dispatch kind + deprecated custom compatibility property
# ---------------------------------------------------------------------------


class TestKindAndCustomProperty:
    """``kind`` drives dispatch; ``custom`` is a deprecated alias of it."""

    def test_kind_defaults_to_generic_table_without_metadata(self) -> None:
        ep = EndpointSpec(path="/foo/bar.html")
        assert ep.metadata is None
        assert ep.kind is EndpointKind.GENERIC_TABLE

    def test_custom_defaults_to_false_without_metadata(self) -> None:
        ep = EndpointSpec(path="/foo/bar.html")
        assert ep.custom is False

    def test_kind_reflects_metadata_kind(self) -> None:
        meta = _minimal_metadata()
        ep = EndpointSpec(path="/foo/bar.html", metadata=meta)
        assert ep.kind is EndpointKind.GENERIC_TABLE

    def test_workflow_metadata_makes_kind_workflow(self) -> None:
        meta = EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.DATE,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        )
        ep = EndpointSpec(path="/foo/bar.html", metadata=meta)
        assert ep.kind is EndpointKind.WORKFLOW
        assert ep.custom is True

    def test_generic_table_metadata_keeps_custom_false(self) -> None:
        ep = EndpointSpec(path="/foo/bar.html", metadata=_minimal_metadata())
        assert ep.kind is EndpointKind.GENERIC_TABLE
        assert ep.custom is False

    def test_custom_is_consistent_with_kind_across_registry(self) -> None:
        for name, ep in ENDPOINTS.items():
            assert ep.custom is (ep.kind is EndpointKind.WORKFLOW), name


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
            metadata=meta,
        )
        assert ep.metadata is meta

    def test_endpoint_factory_metadata_none_by_default(self) -> None:
        from courtside_data.errors import InvalidSeason

        ep = _endpoint(
            "/foo/{season_end_year}.html",
            params=("season_end_year",),
            error=InvalidSeason,
            error_params=("season_end_year",),
        )
        assert ep.metadata is None

    def test_season_factory_preserves_metadata(self) -> None:
        meta = EndpointMetadata(
            domain=EndpointDomain.LEAGUE,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        )
        ep = _season("/leagues/NBA_{season_end_year}_per_game.html", metadata=meta)
        assert ep.metadata is meta

    def test_season_factory_metadata_none_by_default(self) -> None:
        ep = _season("/leagues/NBA_{season_end_year}_per_game.html")
        assert ep.metadata is None

    def test_team_factory_preserves_metadata(self) -> None:
        meta = EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        )
        ep = _team("/teams/{team_abbreviation}/{season_end_year}.html", metadata=meta)
        assert ep.metadata is meta

    def test_team_factory_metadata_none_by_default(self) -> None:
        ep = _team("/teams/{team_abbreviation}/{season_end_year}.html")
        assert ep.metadata is None

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
            metadata=meta,
        )
        assert ep.metadata is meta

    def test_player_factory_metadata_none_by_default(self) -> None:
        ep = _player("/players/{player_identifier[0]}/{player_identifier}.html")
        assert ep.metadata is None


# ---------------------------------------------------------------------------
# Existing ENDPOINTS registry still works
# ---------------------------------------------------------------------------


class TestEndpointsRegistryUnaffected:
    def test_endpoints_dict_is_non_empty(self) -> None:
        assert len(ENDPOINTS) > 0

    def test_all_endpoints_have_metadata_after_backfill(self) -> None:
        for name, ep in ENDPOINTS.items():
            assert ep.metadata is not None, f"Missing metadata on {name!r}"

    def test_endpoints_are_tableendpoint_instances(self) -> None:
        for ep in ENDPOINTS.values():
            assert isinstance(ep, EndpointSpec)

    def test_endpoints_still_importable_from_package(self) -> None:
        from courtside_data.endpoints import ENDPOINTS as _ENDPOINTS

        assert _ENDPOINTS is ENDPOINTS
