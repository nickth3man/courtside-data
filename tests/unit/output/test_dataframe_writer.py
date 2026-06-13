from datetime import date
from unittest import TestCase

from pydantic import BaseModel

from courtside_data.data import OutputType, OutputWriteOption
from courtside_data.output.writers import DataFrameWriter, FileOptions, OutputOptions


class PlayerRow(BaseModel):
    name: str
    game_date: date
    points: int


class TestDataFrameWriter(TestCase):
    def setUp(self):
        self.DATA = [
            {"name": "Jayson Tatum", "points": 30, "team": "BOS"},
            {"name": "Jaylen Brown", "points": 25, "team": "BOS"},
        ]
        self.writer = DataFrameWriter()

    def _options(self, column_names=None, file_options=None):
        return OutputOptions(
            file_options=file_options,
            formatting_options={"column_names": column_names},
            output_type=OutputType.DATAFRAME,
        )

    def test_returns_dataframe_with_rows(self):
        frame = self.writer.write(data=self.DATA, options=self._options())
        self.assertEqual(len(frame), 2)
        self.assertEqual(frame.iloc[0]["name"], "Jayson Tatum")

    def test_explicit_column_names_set_column_order(self):
        frame = self.writer.write(data=self.DATA, options=self._options(column_names=["team", "name", "points"]))
        self.assertEqual(list(frame.columns), ["team", "name", "points"])

    def test_extracts_rows_from_dict_payload(self):
        frame = self.writer.write(data={"players": self.DATA}, options=self._options())
        self.assertEqual(len(frame), 2)

    def test_missing_declared_columns_become_empty(self):
        frame = self.writer.write(data=self.DATA, options=self._options(column_names=["name", "absent"]))
        self.assertEqual(list(frame.columns), ["name", "absent"])
        self.assertTrue(frame["absent"].isna().all())

    def test_file_path_raises(self):
        file_options = FileOptions(path="out.csv", mode=OutputWriteOption.WRITE)
        with self.assertRaises(ValueError):
            self.writer.write(data=self.DATA, options=self._options(file_options=file_options))

    def test_values_keep_python_types(self):
        frame = self.writer.write(data=self.DATA, options=self._options())
        self.assertEqual(int(frame["points"].sum()), 55)

    def test_base_model_rows_are_dumped_in_json_mode(self):
        frame = self.writer.write(
            data=[PlayerRow(name="Jayson Tatum", game_date=date(2024, 6, 17), points=31)],
            options=self._options(),
        )
        self.assertEqual(list(frame.columns), ["name", "game_date", "points"])
        self.assertEqual(frame.iloc[0]["game_date"], "2024-06-17")

    def test_base_model_rows_honor_explicit_column_order(self):
        frame = self.writer.write(
            data=[PlayerRow(name="Jayson Tatum", game_date=date(2024, 6, 17), points=31)],
            options=self._options(column_names=["points", "name"]),
        )
        self.assertEqual(list(frame.columns), ["points", "name"])
