"""Service for handling data output (JSON/CSV)."""

from src.core.domain import OutputType


class OutputService:
    """
    Delegates data serialization to the appropriate writer (JSON/CSV).

    This service decouples the scraping logic from the output format.
    It selects the correct Writer strategy based on the OutputOptions.
    """

    def __init__(self, json_writer, csv_writer):
        """Initialize the output service.

        Args:
            json_writer (JSONWriter): The writer strategy for JSON output.
            csv_writer (CSVWriter): The writer strategy for CSV output.
        """
        self.json_writer = json_writer
        self.csv_writer = csv_writer
        self.output_type_writers = {
            OutputType.JSON: self.json_writer,
            OutputType.CSV: self.csv_writer,
        }

    def output(self, data, options):
        """
        Serializes data according to the provided options.

        Args:
            data (list|dict): The data to serialize.
            options (OutputOptions): Configuration for output format and file destination.

        Returns:
            str|dict|None: The serialized string (if JSON/CSV) or the raw data (if no output type specified).
        """
        if options.output_type is None:
            return data

        writer = self.output_type_writers.get(options.output_type)

        if writer is None:
            message = f"Unknown output type: {options.output_type}"
            raise ValueError(message)

        return writer.write(data=data, options=options)
