from courtside_data.data import OutputType
from courtside_data.output.writers import DataFrameWriter


class OutputService:
    def __init__(self, json_writer, csv_writer, dataframe_writer=None):
        self.json_writer = json_writer
        self.csv_writer = csv_writer
        self.dataframe_writer = dataframe_writer if dataframe_writer is not None else DataFrameWriter()
        self.output_type_writers = {
            OutputType.JSON: self.json_writer,
            OutputType.CSV: self.csv_writer,
            OutputType.DATAFRAME: self.dataframe_writer,
        }

    def output(self, data, options):
        if options.output_type is None:
            return data

        writer = self.output_type_writers.get(options.output_type)

        if writer is None:
            raise ValueError(f"Unknown output type: {options.output_type}")

        return writer.write(data=data, options=options)
