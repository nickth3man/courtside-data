"""HTTP status-code tuples shared by the endpoint registry and ``TableEndpoint``.

The endpoint factories default ``error_status_codes`` to :data:`NOT_FOUND`, and
the bespoke player-gamelog endpoints override with
:data:`NOT_FOUND_OR_SERVER_ERROR` (the BR gamelog pages return 500 for some
invalid player/season combinations).
"""

from __future__ import annotations

import httpx

NOT_FOUND = (int(httpx.codes.NOT_FOUND),)
NOT_FOUND_OR_SERVER_ERROR = (int(httpx.codes.NOT_FOUND), int(httpx.codes.INTERNAL_SERVER_ERROR))
