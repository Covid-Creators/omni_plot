from PyQt5 import QtWidgets, QtGui, QtCore
import widgets.buttons as buttons
from plugins.content_editor_popup import ContentEditorPopup
from widgets.animations.abstract_animation import AbstractAnimation
from plugins.supported_plugins import SUPPORTED_CONTENT_WIDGETS


class InteractiveLayout(QtWidgets.QFrame):

    def __init__(self, parent, controller, layout=None, *args, **kwargs):
        super(InteractiveLayout, self).__init__(*args, **kwargs)

        self.step_parent = parent
        self.controller = controller
        self.id = self.step_parent.new_id()
        self.title = None

        self.central_widget = None
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self.construct_from_json_dict(layout)

        # Can't figure out how to move this to style.qss
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    @property
    def root_parent(self):
        return self.step_parent.root_parent

    @property
    def edit_mode(self):
        return self.controller.edit_mode

    @edit_mode.setter
    def edit_mode(self, toggle: bool):

        self.central_widget.edit_mode = toggle

    @property
    def debug_mode(self):
        return self.controller.debug_mode

    @debug_mode.setter
    def debug_mode(self, toggle: bool):
        self.central_widget.debug_mode = toggle

    def new_id(self):
        return self.step_parent.new_id()

    @property
    def json_key(self):
        return 'Interactive Layout'

    def construct_from_default(self):
        self.central_widget = InteractiveLayoutHandler(self, self.controller)
        self.main_layout.addWidget(self.central_widget)

    def construct_from_json_dict(self, json_dict):
        if json_dict:
            for key, layout_type in LAYOUTS.items():
                if key in json_dict:
                    self.central_widget = layout_type(
                        parent=self,
                        controller=self.controller,
                        json_dict=json_dict[key])

                    self.main_layout.addWidget(self.central_widget)

        else:
            self.construct_from_default()

    def generate_json_dict(self):
        return {self.json_key: self.central_widget.generate_json_dict()}

    def replace_kid(self, new_instance, old_kid, and_delete_existing=False):

        new_instance.setParent(self)
        new_instance.step_parent = self
        if and_delete_existing:
            old_kid.setParent(None)

        for i in reversed(range(self.main_layout.count())):
            self.main_layout.removeWidget(self.main_layout.itemAt(i).widget())

        self.central_widget = new_instance
        self.main_layout.addWidget(new_instance)

    def __repr__(self):
        return "Interactive Layout [ID: " + str(self.id) + "] (Contains " + repr(self.central_widget) + ")"


