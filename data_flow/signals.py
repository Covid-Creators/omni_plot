import numpy as np
import scipy.stats as st
from scipy import interpolate
__all__ = ['SignalGenerator', 'Signal', 'FloatTimeSeries', 'NonNumericTimeSeries',
           'AbstractInterpolatedSignal']


class Signal:

    si_prefixes = {
        -24: 'y',
        -21: 'z',
        -18: 'a',
        -15: 'f',
        -12: 'p',
        -9: 'n',
        -6: 'u',
        -3: 'm',
        3: 'k',
        6: 'M',
        9: 'G',
        12: 'T',
        15: 'P',
        18: 'E',
        21: 'Z',
        24: 'Y',
    }

    def __init__(self, value_array, value_units=None, signal_path=''):

        self._value_array = np.array(value_array)
        self._value_units = value_units
        self._path = signal_path
        self._name = signal_path.split('/')[-1]

    @property
    def property_keys(self):
        return self.properties.keys()

    @property
    def properties(self):
        return {
            'Min': self.min,
            'Avg': self.avg,
            'Med': self.med,
            'Mode': self.mode,
            'Max': self.max,
            'Std': self.std,
            'Units': self.units,
        }

    def get_property_strings(self, keys, float_format=None):
        return [self.get_property_string(key, float_format) for key in keys] if keys else []

    def get_property_string(self, key, float_format=None):
        float_format = '{:0.1f}' or float_format
        value = self.properties.get(key)
        if SignalGenerator.is_float(value):
            e_count = 0
            if np.abs(value) > 1000.0:
                while np.abs(value) > 100.0:
                    value /= 1000.0
                    e_count += 3
            elif 0.0 < np.abs(value) < 1.0:
                while np.abs(value) < 1.0:
                    value *= 1000.0
                    e_count -= 3

            if e_count == 0:
                return float_format.format(value)

            else:
                postfix = Signal.si_prefixes.get(e_count, 'e'+str(e_count))
                return float_format.format(value) + postfix

        else:
            return str(value)

    @property
    def min(self):
        return np.min(self._value_array) if len(self._value_array) else None

    @property
    def max(self):
        return np.max(self._value_array) if len(self._value_array) else None

    @property
    def avg(self):
        return np.mean(self._value_array) if len(self._value_array) else None

    @property
    def med(self):
        return np.median(self._value_array) if len(self._value_array) else None

    @property
    def mode(self):
        return st.mode(self._value_array)[0][0] if len(self._value_array) else None

    @property
    def std(self):
        return np.std(self._value_array) if len(self._value_array) else None

    @property
    def samples(self):
        return self._value_array

    @property
    def units(self):
        return self._value_units

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    @property
    def length(self):
        return len(self._value_array)

    def change_data_set_name(self, value):

        path_tokens = self._path.split('/')
        path_tokens[0] = value

        self._path = '/'.join(path_tokens)


class AbstractInterpolatedSignal(Signal):

    def __init__(self, time_array, *args, time_units='s', interp_factor=100.0, **kwargs):
        super(AbstractInterpolatedSignal, self).__init__(*args, **kwargs)

        assert len(time_array) == self.length

        self._time_array = np.array(time_array)
        self._time_units = time_units

        self._interp_factor = interp_factor
        self._interpolation = self.interpolate()

    @property
    def time_array(self):
        return self._time_array

    @property
    def time_unit(self):
        return self.time_unit

    @property
    def t_start(self):
        return min(self._time_array)

    @property
    def t_end(self):
        return max(self._time_array)

    @staticmethod
    def get_index_after_time(time_array: np.array, eval_time: float):
        return np.searchsorted(time_array, eval_time)

    def interpolate(self):
        raise NotImplementedError

    def evaluate_interpolation(self, time: np.array = None, interp_factor: float = None):

        if interp_factor is not None:
            self._interp_factor = interp_factor

        # Ensure that interpolation is only valid for recorded time span
        if time is None:
            time = np.linspace(self.t_start, self.t_end, int(self.length * self._interp_factor))

        else:

            # TODO This is untested

            first_valid_index = self.get_index_after_time(time, self.t_start)
            last_valid_index = self.get_index_after_time(time, self.t_end)
            time = time[first_valid_index:last_valid_index]

        values = self._interpolation(time)

        return time, values


