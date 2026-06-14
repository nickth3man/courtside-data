import functools

from tests import http_mock as requests_mock


class ResponseMocker:
    def __init__(self, basketball_reference_paths_by_filename: dict[str, str]):
        self._basketball_reference_paths_by_filename = basketball_reference_paths_by_filename

    def decorate_class(self, klass):
        for attr_name in dir(klass):
            if not attr_name.startswith("test_"):
                continue

            attr = getattr(klass, attr_name)
            if not callable(attr):
                continue

            setattr(klass, attr_name, self.mock(attr))

        return klass

    def mock(self, callable):
        @functools.wraps(callable)
        def inner(*args, **kwargs):
            with requests_mock.Mocker() as m:
                for filename, basketball_reference_path in self._basketball_reference_paths_by_filename.items():
                    if not filename.endswith(".html"):
                        raise ValueError(f"Unexpected prefix for {filename}. Expected all files in to end with .html.")

                    with open(filename, encoding="utf8") as file_input:
                        m.get(
                            f"https://www.basketball-reference.com/{basketball_reference_path}",
                            text=file_input.read(),
                            status_code=200,
                        )
                return callable(*args, **kwargs)

        return inner

    def __call__(self, obj):
        if isinstance(obj, type):
            return self.decorate_class(obj)

        raise ValueError("Should only be used as a class decorator")


class SeasonScheduleMocker(ResponseMocker):
    """Mock a season's schedule pages from the ``raw/season_schedule/<year>`` corpus.

    The corpus stores the main schedule page as ``index.html`` and each month as
    ``<month>.html`` (the ``schedules_directory`` argument is retained for call-site
    compatibility but ignored — fixtures are resolved from ``raw/``).
    """

    def __init__(self, schedules_directory: str, season_end_year: int):
        from tests.integration.client import raw_fixtures

        html_files_directory = raw_fixtures.season_schedule_dir(season_end_year)
        basketball_reference_paths_by_filename: dict[str, str] = {}
        for path in sorted(html_files_directory.glob("*.html")):
            if path.name == "index.html":
                key = f"leagues/NBA_{season_end_year}_games.html"
            else:
                key = f"leagues/NBA_{season_end_year}_games-{path.name}"
            basketball_reference_paths_by_filename[str(path)] = key

        super().__init__(basketball_reference_paths_by_filename=basketball_reference_paths_by_filename)
