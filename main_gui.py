import sys
import ctypes

from PyQt5 import QtWidgets, QtGui, QtCore

from widgets.tabs import InteractiveTab

# Hack to make icon show up in task bar
# https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
my_app_id = u'omni_plot.0.0.0'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, controller, playback_widget, signal_tree, last_layout=None, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.controller = controller

        # Apply startup characteristics for window.
        self.setWindowTitle("OmniPlot")  # TODO More general _name
        self.setGeometry(80, 80, 1250, 750)  # TODO Auto sizing and placement.

        self.menu_bar = self.menuBar()  # Along top of screen.
        self.file_menu = self.menu_bar.addMenu("&File")
        self.action_exit_gui = QtWidgets.QAction("&Exit")
        self.action_close_tab = QtWidgets.QAction("&Close Current Tab")
        self.edit_menu = self.menu_bar.addMenu("&Edit")
        self.data_menu = self.menu_bar.addMenu("&Data")
        self.action_select_stream_source = QtWidgets.QAction("Live &Stream...")
        self.action_import_from_database = QtWidgets.QAction("From &Database...")
        self.action_import_from_file = QtWidgets.QAction("From &File...")
        self.action_load_workspace = QtWidgets.QAction("Load W&orkspace...")
        self.toggle_edit_mode = QtWidgets.QAction()
        self.action_save_workspace_as = QtWidgets.QAction("&Save Workspace As...")
        self.action_quicksave_workspace = QtWidgets.QAction("&Save Workspace")
        self.toggle_debug_mode = QtWidgets.QAction()
        # self.tool_bar = self.addToolBar("Main Tool Bar")

        self._playback_widget = playback_widget
        self._signal_tree = signal_tree
        self._signal_tree_min_width = 0
        self._signal_tree_max_width = 500

        # CentralWidget houses layout features within the app.
        self._central_widget = QtWidgets.QWidget()
        self._status_bar = QtWidgets.QStatusBar()

        self._outer_v_box = QtWidgets.QVBoxLayout()
        self._main_h_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Tabs and stuff
        self.tabs_widget = InteractiveTab(self, self.controller)

        # Section for adding toolbar drop-downs and subsections.
        self.build_menu_and_tool_bars()

        # Sections for placing all layouts and widgets.
        self.place_widgets()

        # Holds instance of add tab _popup.
        self.popup = None

        if last_layout:
            self.tabs_widget.construct_from_json_dict(last_layout)

        else:
            self.tabs_widget.construct_from_str_list(['Main Tab', 'Tab 2', 'Tab 3'])

    @property
    def edit_mode(self):
        return self.controller.edit_mode

    @edit_mode.setter
    def edit_mode(self, toggle: bool):
        self.tabs_widget.edit_mode = toggle
        self.toggle_edit_mode.setChecked(toggle)

    @property
    def debug_mode(self):
        return self.controller.debug_mode

    @debug_mode.setter
    def debug_mode(self, toggle: bool):
        self.tabs_widget.debug_mode = toggle
        self.toggle_debug_mode.setChecked(toggle)
        self.statusBar().setVisible(toggle)

    def build_menu_and_tool_bars(self):

        # File DropDown

        # File drop down option - exit.
        self.action_exit_gui.setShortcut(QtGui.QKeySequence('Ctrl+Q'))
        self.action_exit_gui.triggered.connect(self.close_app)
        self.file_menu.addAction(self.action_exit_gui)

        self.file_menu.addSeparator()

        # Workspaces

        # File drop down option - Load Workspace.
        self.action_load_workspace.setShortcut(QtGui.QKeySequence("Ctrl+O"))
        self.action_load_workspace.triggered.connect(self.controller.load_workspace)
        self.file_menu.addAction(self.action_load_workspace)

        # File drop down option - Save Workspace As...
        self.action_save_workspace_as.triggered.connect(self.controller.save_workspace_as)
        self.file_menu.addAction(self.action_save_workspace_as)

        # File drop down option - Save Workspace As...
        self.action_quicksave_workspace.setShortcut(QtGui.QKeySequence("Ctrl+S"))
        self.action_quicksave_workspace.triggered.connect(self.controller.quick_save_workspace)
        self.action_quicksave_workspace.setEnabled(not self.controller.settings.loaded_workspace == '')
        self.file_menu.addAction(self.action_quicksave_workspace)

        self.file_menu.addSeparator()

        # Close it
        self.action_close_tab.setShortcut(QtGui.QKeySequence("Ctrl+W"))
        self.action_close_tab.triggered.connect(self.tabs_widget.close_current_tab)
        self.file_menu.addAction(self.action_close_tab)

        # Edit DropDown

        # File drop down option - Edit Mode.
        self.toggle_edit_mode.setText('&Edit Mode')
        self.toggle_edit_mode.setShortcut(QtGui.QKeySequence("Ctrl+E"))
        self.toggle_edit_mode.setCheckable(True)
        self.toggle_edit_mode.setChecked(self.controller.edit_mode)
        self.toggle_edit_mode.toggled.connect(self.controller.set_edit_mode)
        self.edit_menu.addAction(self.toggle_edit_mode)

        # File drop down option - Debug Mode.
        self.toggle_debug_mode.setText('&Debug Mode')
        self.toggle_debug_mode.setShortcut(QtGui.QKeySequence("Ctrl+D"))
        self.toggle_debug_mode.setCheckable(True)
        self.toggle_debug_mode.setChecked(self.controller.debug_mode)
        self.toggle_debug_mode.toggled.connect(self.controller.set_debug_mode)
        self.edit_menu.addAction(self.toggle_debug_mode)

        # Data Source

        # File drop down option - Listen to Stream.
        self.action_select_stream_source.setDisabled(True)
        self.action_select_stream_source.triggered.connect(self.select_stream_source)
        self.data_menu.addAction(self.action_select_stream_source)

        # File drop down option - Import Data from Database.
        self.action_import_from_database.setDisabled(True)
        self.action_import_from_database.triggered.connect(self.import_from_database)
        self.data_menu.addAction(self.action_import_from_database)

        # File drop down option - Import Data from File.
        self.action_import_from_file.setShortcut(QtGui.QKeySequence('Ctrl+F'))
        self.action_import_from_file.triggered.connect(self.import_from_file)
        self.data_menu.addAction(self.action_import_from_file)

        self.setStatusBar(self._status_bar)
        self._status_bar.setVisible(self.controller.debug_mode)

    def place_widgets(self):

        # Format Main Window

        # Create horizontal format for main widget subsections.
        self.setCentralWidget(self._central_widget)
        self._central_widget.setLayout(self._outer_v_box)

        self._outer_v_box.addWidget(self._main_h_splitter)
        self._outer_v_box.addWidget(self._playback_widget)

        # Main Window - Left Column
        self._main_h_splitter.addWidget(self._signal_tree)

        # Main Window - Middle Column
        self._main_h_splitter.addWidget(self.tabs_widget)
        self._main_h_splitter.setCollapsible(1, False)

    def set_signal_tree_width(self, width: int):

        splitter_width = self._main_h_splitter.width()

        splitter_sizes = self._main_h_splitter.sizes()

        allowed_width = max(self._signal_tree_min_width, min(width, self._signal_tree_max_width))
        # increase = allowed_width - splitter_sizes[0]

        splitter_sizes[0] = allowed_width
        splitter_sizes[1] = splitter_width - allowed_width

        self._main_h_splitter.setSizes(splitter_sizes)
        self._main_h_splitter.setStretchFactor(0, QtWidgets.QSizePolicy.Maximum)

    def select_stream_source(self):
        # TODO
        pass

    def import_from_database(self):
        # TODO
        pass

    def import_from_file(self):
        self.controller.import_from_file()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:

        self.controller.auto_save_workspace()
        self.controller.settings.geometry = self.saveGeometry()

        super(MainWindow, self).closeEvent(a0)

    @staticmethod
    def close_app():
        # On "File Dropdown - Exit" select exit program.
        sys.exit()
