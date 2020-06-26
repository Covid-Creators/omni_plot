import re
from PyQt5 import QtCore, QtWidgets

from data_flow.data_set import DataSet


class DataStore(QtWidgets.QWidget):

    data_store_changed = QtCore.pyqtSignal()

    def __init__(self, controller, last_session=None, *args, **kwargs):
        super(DataStore, self).__init__(*args, **kwargs)

        self._controller = controller
        self._data_sets = {}  #
        self._listeners = {}  # {listener (Animation): signal_patterns (List[str])}

        if last_session:
            self.load_from_json_dict(last_session)

    @property
    def data_sets(self):
        return self._data_sets

    def generate_json_dict(self):

        data_skeleton = {}
        for key, data_set in self._data_sets.items():
            assert isinstance(data_set, DataSet)
            data_skeleton[key] = data_set.generate_json_dict()

        return data_skeleton

    def load_from_json_dict(self, json_dict):

        if json_dict:

            self.clear_data_sets()

            for _, value in json_dict.items():

                file_type_key = value.get('import_method_type')
                file_format = self._controller.serializer.file_format_by_key(file_type_key)
                path_data = value.get('path_data')
                path_format = value.get('path_format')
                time_key = value.get('time_key')

                if path_format:
                    self.add_data_set(file_format.load(path_data, path_format), suspend_notification=True)

                else:
                    if time_key:
                        self.add_data_set(file_format.load(path_data, time_key), suspend_notification=True)

                    else:
                        self.add_data_set(file_format.load(path_data), suspend_notification=True)

            self.data_sets_changed()

    def clear_data_sets(self):

        # TODO Safety delete things

        self._data_sets = {}

    def data_sets_changed(self, data_sets_that_changed=None):

        self.notify_listeners(data_sets_that_changed)
        self.data_store_changed.emit()

    def refresh(self, overwrite_existing):

        new_data_sets = {}
        changed_data_sets = []

        data_sets_changed = False
        for key, data_set in self._data_sets.items():
            new_set = data_set.refresh()

            if new_set == data_set:
                print(key + ' ingored')
                continue

            else:
                data_sets_changed = True
                changed_data_sets.append(new_set)
                if overwrite_existing:
                    print(key + ' overwritten')
                    self._data_sets[key] = new_set

                else:
                    key = self.increment_name(key)
                    print(key + ' created')
                    new_data_sets[key] = new_set

        self._data_sets.update(new_data_sets)

        if data_sets_changed:
            self.data_sets_changed(changed_data_sets)

    def add_data_set(self, data_set: DataSet, replace_existing=False, suspend_notification=False):

        if not replace_existing:
            if data_set.name in self._data_sets:
                while data_set.name in self._data_sets:
                    data_set.name = self.increment_name(data_set.name)

        self._data_sets[data_set.name] = data_set

        if not suspend_notification:
            self.data_sets_changed([data_set])

    def notify_listeners(self, data_sets_that_changed):

        # If no specific data_sets changed, just assume they all changed
        data_sets_that_changed = data_sets_that_changed or self._data_sets
        self.check_patterns(data_sets_that_changed)

    def set_listener_signal_patterns(self, signal_patterns, listener):
        if signal_patterns is None:
            self._listeners.pop(listener)

        else:
            self._listeners[listener] = signal_patterns

    def check_patterns(self, data_sets):
        for listener, signal_patterns in self._listeners.items():
            listener.patterns_matched(self.get_matching_signals(signal_patterns, data_sets))

    def get_matching_signals(self, signal_patterns, data_sets=None):
        matches = {}
        for pattern in signal_patterns:
            matching_signals = self.pattern_match(pattern, data_sets)
            matches[pattern] = matching_signals

        return matches

    def pattern_match(self, listen_for, data_sets):
        if data_sets is None:
            data_sets = self._data_sets

        if listen_for in data_sets:
            return [data_sets[listen_for]]

        else:
            matches = []

            # TODO Parse the listen string
            # for data_set in data_sets,
            #   if listener_signal_applies(data_set.signal_path, listen_for),
            #       return data_set

            return matches

    def signal_from_path(self, signal_path):
        data = self.data_sets
        if not data:
            return None

        path_tokens = signal_path.split('/')
        for token in path_tokens:
            if isinstance(data, DataSet):
                data = data.signal_dict

            if isinstance(data, dict):
                data = data.get(token)

        return data

    @staticmethod
    def listener_signal_applies(signal_path, listener_pattern):

        # TODO Add terms like "*/sig1 & */sig2" or "sig1 | sig2" to greedy or optionally select
        if signal_path == listener_pattern:
            return True
        else:
            if listener_pattern.endswith('*'):
                listener_pattern = listener_pattern[:-1]
                if signal_path.startswith(listener_pattern):
                    return True

            elif listener_pattern.startswith('*'):
                listener_pattern = listener_pattern[1:]
                if signal_path.endswith(listener_pattern):
                    return True

        return False

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