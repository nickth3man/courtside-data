"""Shared module-level constants and TYPE_CHECKING aliases for workflow steps."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from parsel import Selector

from courtside_data.errors import InvalidDate

if TYPE_CHECKING:
    from courtside_data.parsing.workflows._context import WorkflowExecutionContext

    ErrorFactory = Callable[[WorkflowExecutionContext], Exception]
    ParserWithStats = Callable[[Selector], tuple[list[dict[str, Any]], dict[str, Any]]]
    StatsMerger = Callable[[dict[str, Any], dict[str, Any]], None]


SCHEDULE_MONTH_LINK_SELECTOR = 'div#content div.filter div:not([class*="current"]) a'


def _invalid_date_from_context(context: WorkflowExecutionContext) -> Exception:
    return InvalidDate(
        day=context.params["day"],
        month=context.params["month"],
        year=context.params["year"],
    )
