from typing import Optional
from PyQt5 import QtWidgets


class AbstractFileType:

    def __init__(self):
        pass

    def __repr__(self):
        return self.name + ' (' + self.abbreviation_data + ')' if self.abbreviation_data else self.name

    def __str__(self):
        return self.__repr__()

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def key(self) -> str:
        return self.abbreviation_data

    @property
    def abbreviation_data(self) -> str:
        raise NotImplementedError

    @property
    def extension_data(self) -> str:
        raise NotImplementedError

    @property
    def extension_str_data(self) -> str:
        return self.abbreviation_data + ' (*.' + self.extension_data + ')'

    @property
    def abbreviation_format(self) -> Optional[str]:
        return None

    @property
    def extension_format(self) -> Optional[str]:
        return None

    @property
    def extension_str_format(self) -> Optional[str]:
        return self.abbreviation_format + ' (*.' + self.extension_format + ')'

    def load(self, *args, **kwargs):
        raise NotImplementedError

    def num_files_required_to_view(self):
        return 1 if self.extension_str_format is None else 2

    def list_of_extensions(self):

        if self.num_files_required_to_view() == 1:
            return [self.extension_str_data]

        else:
            return [self.extension_str_data, self.extension_str_format]

    @staticmethod
    def get_time_key(time_key, signal_names):
        if not time_key:
            item, ok = QtWidgets.QInputDialog.getItem(
                QtWidgets.QWidget(),
                "Time Column",
                "Does file contain a separate time column?",
                signal_names, 0, False)

            if ok and item:
                time_key = item
            else:
                time_key = None

        return time_key

