from PyQt5 import QtWidgets, QtCore

from data_flow.signals import Signal
from data_flow.data_set import DataSet


class SignalTree(QtWidgets.QWidget):

    signal_selected = QtCore.pyqtSignal(object)
    signal_request_width = QtCore.pyqtSignal(int)

    def __init__(self, controller, hidden_properties, *args, **kwargs):
        super(SignalTree, self).__init__(*args, **kwargs)

        self._controller = controller

        self._outer_v_box = QtWidgets.QVBoxLayout()
        self._refresh_h_box = QtWidgets.QHBoxLayout()
        self._check_overwrite = QtWidgets.QCheckBox('Overwrite Existing')
        self._btn_refresh = QtWidgets.QPushButton('Refresh')
        self._channel_selectors = QtWidgets.QTreeWidget()
        self._available_signal_properties: [str] = list(Signal([]).property_keys)
        self._hidden_signal_properties: [str] = hidden_properties

        self.setup_ui()

    def setup_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)

        self.setLayout(self._outer_v_box)
        self._outer_v_box.setContentsMargins(0, 0, 0, 0)

        # Refresh Button
        self._outer_v_box.addLayout(self._refresh_h_box)
        self._refresh_h_box.addWidget(self._btn_refresh)
        self._btn_refresh.clicked.connect(self._controller.refresh_data)
        self._refresh_h_box.addWidget(self._check_overwrite)
        self._check_overwrite.setChecked(self._controller.settings.overwrite_on_refresh)
        self._check_overwrite.toggled.connect(self.overwrite_toggle_changed)

        # Collapsible Lists - Signals.
        self._outer_v_box.addWidget(self._channel_selectors)

        self._channel_selectors.setDragEnabled(True)
        self._channel_selectors.setColumnCount(1 + len(self._available_signal_properties))
        self._channel_selectors.setHeaderLabels(['Signal', *self._available_signal_properties])
        self._channel_selectors.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self._channel_selectors.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._channel_selectors.itemClicked.connect(self.selected_signals_changed)

        header_widget = self._channel_selectors.header()
        header_widget.setStretchLastSection(False)
        header_widget.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        header_widget.customContextMenuRequested.connect(self.header_context_menu_requested)

    @property
    def margin_width(self):
        return 8

    def header_context_menu_requested(self, pos):

        menu = QtWidgets.QMenu(self)

        for prop in self._available_signal_properties:
            action = QtWidgets.QAction(prop, self)
            action.setCheckable(True)
            if prop not in self._hidden_signal_properties:
                action.setChecked(True)

            action.toggled.connect(lambda x, y=prop: self.toggle_property_column(y))

            menu.addAction(action)

        menu.popup(self._channel_selectors.header().mapToGlobal(pos))
        menu.show()

    def toggle_property_column(self, property_string):

        if property_string in self._hidden_signal_properties:
            self._hidden_signal_properties.remove(property_string)

        else:
            self._hidden_signal_properties.append(property_string)

        self._controller.save_hidden_columns(self._hidden_signal_properties, self)

        self.update_columns()

    def overwrite_toggle_changed(self, _):
        self._controller.set_overwrite_on_refresh(self._check_overwrite.isChecked(), self)

    def set_overwrite_toggle(self, toggle):
        self._check_overwrite.setChecked(toggle)

    def update_columns(self):
        self.update_signals(self._controller.data_store.data_sets)

    def update_signals(self, data_sets):
        property_keys = [key for key in self._available_signal_properties if key not in self._hidden_signal_properties]
        self._channel_selectors.setColumnCount(1+len(property_keys))
        self._channel_selectors.setHeaderLabels(['Signal', *property_keys])
        self.populate_tree(self._channel_selectors, data_sets, property_keys)

        self.auto_set_width()

    def auto_set_width(self):
        num_cols = self._channel_selectors.columnCount()

        total_requested_width = self.margin_width
        for i in range(num_cols):
            total_requested_width += self._channel_selectors.columnWidth(i)

        self.signal_request_width.emit(total_requested_width)

    def selected_signals_changed(self):

        selected_tree_item = self._channel_selectors.selectedItems()

        if len(selected_tree_item) == 1:
            selected_tree_item = selected_tree_item[0]

            signal_path = self.tree_item_to_signal_path(selected_tree_item)

            print(signal_path)
            self.signal_selected.emit(signal_path)

        elif len(selected_tree_item) == 0:
            pass

        else:
            raise ValueError

    @staticmethod
    def select_tree_items(tree, items):

        tree.selectionModel().clearSelection()

        all_items_selected = True

        if isinstance(items, dict):
            for key, value in items.items():
                if not SignalTree.select_tree_item(tree, key):
                    all_items_selected = False

        elif isinstance(items, list):
            for key in items:
                if not SignalTree.select_tree_item(tree, key):
                    all_items_selected = False

        else:
            all_items_selected = SignalTree.select_tree_item(tree, items)

        return all_items_selected

    @staticmethod
    def select_tree_item(tree, key):
        iterator = QtWidgets.QTreeWidgetItemIterator(tree)

        while iterator.value():
            child = iterator.value()
            child_name = SignalTree.tree_item_to_signal_path(child)

            if child_name == key:
                child.setSelected(True)
                return True

            iterator += 1

        return False

    @staticmethod
    def get_widget_item_by_name(parent, name):

        if parent:
            for i in range(parent.childCount()):
                child = parent.child(i)
                if child.text(0) == name:
                    return child

        return None

    @staticmethod
    def tree_item_to_signal_path(child):

        path = child.text(0)
        parent = child.parent()
        while parent:
            path = parent.text(0) + '/' + path
            child = parent
            parent = child.parent()

        return path

    @staticmethod
    def populate_tree(tree, content_dict, property_keys=None):

        # Because it's recursive, don't clear child widgets
        clear_func = getattr(tree, 'clear', None)
        if callable(clear_func):
            tree.clear()

        # Populate tree widget with groups and channels.
        for key, value in content_dict.items():
            if isinstance(value, Signal):
                properties = value.get_property_strings(property_keys)
                parent = QtWidgets.QTreeWidgetItem(tree, [key, *properties])

            else:
                parent = QtWidgets.QTreeWidgetItem(tree, [key])
                parent.setFlags(parent.flags() & ~QtCore.Qt.ItemIsSelectable)
                parent.setExpanded(True)

            if isinstance(value, dict):
                SignalTree.populate_tree(parent, value, property_keys)

            elif isinstance(value, DataSet):
                SignalTree.populate_tree(parent, value.signal_dict, property_keys)