class InteractiveLayoutHandler(QtWidgets.QFrame):

    def __init__(self, parent, controller, json_dict=None, initial_content=None, *args, **kwargs):
        super(InteractiveLayoutHandler, self).__init__(*args, **kwargs)

        self.step_parent = parent
        self._controller = controller
        self.contains_display = False
        self.title = None
        self.popup = None
        self.id = self.step_parent.new_id()

        self.main_layout = QtWidgets.QGridLayout()
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.btn_add_display = buttons.ImageIdentifiableButton(self, self._controller)
        self.btn_go_horizontal = buttons.RightSideButton(self, self._controller)
        self.btn_go_vertical = buttons.BottomSideButton(self, self._controller)

        self.btn_add_display.set_hidden_icon(QtGui.QIcon(self._controller.serializer.get_new_image_path()))
        self.btn_add_display.set_hover_icon(QtGui.QIcon(self._controller.serializer.get_plot_btn_path()))

        self.buttons = [self.btn_add_display, self.btn_go_horizontal, self.btn_go_vertical]

        if initial_content or json_dict:
            self.contains_display = True
            self.content_widget = None

            if json_dict:

                for key, layout_type in LAYOUTS.items():
                    if key in json_dict:
                        self.content_widget = layout_type(
                            parent=self,
                            controller=self._controller,
                            json_dict=json_dict[key])

                        break

                for key, (_, content_type) in SUPPORTED_CONTENT_WIDGETS.items():
                    if key in json_dict:
                        self.content_widget = content_type(
                            controller=self._controller,
                            layout_handler=self,
                            json_dict=json_dict[key])

                        break

                if isinstance(self.content_widget, AbstractAnimation):
                    self._controller.add_animation(self.content_widget)

            if not self.content_widget:
                self.content_widget = initial_content

            if self.content_widget:
                self.btn_add_display.hide()

            else:
                self.contains_display = False

        else:
            self.content_widget = None

        self.setup_ui()

    @property
    def root_parent(self):
        return self.step_parent.root_parent

    @property
    def edit_mode(self):
        return self._controller.edit_mode

    @edit_mode.setter
    def edit_mode(self, toggle: bool):

        for btn in [self.btn_go_vertical, self.btn_go_horizontal]:
            btn.edit_mode = toggle

        if self.contains_display:
            self.btn_add_display.edit_mode = False
            self.content_widget.edit_mode = toggle

        else:
            self.btn_add_display.edit_mode = toggle

    @property
    def debug_mode(self):
        return self._controller.debug_mode

    @debug_mode.setter
    def debug_mode(self, toggle: bool):

        for btn in self.buttons:
            btn.debug_mode = toggle

        if self.contains_display:
            self.content_widget.debug_mode = toggle

    def setup_ui(self):

        self.btn_go_horizontal.clicked.connect(self.go_horizontal)
        self.btn_go_vertical.clicked.connect(self.go_vertical)
        self.btn_add_display.clicked.connect(self.add_display)

        self.main_layout.setContentsMargins(0, 0, 0, 0)

        if self.contains_display:
            self.main_layout.addWidget(self.content_widget, 1, 1)

        else:
            self.main_layout.addWidget(self.btn_add_display, 1, 1)

        self.main_layout.addWidget(self.btn_go_horizontal, 1, 2)
        self.main_layout.addWidget(self.btn_go_vertical, 2, 1)

        self.edit_mode = self._controller.edit_mode
        self.debug_mode = self._controller.debug_mode

    @property
    def json_key(self):
        return 'InteractiveLayoutHandler'

    def generate_json_dict(self):
        kid_dict = self.content_widget.generate_json_dict() if self.contains_display else None
        return {self.json_key: kid_dict}

    def add_display(self):
        self.popup = ContentEditorPopup(
            content_home=self,
            signal_tree=self._controller.popup_signal_tree,
            controller=self._controller,
        )

        self.popup.display_generated.connect(self.display_generated)
        self.popup.main = self
        self.popup.show()

    def display_generated(self, display):

        if display:
            if self.contains_display:
                self.content_widget.deleteLater()

            else:
                self.contains_display = True
                self.btn_add_display.hide()

            self.content_widget = display
            self.main_layout.addWidget(self.content_widget, 1, 1)

            if isinstance(display, AbstractAnimation):
                self._controller.add_animation(display)

    def close_display(self):
        self.close_tab(self.tabs_widget.currentIndex())

    def hide_horizontal_button(self):
        self.btn_go_horizontal.set_enabled(False)

    def hide_vertical_button(self):
        self.btn_go_vertical.set_enabled(False)

    def show_horizontal_button(self):
        if self.edit_mode:
            self.btn_go_horizontal.set_enabled(True)

    def show_vertical_button(self):
        if self.edit_mode:
            self.btn_go_vertical.set_enabled(True)

    def close(self):
        raise NotImplementedError

    def new_id(self):
        return self.step_parent.new_id()

    def go_horizontal(self):
        self.morph(vertical_not_horizontal=False)

    def go_vertical(self):
        self.morph(vertical_not_horizontal=True)

    def morph(self, vertical_not_horizontal: bool):

        old_parent = self.step_parent  # InteractiveBoxLayout sets the parent of each el in model to self

        new_type = InteractiveVBoxLayout if vertical_not_horizontal else InteractiveHBoxLayout

        new_instance = new_type(
            parent=self.step_parent,
            controller=self._controller,
            model=[self, ])

        if vertical_not_horizontal:
            new_instance.hide_vertical_buttons()
            new_instance.show_horizontal_buttons()

        else:
            new_instance.hide_horizontal_buttons()
            new_instance.show_vertical_buttons()

        old_parent.replace_kid(new_instance, self)

    def show_buttons(self):
        if not self.contains_display:
            self.btn_add_display.show()

    def hide_buttons(self):
        pass

    def replace_main_kid(self, new_kid):

        if self.contains_display:
            self.main_layout.removeWidget(self.content_widget)

        else:
            self.main_layout.removeWidget(self.btn_add_display)

        self.content_widget = new_kid
        self.main_layout.addWidget(self.content_widget, 1, 1)
        self.contains_display = True

    def __repr__(self):
        return ("AbstractAnimation" if self.contains_display else "Empty") + " Layout Handler [ID: " + str(self.id) + "]"


