from PyQt5 import QtWidgets, QtCore, QtGui


class IdentifiableButton(QtWidgets.QPushButton):

    def __init__(self, parent, controller, *args, **kwargs):
        super(IdentifiableButton, self).__init__(*args, **kwargs)

        self.step_parent = parent
        self.controller = controller
        self.id = controller.new_id() if parent else -1
        self._text = self.text()
        self._enabled = True
        self.setToolTip(self.debug_str)
        self.setStatusTip(self.debug_str)

    @property
    def root_parent(self):
        return self.step_parent.root_parent

    @property
    def edit_mode(self):
        return self.controller.edit_mode

    @edit_mode.setter
    def edit_mode(self, toggle: bool):
        if self._enabled:
            if toggle:
                self.show()
            else:
                self.hide()
        else:
            self.hide()

    @property
    def debug_mode(self):
        return self.controller.debug_mode

    @debug_mode.setter
    def debug_mode(self, toggle: bool):
        if self.icon():
            pass

        else:
            if toggle:
                if not self.debug_mode:
                    self._text = self.text()

                self.setText(self.__str__())

            else:
                self.setText(self._text)

    def set_enabled(self, enabled: bool):

        if enabled and self.edit_mode:
            self.setVisible(True)

        else:
            self.setVisible(False)

        self._enabled = enabled

    def __str__(self):
        return "ID: " + str(self.id)

    def __repr__(self):
        return self.debug_str

    @property
    def debug_str(self):
        return str(self) + " " + str(type(self))


class ExtraWideButton(IdentifiableButton):

    def __init__(self, *args, **kwargs):
        super(ExtraWideButton, self).__init__(*args, **kwargs)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)

    def sizeHint(self) -> QtCore.QSize:
        default_btn = QtWidgets.QPushButton()
        return QtCore.QSize(40, default_btn.sizeHint().height())


class ExtraTallButton(IdentifiableButton):

    def __init__(self, *args, **kwargs):
        super(ExtraTallButton, self).__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)

    def sizeHint(self) -> QtCore.QSize:
        default_btn = QtWidgets.QPushButton()
        return QtCore.QSize(default_btn.sizeHint().height(), 40)


class ExtraLargeButton(IdentifiableButton):

    def __init__(self, *args, **kwargs):
        super(ExtraLargeButton, self).__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(40, 40)


class ExtraSmallButton(IdentifiableButton):

    def __init__(self, *args, **kwargs):
        super(ExtraSmallButton, self).__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(23, 23)


class ImageIdentifiableButton(ExtraLargeButton):

    def __init__(self, *args, **kwargs):
        super(ImageIdentifiableButton, self).__init__(*args, **kwargs)

        self.installEventFilter(self)
        self.hidden_icon = QtGui.QIcon()
        self.hidden_icon_saved = False
        self.hover_icon = QtGui.QIcon()
        self.hover_icon_set = False
        self.hovered = False

        self.minSize = 8
        self.ar = 1.5
        self.pad = 10

    @ExtraLargeButton.edit_mode.setter
    def edit_mode(self, toggle):
        self.setEnabled(toggle)

        if toggle:
            if self.hovered:
                self.HoverEnter(None)

        else:
            self.HoverLeave(None)

    def set_hidden_icon(self, icon_path):
        self.hidden_icon = QtGui.QIcon(icon_path)
        self.setIcon(self.hidden_icon)
        self.hidden_icon_saved = True

    def set_hover_icon(self, icon_path):
        self.hover_icon = QtGui.QIcon(icon_path)
        self.hover_icon_set = True

    def eventFilter(self, a0, a1):

        if a1.type() == QtCore.QEvent.HoverEnter:
            self.HoverEnter(a1)

        if a1.type() == QtCore.QEvent.HoverLeave:
            self.HoverLeave(a1)

        return super(ImageIdentifiableButton, self).eventFilter(a0, a1)

    def HoverEnter(self, *_):
        self.hovered = True
        if self.controller.edit_mode:
            if self.hover_icon_set:
                self.setIcon(self.hover_icon)

    def HoverLeave(self, *_):
        self.hovered = False
        if self.hidden_icon_saved:
            self.setIcon(self.hidden_icon)

    def paintEvent(self, event):
        """
        https://stackoverflow.com/questions/31742194/dynamically-resize-qicon-without-calling-setsizeicon
        :param event:
        :return:
        """

        qp = QtGui.QPainter()
        qp.begin(self)

        # Get default style

        opt = QtWidgets.QStyleOptionButton()
        self.initStyleOption(opt)

        # Scale icon to button size

        rect = opt.rect
        h = rect.height()
        w = rect.width()

        if self.hovered and self.edit_mode:
            icon_size = max(int(min(h, w)) - 2 * self.pad, self.minSize)

        else:
            icon_size = max(int(max(h*self.ar, w)) + 1, self.minSize)

        opt.iconSize = QtCore.QSize(icon_size, icon_size)

        # Draw button

        self.style().drawControl(QtWidgets.QStyle.CE_PushButton, opt, qp, self)

        qp.end()


# Subclassing these so they can be individually addressed in the QSS


class SquareButton(QtWidgets.QPushButton):
    pass


class RightSideButton(ExtraTallButton):
    pass


class LeftSideButton(ExtraTallButton):
    pass


class TopSideButton(ExtraWideButton):
    pass


class BottomSideButton(ExtraWideButton):
    pass


class HorzAddButton(ExtraWideButton):
    pass


class HorzRmvButton(ExtraWideButton):
    pass


class VertAddButton(ExtraTallButton):
    pass


class VertRmvButton(ExtraTallButton):
    pass


class SquareCloseButton(ExtraSmallButton):
    pass


class SquareRotateButton(ExtraSmallButton):
    pass


class RowFrame(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super(RowFrame, self).__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
