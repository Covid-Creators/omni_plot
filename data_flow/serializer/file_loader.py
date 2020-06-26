import os
from typing import Optional

from PyQt5 import QtWidgets, QtCore

from data_flow.serializer.import_popup import ImportPopup

from data_flow.serializer.file_type import AbstractFileType
from plugins.file_types.csv import CSV


class FileLoader:

    def __init__(self, controller):

        self.controller = controller
        self.popup = None
        self.form = None

        self._valid_files = []
        self._path_data = ''
        self._path_format = None

        self._file_format = self.get_file_type_by_name(
            self.controller.settings.default_file_type) or self.data_formats_available[0]

    @property
    def data_formats_available(self) -> [AbstractFileType]:
        return list(self.data_format_dict.values())

    @property
    def data_format_dict(self) -> dict:
        return {
            CSV().key: CSV(),
        }

    @property
    def file_format(self) -> AbstractFileType:
        return self._file_format

    @file_format.setter
    def file_format(self, value):
        # TODO Make this more robust by checking if class or instance
        if isinstance(value, str):
            file_format = self.get_file_type_by_name(value)

        else:
            file_format = value

        self._file_format = file_format

    @property
    def file_type_extensions_dict(self):
        zipped = {}
        for file_format in self.data_formats_available:
            if file_format.extension_str_format:
                zipped[file_format.key] = (file_format.extension_str_data, file_format.extension_str_format)

            else:
                zipped[file_format.key] = (file_format.extension_str_data,)

        return zipped

    @QtCore.pyqtSlot(str)
    def file_type_changed(self, new_file_type_str=None, caller=None):

        if not self.popup:
            self.popup = caller

        if not new_file_type_str:
            new_file_type_str = self.popup._file_type_combo.currentText()

        format_type = self.get_file_type_by_name(new_file_type_str)

        if format_type:
            self.controller.settings.default_file_type = new_file_type_str
            self.file_format = format_type

        self.update_file_browsing_rows()

    @property
    def valid_files(self) -> [str]:
        return self._valid_files

    @property
    def path_data(self):
        return self._path_data

    @path_data.setter
    def path_data(self, value):
        if self.check_file_valid(value) and value.endswith(self.file_format.extension_data):
            self._path_data = value

    @property
    def path_format(self):
        if not self.file_format.extension_format:
            self._path_format = None

        return self._path_format

    @path_format.setter
    def path_format(self, value):
        if self.file_format.extension_format:
            if self.check_file_valid(value) and value.endswith(self.file_format.extension_format):
                self._path_format = value

        else:
            self._path_format = None

    def open_popup(self):
        self.popup = ImportPopup(self.controller, self)
        self.form = self.popup._file_browsing_grid
        self.popup.show()

    def update_file_browsing_rows(self):

        # TODO Set text from settings based on file type
        self.popup._label_data.setText(self.file_format.extension_str_data)
        self.popup._text_path_data.setText(self.controller.settings.default_path_data_for(self.file_format.key))

        if self.file_format.extension_format:
            self.popup._label_format.setText(self.file_format.extension_str_format)
            self.popup._text_path_format.setText(self.controller.settings.default_path_format_for(self.file_format.key))

            self.popup._label_format.show()
            self.popup._text_path_format.show()
            self.popup._btn_browse_format.show()

        else:
            self.popup._label_format.setText('')
            self.popup._text_path_format.setText('')

            self.popup._label_format.hide()
            self.popup._text_path_format.hide()
            self.popup._btn_browse_format.hide()

        self.popup.text_field_changed()

    def check_files(self, files: [str] = None) -> bool:

        files_are_valid = True

        if files:
            for file_str in files:
                if not self.check_file_valid(file_str):
                    files_are_valid = False
                    break

        else:
            trial_path = self.popup._text_path_data.text()
            if self.check_file_valid(trial_path):
                self.path_data = trial_path

                if self.file_format.extension_format:
                    trial_path = self.popup._text_path_format.text()
                    if self.check_file_valid(trial_path):
                        self.path_format = trial_path

                    else:
                        files_are_valid = False
                else:
                    self.path_format = None
            else:
                files_are_valid = False

            if files_are_valid:
                self.popup._btn_submit.setEnabled(True)

            else:
                self.popup._btn_submit.setEnabled(False)

        return files_are_valid

    def pass_files(self):
        if not self.check_files():
            error_window = QtWidgets.QErrorMessage()
            error_window.showMessage("Error: At least one file must be selected.")

        else:
            self.controller.settings.set_default_path_data_for(self.path_data, self.file_format.key)
            if self.file_format.extension_format:
                self.controller.settings.set_default_path_format_for(self.path_format, self.file_format.key)
                self.controller.data_store.add_data_set(self.file_format.load(self.path_data, self.path_format))

            else:
                self.controller.data_store.add_data_set(self.file_format.load(self.path_data))

        self.popup.close()

    def get_file_type_by_name(self, name) -> Optional[AbstractFileType]:
        for file_type in self.data_formats_available:

            if name == repr(file_type):
                return file_type

        return None

    def get_file_data(self):
        self.get_file(
            filter_str=self.file_format.extension_str_data,
            callback=(lambda x: self.popup._text_path_data.setText(x)),
            path=self.popup._text_path_data.text())

    def get_file_format(self):
        self.get_file(
            filter_str=self.file_format.extension_str_format,
            callback=(lambda x: self.popup._text_path_format.setText(x)),
            path=self.popup._text_path_format.text())

    @staticmethod
    def get_file(filter_str='', callback=None, path=None):
        # Get user selected file path.
        if path is None:
            path = os.getcwd()

        file_return = QtWidgets.QFileDialog.getOpenFileName(
            caption='Select file',
            directory=path,
            filter=filter_str)

        if callback:
            if file_return[0]:
                callback(file_return[0])

    @staticmethod
    def check_file_valid(file_path: str):
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return True

        else:
            return False