class AbstractInteractiveStackLayout(QtWidgets.QFrame):

    layout_changed = QtCore.pyqtSignal()

    def __init__(self, parent, controller, json_dict=None, model: list = None, num_el: int = 2, *args, **kwargs):
        """
        Number of elements in queue overrides num_el

        :param parent:
        :param use_stretches:
        :param model:
        :param num_el:
        :param args:
        :param kwargs:
        """
        super(AbstractInteractiveStackLayout, self).__init__(*args, **kwargs)

        self.step_parent = parent
        self.controller = controller
        self.id = self.step_parent.new_id()
        self._initial_model = json_dict if json_dict else model
        self._default_num_el = num_el

        self._horizontal_buttons_hidden = False
        self._vertical_buttons_hidden = False

        self.min_elements = self._default_num_el
        self.num_elements = 0
        self.max_elements = 6
        self._widget_list: [] = None

        self.btn_cls = buttons.SquareCloseButton(self, self.controller)
        self.btn_add: QtWidgets.QPushButton
        self.btn_rmv: QtWidgets.QPushButton
        self.btn_rot = buttons.SquareRotateButton(self, self.controller)

        self.btn_list: [] = None

        self.outer_layout: QtWidgets.QLayout() = None
        self.button_tray: QtWidgets.QLayout() = None
        self.central_layout: QtWidgets.QLayout() = None

        self.layout_changed.connect(self.update_buttons)

    @property
    def root_parent(self):
        return self.step_parent.root_parent

    @property
    def widget_list(self):
        self.layout_changed.emit()
        return self._widget_list

    @widget_list.setter
    def widget_list(self, new_list):
        self.layout_changed.emit()
        self._widget_list = new_list

    @property
    def edit_mode(self):
        return self.controller.edit_mode

    @edit_mode.setter
    def edit_mode(self, toggle: bool):

        for btn in self.btn_list:
            btn.edit_mode = toggle

        for el in self.widget_list:
            el.edit_mode = toggle

        self.layout_changed.emit()

    @property
    def debug_mode(self):
        return self.controller.debug_mode

    @debug_mode.setter
    def debug_mode(self, toggle: bool):

        for btn in self.btn_list:
            btn.debug_mode = toggle

        for i in range(self.central_layout.count()):
            self.central_layout.itemAt(i).widget().debug_mode = toggle

    @property
    def eq_args(self):
        """
        Used for reconstructing a similar object of different type
        Using property so that latest parameters are sent instead of the ones at timestamps of __init__.py.py

        :return:
        """
        return []

    @property
    def eq_kwargs(self):
        """
        Used for reconstructing a similar object of different type
        Using property so that latest parameters are sent instead of the ones at timestamps of __init__.py.py

        :return:
        """

        return {'model': self.get_model()}

    @property
    def shape_str(self) -> str:

        raise NotImplementedError

    def setup_ui(self):

        if self._initial_model is None:
            self.construct_from_num_el()

        else:
            if isinstance(self._initial_model, list):
                if isinstance(self._initial_model[0], dict):
                    self.construct_from_json_dict(self._initial_model)

                else:
                    self.construct_from_widget_list(self._initial_model)

        self.setLayout(self.outer_layout)

        self.btn_cls.clicked.connect(self.close_widget)
        self.btn_add.clicked.connect(self.add_el)
        self.btn_rmv.clicked.connect(self.rmv_el)
        self.btn_rot.clicked.connect(self.morph)

        self.set_local_layouts()
        self.place_buttons()

        self.outer_layout.setSpacing(0)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        self.button_tray.setSpacing(0)

        self.btn_list = [self.btn_cls, self.btn_add, self.btn_rmv, self.btn_rot]

    @QtCore.pyqtSlot()
    def update_buttons(self):

        last_type = None
        all_the_same = True

        if not self._widget_list:
            return

        if len(self._widget_list) == 1:
            all_the_same = False

        else:
            for el in self._widget_list:
                if last_type is None:
                    last_type = type(el)
                    continue

                if not type(el) == last_type:
                    all_the_same = False
                    break

        if all_the_same:
            if isinstance(self, InteractiveHBoxLayout):
                self.show_vertical_buttons()
                self.hide_horizontal_buttons()

            elif isinstance(self, InteractiveVBoxLayout):
                self.show_horizontal_buttons()
                self.hide_vertical_buttons()

        else:
            self.show_horizontal_buttons()
            self.show_vertical_buttons()

    @property
    def json_key(self):
        raise NotImplementedError

    def generate_json_dict(self):

        return {self.json_key: [w.generate_json_dict() for w in self.widget_list]}

    def construct_from_json_dict(self, json_dict):

        num_added = 0
        self.widget_list = []

        for el in json_dict:
            w = None
            for key, new_type in LAYOUTS.items():
                if key in el:
                    w = new_type(self, self.controller, el[key])

            if w:
                w.setParent(self)
                w.step_parent = self
                self.add_el(element=w)

            else:
                self.add_el()

            num_added += 1

    def construct_from_widget_list(self, model: list):
        """
        Because self.model_stack strips out RemovableStretches, it is assumed that the model only contains elements
        :param model:
        :return:
        """
        num_added = 0
        self.widget_list = []

        for el in model:
            if isinstance(el, QtWidgets.QWidget):
                w = el

            elif isinstance(el, QtWidgets.QWidgetItem):
                w = el.widget()

            else:
                raise TypeError

            w.setParent(self)
            w.step_parent = self
            self.add_el(element=w)
            num_added += 1

        while num_added < self._default_num_el:
            self.add_el()
            num_added += 1

    def get_model(self):
        model = []
        for i in range(self.central_layout.count()):
            model.append(self.central_layout.itemAt(i))

        return model

    def replace_kid(self, new_kid, old_kid, and_delete_existing=False):
        index = self.widget_list.index(old_kid)
        if index < 0:
            self.add_el(new_kid)

        else:
            self.replace_el(index, new_kid, and_delete_existing=and_delete_existing)

    def new_id(self):
        return self.step_parent.new_id()

    def get_main_layout(self):
        return self.outer_layout

    def close_widget(self):

        while self.central_layout.count() > 1:
            self.rmv_el(close_override=True)

        widget = self.rmv_el(delete_widget=False, close_override=True)

        widget.setParent(self.step_parent)
        widget.step_parent = self.step_parent
        self.step_parent.replace_kid(widget, self, and_delete_existing=True)

    def set_local_layouts(self):
        """
        Must be implemented in child class
        :return:
        """
        raise NotImplementedError

    def place_buttons(self):
        """
        Must be implemented in child class
        :return:
        """
        raise NotImplementedError

    def morph(self):
        if isinstance(self, InteractiveHBoxLayout):
            new_instance = InteractiveVBoxLayout(self.step_parent, self.controller, *self.eq_args, **self.eq_kwargs)
            new_instance.show_horizontal_buttons()

        elif isinstance(self, InteractiveVBoxLayout):
            new_instance = InteractiveHBoxLayout(self.step_parent, self.controller, *self.eq_args, **self.eq_kwargs)
            new_instance.show_vertical_buttons()

        else:
            raise NotImplementedError

        self.step_parent.replace_kid(new_instance, self, and_delete_existing=True)

    def add_el(self, *_, element=None) -> bool:
        """
        Because add_el is a slot, the _signal will pass some obj parameters to it.
        Specific widget to add must be given 'element' keyword

        :param element:
        :return: True if able to add, False if layout is full (self.max_elements reached)
        """

        if self.num_elements < self.max_elements:

            self.num_elements += 1

            w = InteractiveLayoutHandler(self, self.controller) if element is None else element

            try:
                if self._horizontal_buttons_hidden:
                    w.hide_horizontal_button()

                if self._vertical_buttons_hidden:
                    w.hide_vertical_button()

            except AttributeError:
                pass

            if isinstance(w, QtWidgets.QWidgetItem):
                w = w.widget()

            self.central_layout.addWidget(w)
            self.widget_list.append(w)

            return True

        else:
            return False

    def rmv_el(self, *_, element=None, index: int = None, delete_widget=True, close_override=False):
        """
        If element is not None, index is ignored. If neither element nor index is passed,
        the last element in the list will be removed
        :param element:
        :param index:
        :param delete_widget:
        :param close_override:
        :return:
        """

        w = None

        if self.num_elements > self.min_elements or close_override:

            self.num_elements -= 1

            if not element:
                w = self.central_layout.itemAt(index) \
                    if index else self.central_layout.itemAt(self.central_layout.count()-1)

            if isinstance(w, QtWidgets.QWidgetItem):
                w = w.widget()

            self.central_layout.removeWidget(w)
            self.widget_list.remove(w)

            if delete_widget:
                w.deleteLater()

        else:
            self.close_widget()

        return w

    def replace_el(self, index, element, and_delete_existing=False):

        forward_list_to_leave_unchanged = []

        if len(self.widget_list) <= index:
            if self.central_layout.count() == index:
                self.add_el(element)

            else:
                raise ValueError

        if self.debug_mode:
            print("Inserting {"+repr(element)+"} at " + str(index) + " in "+repr(self))
            print(self.widget_list)

        while len(self.widget_list) > index+1:
            widget = self.widget_list[-1]
            self.widget_list.remove(widget)
            self.central_layout.removeWidget(widget)
            forward_list_to_leave_unchanged.insert(0, widget)

        existing = self.widget_list[-1]
        self.widget_list.remove(existing)
        self.central_layout.removeWidget(existing)

        if and_delete_existing:
            existing.setParent(None)

        self.widget_list.append(element)
        self.central_layout.addWidget(element)

        while len(forward_list_to_leave_unchanged):
            widget = forward_list_to_leave_unchanged.pop(0)
            self.widget_list.append(widget)
            self.central_layout.addWidget(widget)

        if self.debug_mode:
            print(self.widget_list)

    def hide_horizontal_buttons(self):
        self._horizontal_buttons_hidden = True
        for w in self._widget_list:
            if isinstance(w, InteractiveLayoutHandler):
                w.hide_horizontal_button()

    def hide_vertical_buttons(self):
        self._vertical_buttons_hidden = True
        for w in self._widget_list:
            if isinstance(w, InteractiveLayoutHandler):
                w.hide_vertical_button()

    def show_horizontal_buttons(self):
        self._horizontal_buttons_hidden = False
        for w in self._widget_list:
            if isinstance(w, InteractiveLayoutHandler):
                w.show_horizontal_button()

    def show_vertical_buttons(self):
        self._vertical_buttons_hidden = False
        for w in self._widget_list:
            if isinstance(w, InteractiveLayoutHandler):
                w.show_vertical_button()

    def __repr__(self):
        return self.shape_str + " Stack [ID: " + str(self.id) + "] stack=" + str(self.widget_list)


