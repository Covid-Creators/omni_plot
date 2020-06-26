import re
import hashlib

from data_flow.signals import SignalGenerator, Signal


class DataSet:

    def __init__(self, import_method_type, path_data, path_format=None, name=''):

        self._name = name
        # TODO file_type can probably moved to an entirely static class ("struct")
        self._import_method = import_method_type()
        self._path_data = path_data
        self._path_format = path_format
        self._time_key = None
        self._md5 = self.md5_for_file(path_data)
        self._signal_dict = {}  # Dict of signals navigable by [group _name][_signal _name]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.change_data_set_name(self._signal_dict, value)

    @staticmethod
    def change_data_set_name(signal_dict, name):
        for _, signal in signal_dict.items():

            if isinstance(signal, dict):
                DataSet.change_data_set_name(signal, name)

            else:
                assert isinstance(signal, Signal)
                signal.change_data_set_name(name)

    @property
    def signal_dict(self):
        return self._signal_dict

    def add_signal(self, name, value_array, units=None, time_array=None, time_units=None, relative_path=None):

        relative_path = '/'.join([relative_path, name]) if relative_path else name

        signal_path = self._name + '/' + relative_path

        if units is None or units == '':
            name, units = DataSet.split_units_from_string(name)

        signal = SignalGenerator.generate_signal(
            time_array=time_array,
            time_units=time_units,
            value_array=value_array,
            value_units=units,
            signal_path=signal_path,
        )

        # Construct a dictionary tree of the form {token0: {token1: {token2: signal} } }
        # Remove the name from the end of the token list
        tokens = relative_path.split('/')
        tokens = tokens[:-1]

        signal_dict = self._signal_dict
        for token in tokens:
            if token not in signal_dict:
                signal_dict[token] = {}

            signal_dict = signal_dict[token]

        signal_dict[name] = signal

    def generate_json_dict(self):

        return {
            'import_method_type': self._import_method.key,
            'path_data': self._path_data,
            'path_format': self._path_format,
            'time_key': self._time_key,
        }

    def refresh(self):

        if self._md5 == self.md5_for_file(self._path_data):
            print(self._name + ' has not changed')
            return self

        print(self._name + ' has changed. Refreshing...')

        if self._time_key:
            new_data_set = self._import_method.load(self._path_data, self._time_key)

        else:
            new_data_set = self._import_method.load(self._path_data)

        return new_data_set

    @staticmethod
    def split_units_from_string(string):

        units = re.match(r'.*\S(\s*)(\[.*])', string)
        if units:
            # TODO This has not been tested
            indices_space = units.regs[1]
            indices_units = units.regs[2]
            name = string[:indices_space[0]]
            units = string[indices_units[0] + 1:indices_units[1] - 1]

        else:
            name = string
            units = ''

        return name, units

    @staticmethod
    def md5_for_file(filename, block_size=2 ** 20):
        md5 = hashlib.md5()
        f = open(filename, 'r')
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data.encode('utf8'))
        return md5.digest()
