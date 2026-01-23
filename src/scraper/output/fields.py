"""Field formatting strategies."""

from datetime import date, datetime
from enum import Enum
from json import JSONEncoder


class FieldFormatter:
    """
    Base strategy for formatting values based on their type.
    """

    @staticmethod
    def can_format(data):
        """Check if this formatter can handle the data type.

        Args:
            data: The data to check.

        Returns:
            bool: True if this formatter can handle the data.
        """
        raise NotImplementedError()

    def __init__(self, data):
        """Initialize the formatter.

        Args:
            data: The data to be formatted.
        """
        self.data = data

    def format(self):
        """Format the data into a string.

        Returns:
            str: The formatted data.
        """
        raise NotImplementedError


class EnumFormatter(FieldFormatter):
    """
    Formats Enum objects to their value.
    """

    @staticmethod
    def can_format(data):
        """Check if data is an Enum.

        Args:
            data: The data to check.

        Returns:
            bool: True if data is an Enum.
        """
        return isinstance(data, Enum)

    def format(self):
        """Return the enum value.

        Returns:
            Any: The value of the enum.
        """
        return self.data.value


class ListFormatter(FieldFormatter):
    """
    Formats lists by joining formatted values with hyphens.
    """

    @staticmethod
    def can_format(data):
        """Check if data is a list.

        Args:
            data: The data to check.

        Returns:
            bool: True if data is a list.
        """
        return isinstance(data, list)

    def format(self):
        """Join list elements with dashes.

        Returns:
            str: The joined string.
        """
        return "-".join(format_value(value=value) for value in self.data)


class SetFormatter(FieldFormatter):
    """
    Formats sets by converting to list and using ListFormatter.
    """

    @staticmethod
    def can_format(data):
        """Check if data is a set.

        Args:
            data: The data to check.

        Returns:
            bool: True if data is a set.
        """
        return isinstance(data, set)

    def format(self):
        """Convert set to list and format.

        Returns:
            str: The formatted set as a joined string.
        """
        return ListFormatter(data=list(self.data)).format()


FORMATTER_CLASSES = [
    EnumFormatter,
    ListFormatter,
    SetFormatter,
]


def format_value(value):
    """
    Format a value using the appropriate strategy.

    Delegates to the first matching formatter in FORMATTER_CLASSES.

    Args:
        value: The value to format.

    Returns:
        Any: The formatted value, or the original value if no formatter matches.
    """
    formatter_class = next(
        (
            formatter_class
            for formatter_class in FORMATTER_CLASSES
            if formatter_class.can_format(value)
        ),
        None,
    )

    if formatter_class is None:
        return value

    return formatter_class(data=value).format()


class BasketballReferenceJSONEncoder(JSONEncoder):
    """
    Custom JSON Encoder for project-specific types (Date, Enum, Set).
    """

    def default(self, o):
        """Encode project-specific types.

        Args:
            o: The object to encode.

        Returns:
            Any: The encoded object.
        """
        if isinstance(o, (datetime, date)):
            return o.isoformat()

        if isinstance(o, Enum):
            return o.value

        if isinstance(o, set):
            return list(o)

        return JSONEncoder.default(self, o)
