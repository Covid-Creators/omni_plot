from PyQt5 import QtWidgets


class AbstractContentEditor(QtWidgets.QWidget):

    json_key: str = NotImplemented
    human_readable_type: str = NotImplemented

    def __init__(self, controller, content_home, *args, content_widget=None, **kwargs):
        super(AbstractContentEditor, self).__init__(*args, **kwargs)

        self._controller = controller
        self._content_home = content_home  # The place where the content should go when the _popup closes
        self._content_widget = content_widget

        self._outer_h_box = QtWidgets.QHBoxLayout()
        self._settings_editor_h_box = QtWidgets.QHBoxLayout()

        # Child class must call self.setup_ui() at end of __init__

    def setup_ui(self):
        self.setLayout(self._outer_h_box)

        margins = self._outer_h_box.contentsMargins()
        self._outer_h_box.setContentsMargins(0, margins.top(), 0, 0)
        self._outer_h_box.addLayout(self._settings_editor_h_box)
        self._outer_h_box.addWidget(self._content_widget)

    @property
    def content_widget(self):
        return self._content_widget

    @property
    def content_home(self):
        return self._content_home

    def set_content_widget(self, widget, delete_existing=True):
        """
        Can clear content_widget if widget == None
        :param widget:
        :param delete_existing:
        :return:
        """
        if self._content_widget is not None:
            self._outer_h_box.removeWidget(self._content_widget)

            if delete_existing:
                self._content_widget.setParent(None)

        self._content_widget = widget

        if widget is not None:
            self._outer_h_box.addWidget(widget)

    def create_content_widget(self):
        raise NotImplementedError

