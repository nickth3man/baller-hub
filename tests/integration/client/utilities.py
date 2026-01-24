import functools
from pathlib import Path

import requests_mock


class ResponseMocker:
    def __init__(self, basketball_reference_paths_by_filename: dict[str, str]):
        self._basketball_reference_paths_by_filename = (
            basketball_reference_paths_by_filename
        )

    def decorate_class(self, klass):
        for attr_name in dir(klass):
            if not attr_name.startswith("test_"):
                continue

            attr = getattr(klass, attr_name)
            if not callable(attr):
                continue

            setattr(klass, attr_name, self.mock(attr))

        return klass

    def mock(self, callable):  # noqa: A002
        @functools.wraps(callable)
        def inner(*args, **kwargs):
            with requests_mock.Mocker() as m:
                for (
                    filename,
                    basketball_reference_path,
                ) in self._basketball_reference_paths_by_filename.items():
                    if not filename.endswith(".html"):
                        msg = f"Unexpected prefix for {filename}. Expected all files in to end with .html."
                        raise ValueError(msg)

                    with open(filename, encoding="utf-8") as file_input:  # noqa: PTH123
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

        msg = "Should only be used as a class decorator"
        raise ValueError(msg)


class SeasonScheduleMocker(ResponseMocker):
    def __init__(self, schedules_directory: str | Path, season_end_year: int):
        basketball_reference_paths_by_filename: dict[str, str] = {}
        html_files_directory = Path(schedules_directory) / str(season_end_year)
        for file_path in html_files_directory.iterdir():
            if file_path.suffix != ".html":
                continue
            filename = file_path.name
            if filename.startswith(str(season_end_year)):
                key = f"leagues/NBA_{season_end_year}_games.html"
            else:
                key = f"leagues/NBA_{season_end_year}_games-{filename}"
            basketball_reference_paths_by_filename[str(file_path)] = key

        super().__init__(
            basketball_reference_paths_by_filename=basketball_reference_paths_by_filename
        )
