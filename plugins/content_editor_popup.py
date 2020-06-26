import re
from PyQt5 import QtWidgets, QtCore, QtGui

from plugins.abstract_content_editor import AbstractContentEditor
from plugins.supported_plugins import SUPPORTED_CONTENT_EDITORS


class ContentEditorPopup(QtWidgets.QDialog):

    display_generated = QtCore.pyqtSignal(object)

    def __init__(self, controller, signal_tree, content_home, *args, existing_content=None, **kwargs):
        super(ContentEditorPopup, self).__init__(*args, **kwargs)

        self._controller = controller
        self._signal_tree = signal_tree
        self._content_home = content_home  # The place where the content should go when the _popup closes
        self._content = existing_content

        self._selected_content = None
        self._delete_content_on_close = True
        self._edit = False

        self._outer_v_box = QtWidgets.QVBoxLayout()
        self._content_tabs = QtWidgets.QTabWidget()
        self._content_editors = {}

        self._confirm_btn_h_box = QtWidgets.QHBoxLayout()
        self._btn_submit = QtWidgets.QPushButton("Submit")
        self._btn_cancel = QtWidgets.QPushButton("Cancel")

        self.load_content_editors()
        self.setup_ui()

        self.setModal(True)

    def load_content_editors(self):

        # Call __init__ for each content class to create an instance
        for key, (type_str, plugin_class) in SUPPORTED_CONTENT_EDITORS.items():
            self._content_editors[key] = (type_str, plugin_class(
                    controller=self._controller,
                    content_home=self._content_home,
            ))

    def setup_ui(self):

        self.setWindowTitle("Content Editor")
        self.setLayout(self._outer_v_box)

        # Editor Selection Section

        self._outer_v_box.addWidget(self._content_tabs)

        # Populate the tabs with AbstractContentEditor objects
        for key, (type_str, plugin_object) in self._content_editors.items():
            self._content_tabs.addTab(plugin_object, type_str)

        # Figure out what class
        if self._content:
            self._edit = True

            # TODO Figure out what type the content is
            # TODO Put the content in the right editor
            # TODO Set that tab as active

        else:

            # TODO Create content for active tab
            editor = self._content_tabs.widget(self._content_tabs.currentIndex())
            assert isinstance(editor, AbstractContentEditor)
            if not editor.content_widget:
                editor.create_content_widget()

            self._content = editor.content_widget

        self._selected_content = self._content.human_readable_type

        # Bottom Section

        self._outer_v_box.addLayout(self._confirm_btn_h_box)

        self._confirm_btn_h_box.addStretch()

        # Submit Tab Button.
        self._confirm_btn_h_box.addWidget(self._btn_submit)
        self._btn_submit.setFixedWidth(65)
        self._btn_submit.clicked.connect(self.confirm_display)
        self._btn_submit.setEnabled(False)

        # Cancel Tab Button.
        self._confirm_btn_h_box.addWidget(self._btn_cancel)
        self._btn_cancel.setFixedWidth(65)
        self._btn_cancel.clicked.connect(self.close)

        self.resize(1400, 600)

    def confirm_display(self):

        self.display_generated.emit(self._content)

        self._delete_content_on_close = False

        self.close()

    @staticmethod
    def increment_name(name):

        match = re.match(r'.*_([0-9]+)', name)
        if match:
            indices = match.regs[1]
            number = int(name[indices[0]:])
            name = name[0:indices[0]]
            name = name + str(number+1)

        else:
            name = name + '_1'

        return name

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:

        if self._delete_content_on_close and self._content:
            self._content.deleteLater()

        self._controller.popup_closed()

        return super(ContentEditorPopup, self).closeEvent(a0)
