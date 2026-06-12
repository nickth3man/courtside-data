"""Allow ``python -m courtside_data`` to run the CLI."""

from courtside_data.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
