import csv
import json
from typing import Any

from pydantic import BaseModel

from courtside_data.data import OutputType, OutputWriteOption

DEFAULT_JSON_SORT_KEYS = True
DEFAULT_JSON_INDENT = 4
DEFAULT_JSON_OPTIONS = {
    "sort_keys": DEFAULT_JSON_SORT_KEYS,
    "indent": DEFAULT_JSON_INDENT,
}


class FileOptions:
    @staticmethod
    def of(path=None, mode=None):
        if mode is None:
            return FileOptions(path=path, mode=OutputWriteOption.WRITE)

        return FileOptions(path=path, mode=mode)

    def __init__(self, path, mode):
        self.path = path
        self.mode = mode

    @property
    def should_write_to_file(self):
        return self.path is not None and self.mode is not None

    def __eq__(self, other):
        if isinstance(other, FileOptions):
            return self.path == other.path and self.mode == other.mode
        return False


class OutputOptions:
    @staticmethod
    def of(file_options, output_type, json_options=None, csv_options=None):
        if output_type == OutputType.JSON:
            if json_options is None:
                formatting_options = DEFAULT_JSON_OPTIONS
            else:
                formatting_options = {**DEFAULT_JSON_OPTIONS, **json_options}
        elif output_type in (OutputType.CSV, OutputType.DATAFRAME):
            # DataFrames reuse the CSV column contract for column order
            formatting_options = csv_options
        elif output_type is None:
            return OutputOptions(file_options=None, formatting_options={}, output_type=None)
        else:
            raise ValueError(f"Unknown output type: {output_type}")

        return OutputOptions(
            file_options=file_options,
            formatting_options=formatting_options,
            output_type=output_type,
        )

    def __init__(self, file_options, formatting_options, output_type):
        self.file_options = file_options
        self.formatting_options = formatting_options
        self.output_type = output_type

    def __eq__(self, other):
        if isinstance(other, OutputOptions):
            return (
                self.file_options == other.file_options
                and self.formatting_options == other.formatting_options
                and self.output_type == other.output_type
            )

        return False


class Writer:
    def __init__(self, value_formatter):
        self.value_formatter = value_formatter

    def write(self, data, options):
        raise NotImplementedError


def _is_row_model(value: Any) -> bool:
    return isinstance(value, BaseModel)


def _serialize_row_model(value: BaseModel) -> dict[str, Any]:
    return value.model_dump(mode="json")


def _serialize_row_models(data):
    """Convert Pydantic row models to JSON-ready dicts, preserving other shapes."""
    if isinstance(data, list):
        return [_serialize_row_model(row) if _is_row_model(row) else row for row in data]
    if isinstance(data, dict):
        return {
            key: [_serialize_row_model(row) if _is_row_model(row) else row for row in value]
            if isinstance(value, list)
            else value
            for key, value in data.items()
        }
    return data


class JSONWriter(Writer):
    def write(self, data, options):
        serialized_data = _serialize_row_models(data)
        output_options: dict[str, Any] = {**DEFAULT_JSON_OPTIONS, **options.formatting_options}
        if options.file_options.should_write_to_file:
            with open(
                options.file_options.path, options.file_options.mode.value, newline="", encoding="utf8"
            ) as json_file:
                return json.dump(
                    serialized_data,
                    json_file,
                    cls=self.value_formatter,
                    **output_options,
                )

        return json.dumps(
            serialized_data,
            cls=self.value_formatter,
            **output_options,
        )


class CSVWriter(Writer):
    @staticmethod
    def _extract_rows(data):
        """Extract a list of dict rows from data that may be a list or a dict."""
        data = _serialize_row_models(data)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    return v
        return []

    @staticmethod
    def _detect_fieldnames(rows):
        """Auto-detect column names from the first row if available."""
        if rows and isinstance(rows[0], dict):
            return list(rows[0].keys())
        return []

    def rows(self, data):
        extracted = self._extract_rows(data)
        return [{key: self.value_formatter(value) for key, value in row.items()} for row in extracted]

    def write(self, data, options):
        rows = self._extract_rows(data)
        if not rows:
            # Write an empty CSV with just a header
            fieldnames = options.formatting_options.get("column_names") or []
            with open(
                options.file_options.path,
                options.file_options.mode.value,
                newline="",
                encoding="utf8",
            ) as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(fieldnames)
            return

        # Determine fieldnames: prefer explicit, fall back to auto-detect
        fieldnames = options.formatting_options.get("column_names")
        if not fieldnames:
            fieldnames = self._detect_fieldnames(rows)

        with open(
            options.file_options.path,
            options.file_options.mode.value,
            newline="",
            encoding="utf8",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
                extrasaction="ignore",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(self.rows(data=data))


class DataFrameWriter(Writer):
    """Materializes rows as a pandas DataFrame.

    Requires the ``pandas`` extra (``pip install "courtside-data[pandas]"``).
    Values keep the Python types produced by coercion — no string formatting
    is applied.
    """

    def __init__(self):
        super().__init__(value_formatter=None)

    def write(self, data, options):
        try:
            import pandas
        except ImportError as error:
            raise ImportError(
                "DataFrame output requires pandas. Install it with: pip install 'courtside-data[pandas]'"
            ) from error

        if options.file_options is not None and options.file_options.should_write_to_file:
            raise ValueError(
                "output_file_path is not supported with OutputType.DATAFRAME; "
                "use the returned DataFrame's own to_csv/to_parquet methods"
            )

        rows = CSVWriter._extract_rows(data)
        frame = pandas.DataFrame(rows)
        column_names = (options.formatting_options or {}).get("column_names")
        if column_names:
            frame = frame.reindex(columns=list(column_names))
        return frame
