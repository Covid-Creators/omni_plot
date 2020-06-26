from PyQt5 import QtWidgets, QtCore
from widgets.interactive_layouts import InteractiveLayout


class InteractiveTab(QtWidgets.QTabWidget):

    def __init__(self, parent, controller, last_layout=None, *args, **kwargs):
        super(InteractiveTab, self).__init__(*args, **kwargs)

        self._in_init = True

        self.step_parent = parent
        self.controller = controller
        self.tab_list = []
        self.tab_btn_list = []
        self.was_edit_mode = False
        self.was_debug_mode = False
        self._hidden_new_tab_btn = None
        self._btn_default_size = None

        self.setTabBar(InteractiveTabBar(self))
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)

        if last_layout:
            self.construct_from_json_dict(last_layout)

        self.tabBar().tabBarDoubleClicked.connect(self.tab_double_clicked)
        self.currentChanged.connect(self.current_tab_changed)

        self._in_init = False

    @property
    def root_parent(self):
        return self.step_parent.root_parent

    @property
    def edit_mode(self) -> bool:
        return self.controller.edit_mode

    @edit_mode.setter
    def edit_mode(self, toggle: bool):

        if toggle and not self.was_edit_mode:
            self.show_new_tab_btn()

        elif not toggle and self.was_edit_mode:
            self.hide_new_tab_btn()

        for tab in self.tab_list:
            tab.edit_mode = toggle

        self.was_edit_mode = self.edit_mode

    @property
    def debug_mode(self) -> bool:
        return self.controller.debug_mode

    @debug_mode.setter
    def debug_mode(self, toggle: bool):

        for i, tab in enumerate(self.tab_list):

            if toggle:
                if not self.was_debug_mode or tab.title is None:
                    tab.title = self.tabText(i)

                self.setTabText(i, "ID: "+str(tab.id))

            else:
                if self.was_debug_mode:
                    self.setTabText(i, tab.title)

            tab.debug_mode = toggle

        self.was_debug_mode = self.debug_mode

    @property
    def num_tabs(self) -> int:
        return len(self.tab_list)

    @property
    def last_tab(self) -> int:
        index = len(self.tab_list) - 1
        return index if index >= 0 else None

    @property
    def last_real_tab(self) -> int:
        index = len(self.tab_list) - 2
        return index if index >= 0 else None

    @property
    def new_tab_btn(self) -> QtWidgets.QWidget:
        return self._hidden_new_tab_btn

    @new_tab_btn.setter
    def new_tab_btn(self, thing):
        self._hidden_new_tab_btn = thing

    def new_id(self):
        return self.controller.new_id()

    def construct_from_str_list(self, str_list: [str], index: int = 0):

        self._in_init = True

        self._delete_tabs()
        str_list = str_list or ['Main']

        for title in str_list:
            self.add_tab(title)

        self.show_new_tab_btn()
        self.set_current_tab(index)

        self._in_init = False

    def construct_from_json_dict(self, json_dict):

        if json_dict:

            self._in_init = True

            self._delete_tabs()

            for saved_tab in json_dict:
                for title, tab in saved_tab.items():
                    self.add_tab(title, layout=tab)

            if self.edit_mode:
                self.show_new_tab_btn()

            self.set_current_tab(self.controller.settings.tab_selected)

            self._in_init = False

    def generate_json_dict(self):

        json_dict = []

        for i, tab in enumerate(self.tab_list):

            if self.debug_mode:
                title = tab.title

            else:
                title = self.tabText(i)

            if i < len(self.tab_list)-1 or (i == len(self.tab_list)-1 and not self.edit_mode):
                json_dict.append({title: self.tab_list[i].generate_json_dict()})

        return json_dict

    def _delete_tabs(self):

        while self.tabBar().count() > 0:
            self.removeTab(self.tabBar().count()-1)

        self.tab_list = []

    def tab_double_clicked(self, index):
        if index < 0 or index == self.last_tab or not self.edit_mode:
            return

        current_title = self.tabBar().tabText(index)

        line_edit = QtWidgets.QLineEdit(self)
        line_edit.setText(current_title)

        self.tabBar().setTabText(index, '')

        left_side = self.tabBar().tabButton(index, QtWidgets.QTabBar.LeftSide)
        if left_side:
            left_side_layout = left_side.layout()
            temp_layout = QtWidgets.QHBoxLayout()
            temp_layout.addWidget(line_edit)
            left_side.setLayout(temp_layout)

        else:
            left_side_layout = None
            self.tabBar().setTabButton(index, QtWidgets.QTabBar.LeftSide, line_edit)

        line_edit.editingFinished.connect(lambda: self.rename_tab(index, line_edit, left_side_layout))

        line_edit.setFocusPolicy(QtCore.Qt.StrongFocus)
        QtCore.QTimer.singleShot(0, line_edit.setFocus)

    def rename_tab(self, index, line_edit, previous_layout):

        self.tabBar().setTabText(index, line_edit.text())

        if previous_layout:
            # TODO
            previous_layout('Layout too')

        else:
            self.tabBar().setTabButton(index, QtWidgets.QTabBar.LeftSide, None)

    def current_tab_changed(self, index: int):

        if not self._in_init:

            self.controller.settings.tab_selected = index

            if index < 0:
                self.add_tab('')

            if index >= self.last_tab and self.edit_mode:
                self.add_tab('', and_move_to=index)

            for i, tab in enumerate(self.tab_list):
                btn = self.tabBar().tabButton(i, QtWidgets.QTabBar.RightSide)

                if btn:
                    if i == index and self.edit_mode:
                        btn.show()

                    elif self.edit_mode:
                        btn.hide()

    def add_tab(self, title='', and_move_to=None, layout=None):

        layout = layout.get('Interactive Layout') if layout else None

        new_tab = InteractiveLayout(self, self.controller, layout)
        index = self.num_tabs or 0

        self.insertTab(index, new_tab, title)
        self.tab_list.append(new_tab)
        # self.tabBar().tabButton(self.last_tab, QtWidgets.QTabBar.RightSide).hide()

        if and_move_to:
            self.set_current_tab(and_move_to, override=True)

    def hide_new_tab_btn(self):

        self.removeTab(self.last_tab)
        self.tab_list.pop(self.last_tab)

    def show_new_tab_btn(self):

        self.add_tab()

    def set_current_tab(self, index: int, override=False):
        self.setCurrentIndex(index)
        if not override:
            self.current_tab_changed(index)

    def close_current_tab(self):

        current_tab = self.tabBar().currentIndex()
        self.close_tab(current_tab)

    def close_tab(self, i):

        current_index = self.currentIndex()
        last_real_tab = len(self.tab_list) - 2

        if i == current_index == last_real_tab:  # Closing last tab, and on last tab
            if i > 0:
                self.set_current_tab(i-1)

        self.tab_list.pop(i)
        self.removeTab(i)


class InteractiveTabBar(QtWidgets.QTabBar):

    def __init__(self, *args, **kwargs):
        super(InteractiveTabBar, self).__init__(*args, **kwargs)

        self.setAutoHide(True)
