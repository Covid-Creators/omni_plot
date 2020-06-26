import os
from PyQt5 import QtCore


class Settings(QtCore.QSettings):

    settings_file = '/__qsettings.ini'

    def __init__(self, controller, *args, location=None, **kwargs):

        self._controller = controller

        file_path = Settings.set_path(location)
        if file_path:
            super(Settings, self).__init__(file_path, Settings.IniFormat)
        else:
            super(Settings, self).__init__(*args, **kwargs)

    @property
    def edit_mode(self):
        return self._try_bool('edit_mode', False)

    @edit_mode.setter
    def edit_mode(self, toggle):
        self.setValue('edit_mode', toggle)

    @property
    def debug_mode(self):
        return self._try_bool('debug_mode', False)

    @debug_mode.setter
    def debug_mode(self, toggle):
        self.setValue('debug_mode', toggle)

    @property
    def tab_selected(self):
        return self._try_int('tab_selected', 0)

    @tab_selected.setter
    def tab_selected(self, value):
        self.setValue('tab_selected', value)

    @property
    def geometry(self):
        return self._try_value('geometry', None)

    @geometry.setter
    def geometry(self, value):
        self.setValue('geometry', value)

    @property
    def overwrite_on_refresh(self):
        return self._try_bool('overwrite_on_refresh', False)

    @overwrite_on_refresh.setter
    def overwrite_on_refresh(self, toggle):
        self.setValue('overwrite_on_refresh', toggle)

    @property
    def loaded_workspace(self):
        return self._try_value('loaded_workspace', '')

    @loaded_workspace.setter
    def loaded_workspace(self, value):
        self.setValue('loaded_workspace', value)

    @property
    def hidden_columns_main(self):
        return self._try_value('hidden_columns_main', [])

    @hidden_columns_main.setter
    def hidden_columns_main(self, value):
        self.setValue('hidden_columns_main', value)

    @property
    def hidden_columns_popup(self):
        return self._try_value('hidden_columns_popup', [])

    @hidden_columns_popup.setter
    def hidden_columns_popup(self, value):
        self.setValue('hidden_columns_popup', value)

    @property
    def default_file_type(self):
        return self._try_value('file_type')

    @default_file_type.setter
    def default_file_type(self, value):
        self.setValue('file_type', value)

    @property
    def default_default_path_data(self):
        return self._try_value('_path_data', '')

    @default_default_path_data.setter
    def default_default_path_data(self, value):
        self.setValue('_path_data', value)

    @property
    def default_default_path_format(self):
        return self._try_value('_path_format', '')

    @default_default_path_format.setter
    def default_default_path_format(self, value):
        self.setValue('_path_format', value)

    def default_path_data_for(self, file_format: str):
        return self._try_value(file_format+'_path_data', self.default_default_path_data)

    def set_default_path_data_for(self, value, file_format: str):
        self.setValue(file_format+'_path_data', value)

    def default_path_format_for(self, file_format: str):
        return self._try_value(file_format+'_path_format', self.default_default_path_format)

    def set_default_path_format_for(self, value, file_format: str):
        self.setValue(file_format+'_path_format', value)

    @staticmethod
    def set_path(dir_path):
        if dir_path and isinstance(dir_path, str):

            if not os.path.isabs(dir_path):

                dir_path = QtCore.QDir.currentPath() + '/' + dir_path

            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                return dir_path + Settings.settings_file

            else:
                return None

    def _try_value(self, value: str, default=None):
        return self.value(value) if self.contains(value) else default

    def _try_int(self, value: str, default=-1):
        return self.value(value, default, type=int) if self.contains(value) else default

    def _try_bool(self, value: str, default=False):
        return self.value(value, default, type=bool) if self.contains(value) else default
