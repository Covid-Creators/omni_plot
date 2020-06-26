from PyQt5 import QtWidgets, QtGui


class AbstractContentWidget(QtWidgets.QWidget):

    json_key: str = NotImplemented
    human_readable_type: str = NotImplemented

    def __init__(self, controller, content_home, *args, title=None, json_dict=None, **kwargs):
        super(AbstractContentWidget, self).__init__(*args, **kwargs)

        self.setMinimumSize(100, 100)
        self.setMaximumSize(QtWidgets.QWIDGETSIZE_MAX, QtWidgets.QWIDGETSIZE_MAX)
        size_policy = self.sizePolicy()
        size_policy.setHorizontalPolicy(size_policy.MinimumExpanding)
        size_policy.setVerticalPolicy(size_policy.MinimumExpanding)
        self.setSizePolicy(size_policy)

        self._title = title
        self._json_dict = json_dict or {}

        self._controller = controller
        self._content_home = content_home
        self._grid_layout = QtWidgets.QGridLayout()
        self._settings_v_box = QtWidgets.QVBoxLayout()
        self._grid_layout.addLayout(self._settings_v_box, 1, 0)
        self.setLayout(self._grid_layout)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)

    def set_main_widget(self, widget):
        self._grid_layout.addWidget(widget, 1, 1)

    @property
    def title(self):
        if not self._title:
            self._title = self.json_key + '[' + self.content_str + ']'

        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def content_str(self):
        raise NotImplementedError

    def generate_json_dict(self):
        raise NotImplementedError

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._controller.edit_display(self)