class InteractiveHBoxLayout(AbstractInteractiveStackLayout):

    def __init__(self, *args, **kwargs):
        super(InteractiveHBoxLayout, self).__init__(*args, **kwargs)

        self.outer_layout = QtWidgets.QHBoxLayout()
        self.button_tray = QtWidgets.QVBoxLayout()
        self.central_layout = QtWidgets.QHBoxLayout()

        self.btn_add = buttons.VertAddButton(self, self.controller)
        self.btn_rmv = buttons.VertRmvButton(self, self.controller)

        self.setup_ui()

    @property
    def shape_str(self) -> str:
        return "Horizontal"

    @property
    def json_key(self):
        return 'InteractiveHBoxLayout'

    def set_local_layouts(self):
        self.outer_layout.addLayout(self.central_layout)
        self.outer_layout.addLayout(self.button_tray)

    def place_buttons(self):
        self.button_tray.addWidget(self.btn_cls)
        self.button_tray.addWidget(self.btn_add)
        self.button_tray.addWidget(self.btn_rmv)
        self.button_tray.addWidget(self.btn_rot)


class InteractiveVBoxLayout(AbstractInteractiveStackLayout):

    def __init__(self, *args, **kwargs):
        super(InteractiveVBoxLayout, self).__init__(*args, **kwargs)

        self.outer_layout = QtWidgets.QVBoxLayout()
        self.button_tray = QtWidgets.QHBoxLayout()
        self.central_layout = QtWidgets.QVBoxLayout()

        self.btn_add = buttons.HorzAddButton(self, self.controller)
        self.btn_rmv = buttons.HorzRmvButton(self, self.controller)

        self.setup_ui()

    @property
    def shape_str(self) -> str:

        return "Vertical"

    @property
    def json_key(self):
        return 'InteractiveVBoxLayout'

    def set_local_layouts(self):
        self.outer_layout.addLayout(self.central_layout)
        self.outer_layout.addLayout(self.button_tray)

    def place_buttons(self):
        self.button_tray.addWidget(self.btn_cls)
        self.button_tray.addWidget(self.btn_rmv)
        self.button_tray.addWidget(self.btn_add)
        self.button_tray.addWidget(self.btn_rot)


