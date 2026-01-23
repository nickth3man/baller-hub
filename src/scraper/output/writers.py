"""Writers for different output formats."""

import csv
import json
from pathlib import Path

from src.core.domain import OutputType, OutputWriteOption
from src.scraper.utils.dictionaries import merge_two_dicts

DEFAULT_JSON_SORT_KEYS = True
DEFAULT_JSON_INDENT = 4
DEFAULT_JSON_OPTIONS = {
    "sort_keys": DEFAULT_JSON_SORT_KEYS,
    "indent": DEFAULT_JSON_INDENT,
}


def _ensure_parent_dir(path):
    """Ensure that the parent directory of the given path exists.

    Args:
        path (str | None): The file path.
    """
    if not path:
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)


class FileOptions:
    """
    Configuration for file output operations.
    """

    @staticmethod
    def of(path=None, mode=None):
        """
        Factory method to create FileOptions.

        Args:
            path (str | None): File path.
            mode (OutputWriteOption | None): Write mode (e.g. 'w', 'a').

        Returns:
            FileOptions: Configured object.
        """
        if mode is None:
            return FileOptions(path=path, mode=OutputWriteOption.WRITE)

        return FileOptions(path=path, mode=mode)

    def __init__(self, path, mode):
        """Initialize FileOptions.

        Args:
            path (str | None): The file path.
            mode (OutputWriteOption | None): The write mode.
        """
        self.path = path
        self.mode = mode

    @property
    def should_write_to_file(self):
        """bool: True if valid path and mode are set."""
        return self.path is not None and self.mode is not None

    def __eq__(self, other):
        """Check equality with another FileOptions instance.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if equal, False otherwise.
        """
        if isinstance(other, FileOptions):
            return self.path == other.path and self.mode == other.mode
        return False

    __hash__ = None


class OutputOptions:
    """
    Configuration for data serialization (JSON/CSV) and output destination.
    """

    @staticmethod
    def of(file_options, output_type, json_options=None, csv_options=None):
        """
        Factory method to create OutputOptions.

        Args:
            file_options (FileOptions): File output settings.
            output_type (OutputType): JSON or CSV.
            json_options (dict | None): JSON specific settings (sort_keys, etc.).
            csv_options (dict | None): CSV specific settings (column_names).

        Returns:
            OutputOptions: Configured object.
        """
        if output_type == OutputType.JSON:
            if json_options is None:
                formatting_options = DEFAULT_JSON_OPTIONS
            else:
                formatting_options = merge_two_dicts(DEFAULT_JSON_OPTIONS, json_options)
        elif output_type == OutputType.CSV:
            formatting_options = csv_options
        elif output_type is None:
            return OutputOptions(
                file_options=None, formatting_options={}, output_type=None
            )
        else:
            message = f"Unknown output type: {output_type}"
            raise ValueError(message)

        return OutputOptions(
            file_options=file_options,
            formatting_options=formatting_options,
            output_type=output_type,
        )

    def __init__(self, file_options, formatting_options, output_type):
        """Initialize OutputOptions.

        Args:
            file_options (FileOptions): File output settings.
            formatting_options (dict): Format-specific settings.
            output_type (OutputType): The type of output (JSON/CSV).
        """
        self.file_options = file_options
        self.formatting_options = formatting_options
        self.output_type = output_type

    def __eq__(self, other):
        """Check equality with another OutputOptions instance.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if equal, False otherwise.
        """
        if isinstance(other, OutputOptions):
            return (
                self.file_options == other.file_options
                and self.formatting_options == other.formatting_options
                and self.output_type == other.output_type
            )

        return False

    __hash__ = None


class Writer:
    """
    Base class for all output writers (JSON, CSV, etc.).
    """

    def __init__(self, value_formatter):
        """Initialize the Writer.

        Args:
            value_formatter (Callable): A function/callable to format values.
        """
        self.value_formatter = value_formatter

    def write(self, data, options):
        """
        Serialize data to the specified output.

        Args:
            data (list | dict): The data to serialize.
            options (OutputOptions): Configuration for writing.
        """
        raise NotImplementedError


class JSONWriter(Writer):
    """
    Writes data to JSON format, either to a file or returning a string.
    """

    def write(self, data, options):
        """
        Serialize to JSON.

        If path is provided in options, writes to file. Otherwise returns JSON string.
        """
        output_options = merge_two_dicts(
            DEFAULT_JSON_OPTIONS, options.formatting_options
        )

        if options.file_options.should_write_to_file:
            _ensure_parent_dir(options.file_options.path)
            with Path(options.file_options.path).open(
                options.file_options.mode.value,
                newline="",
                encoding="utf8",
            ) as json_file:
                return json.dump(
                    data,
                    json_file,
                    cls=self.value_formatter,
                    **output_options,
                )

        return json.dumps(
            data,
            cls=self.value_formatter,
            **output_options,
        )


class CSVWriter(Writer):
    """
    Writes data to CSV format.

    Requires 'column_names' to be present in options.formatting_options.
    """

    def rows(self, data):
        """Convert data into a list of rows for CSV writing.

        Args:
            data (list[dict]): The input data.

        Returns:
            list[dict]: A list of row dictionaries with formatted values.
        """
        return [
            {key: self.value_formatter(value) for key, value in row.items()}
            for row in data
        ]

    def write(self, data, options):
        """
        Write data to CSV file.

        Args:
            data (list[dict]): List of data rows.
            options (OutputOptions): Must contain valid file path and column_names.
        """
        _ensure_parent_dir(options.file_options.path)
        with Path(options.file_options.path).open(
            options.file_options.mode.value,
            newline="",
            encoding="utf8",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=options.formatting_options.get("column_names"),
                lineterminator="\n",
            )
            writer.writeheader()

            writer.writerows(self.rows(data=data))


class SearchCSVWriter(CSVWriter):
    """
    Specialized CSV writer for search results.

    Search results have a nested structure (dict with 'players' key), unlike standard lists.
    This writer flattens the 'players' list for CSV output.
    """

    def rows(self, data):
        """Convert search results into a list of rows.

        Args:
            data (dict): The search results data containing a 'players' list.

        Returns:
            list[dict]: Flattened list of player data rows.
        """
        return [
            {key: self.value_formatter(value) for key, value in row.items()}
            for row in data["players"]
        ]
