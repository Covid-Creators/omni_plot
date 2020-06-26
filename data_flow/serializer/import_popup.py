from PyQt5 import QtWidgets, QtGui


class ImportPopup(QtWidgets.QDialog):

    def __init__(self, controller, file_loader, *args, **kwargs):
        super(ImportPopup, self).__init__(*args, **kwargs)

        self._controller = controller
        self._file_loader = file_loader

        self._file_type_h_box = QtWidgets.QHBoxLayout()
        self._file_type_combo = QtWidgets.QComboBox()

        self._file_browsing_grid = QtWidgets.QGridLayout()
        self._label_data = QtWidgets.QLabel()
        self._text_path_data = QtWidgets.QLineEdit()
        self._btn_browse_data = QtWidgets.QPushButton('Browse...')
        self._label_format = QtWidgets.QLabel()
        self._text_path_format = QtWidgets.QLineEdit()
        self._btn_browse_format = QtWidgets.QPushButton('Browse...')

        self._btn_submit = QtWidgets.QPushButton("Submit")
        self._btn_cancel = QtWidgets.QPushButton("Cancel")

        self.place_widgets()
        self.file_type_changed(self._file_type_combo.currentText())

        self.setMinimumWidth(500)

    def place_widgets(self):

        self.setModal(True)

        self._text_path_data.textChanged.connect(self.text_field_changed)
        self._btn_browse_data.clicked.connect(self._file_loader.get_file_data)
        self._text_path_format.textChanged.connect(self.text_field_changed)
        self._btn_browse_format.clicked.connect(self._file_loader.get_file_format)

        self.setWindowTitle("Import Data From File")

        layout_vertical_sections = QtWidgets.QVBoxLayout()
        self.setLayout(layout_vertical_sections)

        # Grid Layout - Widgets

        for file_type in self._file_loader.data_formats_available:
            self._file_type_combo.addItem(repr(file_type))

        self._file_type_h_box.addWidget(QtWidgets.QLabel('Data File Type'))
        self._file_type_h_box.addWidget(self._file_type_combo)
        self._file_type_h_box.addStretch()

        self._file_type_combo.setCurrentText(self._controller.settings.default_file_type)
        self._file_type_combo.currentTextChanged.connect(self.file_type_changed)
        layout_vertical_sections.addLayout(self._file_type_h_box)

        # File Location Section

        self._file_browsing_grid.addWidget(self._label_data, 0, 0)
        self._file_browsing_grid.addWidget(self._text_path_data, 0, 1)
        self._file_browsing_grid.addWidget(self._btn_browse_data, 0, 2)
        self._file_browsing_grid.addWidget(self._label_format, 1, 0)
        self._file_browsing_grid.addWidget(self._text_path_format, 1, 1)
        self._file_browsing_grid.addWidget(self._btn_browse_format, 1, 2)
        self._btn_browse_data.setAutoDefault(False)
        self._btn_browse_format.setAutoDefault(False)
        layout_vertical_sections.addLayout(self._file_browsing_grid)
        layout_vertical_sections.addStretch()

        # Final Buttons Section

        layout_final_buttons = QtWidgets.QHBoxLayout()
        layout_final_buttons.addStretch()

        # Cancel button.
        self._btn_cancel.clicked.connect(self.close)
        layout_final_buttons.addWidget(self._btn_cancel)

        # Submit button.
        self._btn_submit.setDefault(True)
        self._btn_submit.pressed.connect(self._file_loader.pass_files)
        self._btn_submit.setShortcut(QtGui.QKeySequence('Return'))
        self._btn_submit.setEnabled(False)
        self._btn_submit.setFocus()
        layout_final_buttons.addWidget(self._btn_submit)

        layout_vertical_sections.addLayout(layout_final_buttons)

    def file_type_changed(self, current_text=None):
        # _file_loader calls text_field_changed
        self._file_loader.file_type_changed(current_text, self)

    def text_field_changed(self, new_text=None):
        self._file_loader.check_files()
