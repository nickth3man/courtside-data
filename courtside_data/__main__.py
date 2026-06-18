"""Allow ``python -m courtside_data`` to run the CLI."""

from __future__ import annotations

import sys

from courtside_data.cli import main

if __name__ == "__main__":
    if sys.stdout.isatty():
        try:
            from rich.traceback import install as _install_rich_traceback

            _install_rich_traceback(show_locals=False)
        except ImportError:
            # rich is optional; fall back to the default traceback.
            pass
    raise SystemExit(main())
