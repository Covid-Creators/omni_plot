from widgets.toggle import EditAndDebug
from main_gui import MainWindow
from settings.settings import Settings

from data_flow.serializer.serializer import Serializer
from data_flow.playback_manager import PlaybackManager
from data_flow.data_store import DataStore
from data_flow.signal_tree import SignalTree
from plugins.content_editor_popup import ContentEditorPopup
from widgets.playback_widget import PlaybackWidget


class Controller(EditAndDebug):

    def __init__(self, application):
        super(Controller, self).__init__()

        self._created_displays_counter = 0
        self._animations = {}
        self._popup = None

        self._settings = Settings(self, 'DynamicsToolBox', 'UserSettings', location='settings')
        self._serializer = Serializer(self)

        last_session = self.auto_load_workspace()
        self._playback_widget = PlaybackWidget()
        self._signal_tree_main = SignalTree(
            controller=self,
            hidden_properties=self.settings.hidden_columns_main,
        )
        self._signal_tree_popup = SignalTree(
            controller=self,
            hidden_properties=self.settings.hidden_columns_popup,
        )
        self._data_store = DataStore(
            controller=self,
            last_session=last_session.get('data_store') if last_session else None,
        )
        self._playback_manager = PlaybackManager(
            controller=self,
            playback_widget=self._playback_widget,
            playback_hz=30,
        )
        self._gui = MainWindow(
            controller=self,
            playback_widget=self._playback_widget,
            signal_tree=self._signal_tree_main,
            last_layout=last_session.get('layout') if last_session else None,
        )

        self._signal_tree_main.signal_request_width.connect(self._gui.set_signal_tree_width)
        self._data_store.data_store_changed.connect(self.update_data_views)

        if self.settings.geometry:
            self._gui.restoreGeometry(self.settings.geometry)

        # TODO I think inheriting from EditAndDebug is pointless.
        #  The children widgets are really the ones that should inherit from some kind of Editable class
        self.edit_mode = self.settings.edit_mode
        self.debug_mode = self.settings.debug_mode

        self.main_window.show()

        self.update_data_views()

        # application.processEvents()
        # self._signal_tree_main.auto_set_width()

    @property
    def main_window(self):
        return self._gui

    @property
    def settings(self):
        return self._settings

    @property
    def serializer(self):
        return self._serializer

    @property
    def data_store(self):
        return self._data_store

    @property
    def popup_signal_tree(self):
        return self._signal_tree_popup

    @property
    def animations(self):
        return self._animations

    @property
    def playback_manager(self):
        return self._playback_manager

    @property
    def playback_widget(self):
        return self._playback_widget

    @EditAndDebug.edit_mode.setter
    def edit_mode(self, toggle: bool):
        self._edit_mode = toggle
        self.settings.edit_mode = toggle
        self.main_window.edit_mode = toggle

    @EditAndDebug.debug_mode.setter
    def debug_mode(self, toggle: bool):
        self._debug_mode = toggle
        self.settings.debug_mode = toggle
        self.main_window.debug_mode = toggle

    def set_edit_mode(self, toggle):
        self.edit_mode = toggle

    def set_debug_mode(self, toggle: bool):
        self.debug_mode = toggle

    def set_overwrite_on_refresh(self, toggle, caller):
        self.settings.overwrite_on_refresh = toggle
        if caller is self._signal_tree_main:
            self._signal_tree_popup.set_overwrite_toggle(toggle)

        elif caller is self._signal_tree_popup:
            self._signal_tree_main.set_overwrite_toggle(toggle)

    def save_hidden_columns(self, hidden_signal_properties, caller):
        if caller is self._signal_tree_main:
            self.settings.hidden_columns_main = hidden_signal_properties

        elif caller is self._signal_tree_popup:
            self.settings.hidden_columns_popup = hidden_signal_properties

    def check_edit_and_debug_buttons(self):
        self.debug_mode = self._gui.toggle_debug_mode.isChecked()
        self.edit_mode = self._gui.toggle_edit_mode.isChecked()

    def refresh_data(self):
        self.data_store.refresh(self.settings.overwrite_on_refresh)

    def add_animation(self, animation):

        self.animations[animation.title] = animation
        if hasattr(animation, 'time_span'):
            self.playback_manager.update_time_range(*animation.time_bounds)

    def edit_display(self, display):

        if not self._popup:
            self._popup = ContentEditorPopup(
                content_home=display.content_home,
                signal_tree=self._signal_tree_popup,
                controller=self,
                existing_content=display,
            )

            self._popup.display_generated.connect(display.content_home.display_generated)

            self._popup.main = self

        self._popup.show()

    def popup_closed(self):
        self._popup = None

    def new_id(self):
        self._created_displays_counter += 1
        return self._created_displays_counter - 1

    def import_from_file(self):
        self._serializer.file_loader.open_popup()

    def update_data_views(self):
        self._signal_tree_main.update_signals(self._data_store.data_sets)
        self._signal_tree_popup.update_signals(self._data_store.data_sets)

    def generate_json_dict(self):
        return {'data_store': self.data_store.generate_json_dict(),
                'layout': self.main_window.tabs_widget.generate_json_dict()}

    def save_workspace_as(self):
        self.serializer.workspace.save_workspace_as(self.generate_json_dict())

    def quick_save_workspace(self):
        self.serializer.workspace.quick_save_workspace(self.generate_json_dict())

    def load_workspace(self):
        workspace = self.serializer.workspace.load_workspace_from()
        self.data_store.load_from_json_dict(workspace.get('data_store') if workspace else None)
        self.main_window.tabs_widget.construct_from_json_dict(workspace.get('layout') if workspace else None)

    def auto_save_workspace(self):
        self.serializer.workspace.auto_save_workspace(self.generate_json_dict())

    def auto_load_workspace(self):
        return self.serializer.workspace.auto_load_workspace()
