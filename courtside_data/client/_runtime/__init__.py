"""Runtime plumbing shared by :func:`courtside_data.client._runner._run_endpoint`.

Private subpackage (leading underscore). The modules here hold the clearly-
separable moving parts that used to live in the monolithic
:mod:`courtside_data.client._runner`:

- :mod:`courtside_data.client._runtime._locator` — process-wide
  :class:`~courtside_data.http_service.HTTPService` singleton and the
  :class:`~contextvars.ContextVar` that lets a
  :class:`~courtside_data.client.courtside_client.CourtsideClient` swap in
  its own service for the duration of one method call.
- :mod:`courtside_data.client._runtime._coerce` — typed-param coercion
  (raw abbreviations → :class:`~courtside_data.data.Team` enum) for custom
  endpoints, plus the ``@lru_cache``-d annotation map.
- :mod:`courtside_data.client._runtime._output` — :class:`OutputService`
  factory, the strategy-pattern :func:`_format_output` dispatch, and the
  :func:`_output_debug_result` envelope wrapper used when ``debug=True``.
- :mod:`courtside_data.client._runtime._flush` — best-effort, idempotent
  write of the debug-trace envelope to disk; the ``WeakKeyDictionary`` that
  makes the success-path and ``finally``-path flushes safe to coexist.
- :mod:`courtside_data.client._runtime._execute` — the
  :func:`_call_with_error_mapping` HTTP-status-to-domain-error translator
  and the :func:`_execute` template method that ties the service call to
  the dual Pydantic / legacy validation pipelines and the output
  formatter.

The :func:`_run_endpoint` template itself stays in
:mod:`courtside_data.client._runner` and re-exports
:data:`_service_override` so :class:`CourtsideClient` can keep using
``_runner._service_override.set(...)`` as its injection seam.
"""

from __future__ import annotations