class RemovableStretch(QtWidgets.QSpacerItem):

    def __init__(self):
        super(RemovableStretch, self).__init__(
            10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


class BlankWidget(QtWidgets.QLabel):

    def __init__(self, parent, string, color=QtCore.Qt.red, *args, **kwargs):
        super(BlankWidget, self).__init__(string, *args, **kwargs)

        self.step_parent = parent
        self.id = self.step_parent.new_id()

        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)

        self.setMinimumSize(10, 10)


class DynamicForm(QtWidgets.QFormLayout):

    def __init__(self, *args, **kwargs):
        super(DynamicForm, self).__init__(*args, **kwargs)

        self._row_count = 0
        self._labels: [QtWidgets.QLabel] = []

    @property
    def row_count(self):
        return self._row_count

    @property
    def labels(self) -> [QtWidgets.QLabel]:
        return self._labels

    def addRow(self, label: str or QtWidgets.QLabel,
               *widgets: QtWidgets.QWidget or QtWidgets.QLayout or [QtWidgets.QWidget] or [QtWidgets.QLayout]):

        if isinstance(widgets, list) or isinstance(widgets, tuple):
            anonymous_row = QtWidgets.QHBoxLayout()
            for w in widgets:
                if isinstance(w, QtWidgets.QWidget):
                    anonymous_row.addWidget(w)

            widget = anonymous_row

        else:
            widget = widgets

        if not isinstance(label, QtWidgets.QLabel):
            label = QtWidgets.QLabel(label)

        super(DynamicForm, self).addRow(label, widget)
        self._labels.append(label)
        self._row_count += 1

    def set_row_label(self, index: int, label: str or QtWidgets.QLabel):
        if not isinstance(label, QtWidgets.QLabel):
            self._labels[index].setText(label)

        else:
            self._labels[index] = label

    def set_row_invisible(self, row: int):
        self.set_row_visibility(row, visible=False)
        self._labels[row].setVisible(False)

    def set_row_visible(self, row: int):
        self.set_row_visibility(row, visible=True)
        self._labels[row].setVisible(True)

    def set_row_visibility(self, row: int or QtWidgets.QWidget or QtWidgets.QLayout, visible: bool = True):

        if isinstance(row, int):
            row = self.itemAt((row*2)+1)

        self.recursive_set_visibility(row, visible=visible)

    @staticmethod
    def recursive_set_visibility(spam: QtWidgets.QWidget or QtWidgets.QLayout, visible: bool = True):

        if isinstance(spam, QtWidgets.QLayout):
            for i in range(spam.count()):
                DynamicForm.recursive_set_visibility(spam.itemAt(i), visible=visible)

        elif isinstance(spam, QtWidgets.QWidget):
            spam.setVisible(visible)

        else:
            try:
                spam_layout = spam.layout()
                if spam_layout:
                    for i in range(spam_layout.count()):
                        DynamicForm.recursive_set_visibility(spam.itemAt(i), visible=visible)
                else:
                    spam.widget().setVisible(visible)

            except Exception as e:
                print(e)
                raise e


LAYOUTS = {
    'InteractiveLayout': InteractiveLayout,
    'InteractiveLayoutHandler': InteractiveLayoutHandler,
    'InteractiveHBoxLayout': InteractiveHBoxLayout,
    'InteractiveVBoxLayout': InteractiveVBoxLayout}
