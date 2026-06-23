from enum import Enum


class FieldFormatter:
    @staticmethod
    def can_format(data):
        raise NotImplementedError

    def __init__(self, data):
        self.data = data

    def format(self):
        raise NotImplementedError


class EnumFormatter(FieldFormatter):
    @staticmethod
    def can_format(data):
        return isinstance(data, Enum)

    def format(self):
        return self.data.value


class ListFormatter(FieldFormatter):
    @staticmethod
    def can_format(data):
        return isinstance(data, list)

    def format(self):
        return "-".join(format_value(value=value) for value in self.data)


class DictFormatter(FieldFormatter):
    @staticmethod
    def can_format(data):
        return isinstance(data, dict)

    def format(self):
        # Serialize dict to a compact string representation
        return ";".join(f"{k}={format_value(v)}" for k, v in self.data.items())


class SetFormatter(FieldFormatter):
    @staticmethod
    def can_format(data):
        return isinstance(data, set)

    def format(self):
        return ListFormatter(data=list(self.data)).format()


FORMATTER_CLASSES = [
    EnumFormatter,
    DictFormatter,
    ListFormatter,
    SetFormatter,
]


def format_value(value):
    formatter_class = next(
        (formatter_class for formatter_class in FORMATTER_CLASSES if formatter_class.can_format(value)),
        None,
    )

    if formatter_class is None:
        return value

    return formatter_class(data=value).format()