class FloatTimeSeries(AbstractInterpolatedSignal):

    def interpolate(self):

        # Using a one-sided smoothing interpolation to convey time-causality
        return interpolate.PchipInterpolator(self._time_array, self._value_array) if self.length else None


class IntegerTimeSeries(AbstractInterpolatedSignal):

    def __init__(self, *args, **kwargs):
        super(IntegerTimeSeries, self).__init__(*args, **kwargs)

        self._unique_values = []

    def interpolate(self):

        # https://stackoverflow.com/questions/43203215/map-unique-strings-to-integers-in-python

        # Generate lookup table by assigning an index to each unique value
        self._unique_values = [y for x, y in enumerate(sorted(set(self._value_array)))]
        index_dict = {y: x for x, y in enumerate(self._unique_values)}

        # Convert the y_values to indices
        self._value_array = np.array([index_dict[x] for x in self._value_array])

        # return np.vectorize(self.get_value_at_time)
        return self.get_values_at_times

    def get_values_at_times(self, time_array: np.array):
        return [self.get_value_at_time(time) for time in time_array]

    def get_value_at_time(self, eval_time: float):

        # https://stackoverflow.com/questions/16243955/numpy-first-occurrence-of-value-greater-than-existing-value

        # Get index of first
        index = self.get_index_after_time(self._time_array, eval_time)

        if index > 0:
            index -= 1

        return self._value_array[index]


class NonNumericTimeSeries(IntegerTimeSeries):

    def __init__(self, *args, **kwargs):
        super(NonNumericTimeSeries, self).__init__(*args, **kwargs)

    @property
    def min(self):
        return np.nan

    @property
    def max(self):
        return np.nan

    @property
    def avg(self):
        return np.nan

    @property
    def med(self):
        return np.nan

    @property
    def mode(self):
        index = st.mode(self._value_array)[0][0] if len(self._value_array) else None
        return self._unique_values[index] if index is not None and 0 <= index < len(self._unique_values) else None

    @property
    def std(self):
        return np.nan


class SignalGenerator:

    # https://codereview.stackexchange.com/questions/128032/check-if-a-numpy-array-contains-numerical-data
    # Boolean, unsigned integer, signed integer, float, complex.
    _NUMERIC_KINDS = set('buifc')
    _FLOAT_KINDS = set('fc')

    @staticmethod
    def generate_signal(time_array, time_units, value_array, value_units, signal_path):

        if time_array is None:

            # TODO If it's a 2xN array, or if one of the arrays is sorted, auto detect that as a time_array

            return Signal(
                value_array=value_array,
                value_units=value_units,
                signal_path=signal_path)

        else:
            if SignalGenerator.is_numeric(value_array):
                if SignalGenerator.is_float(value_array):
                    return FloatTimeSeries(
                        time_array=time_array,
                        time_units=time_units,
                        value_array=value_array,
                        value_units=value_units,
                        signal_path=signal_path)
                else:
                    return IntegerTimeSeries(
                        time_array=time_array,
                        time_units=time_units,
                        value_array=value_array,
                        value_units=value_units,
                        signal_path=signal_path)
            else:
                return NonNumericTimeSeries(
                    time_array=time_array,
                    time_units=time_units,
                    value_array=value_array,
                    value_units=value_units,
                    signal_path=signal_path)

    @staticmethod
    def is_numeric(array):
        """Determine whether the argument has a numeric datatype, when
        converted to a NumPy array.

        Booleans, unsigned integers, signed integers, floats and complex
        numbers are the kinds of numeric datatype.

        Parameters
        ----------
        array : array-like
            The array to check.

        Returns
        -------
        is_numeric : `bool`
            True if the array has a numeric datatype, False if not.

        """
        return np.asarray(array).dtype.kind in SignalGenerator._NUMERIC_KINDS

    @staticmethod
    def is_float(array):
        """Determine whether the argument has a numeric datatype, when
        converted to a NumPy array.

        Booleans, unsigned integers, signed integers, floats and complex
        numbers are the kinds of numeric datatype.

        Parameters
        ----------
        array : array-like
            The array to check.

        Returns
        -------
        is_numeric : `bool`
            True if the array has a numeric datatype, False if not.

        """
        return np.asarray(array).dtype.kind in SignalGenerator._FLOAT_KINDS
