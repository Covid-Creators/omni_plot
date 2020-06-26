import pandas

from data_flow.serializer.file_type import AbstractFileType
from data_flow.data_store import DataSet


class CSV(AbstractFileType):

    @property
    def name(self) -> str:
        return 'Comma-Separated Values'

    @property
    def abbreviation_data(self) -> str:
        return 'CSV'

    @property
    def extension_data(self) -> str:
        return 'csv'

    @staticmethod
    def load(path_data, time_key=None) -> DataSet:

        data_frame = pandas.read_csv(path_data)
        signal_names = data_frame.keys()

        data_set = DataSet(
            import_method_type=CSV,
            path_data=path_data,
            name='-'.join(path_data.split('/')[-1].split('.')[:-1]),
        )

        data_set._time_key = time_key = AbstractFileType.get_time_key(time_key, signal_names)

        time_array = data_frame.get(time_key) if time_key else None

        for name in signal_names:

            # Skip the time column if it's defined
            if time_array is not None and name == time_key:
                continue

            data_set.add_signal(
                name=name,
                value_array=data_frame.get(name),
                time_array=time_array
            )

        return data_set
