"""Shared cell-extraction helpers for lxml-backed page/row classes."""

from __future__ import annotations

from lxml.html import HtmlElement


def cell_text(html: HtmlElement, data_stat: str, default: str = "") -> str:
    cells = html.xpath(f'td[@data-stat="{data_stat}"]')
    if len(cells) > 0:
        return cells[0].text_content()
    return default


def th_text(html: HtmlElement, data_stat: str, default: str = "") -> str:
    cells = html.xpath(f'th[@data-stat="{data_stat}"]')
    if len(cells) > 0:
        return cells[0].text_content()
    return default
