import time
import copy
from itertools import cycle
import numpy as np

from data_flow.signals import Signal
from plugins.abstract_content_widget import AbstractContentWidget
from settings.colors import colors_matlab_ints


class AbstractAnimation(AbstractContentWidget):

    _colors_static = copy.deepcopy(colors_matlab_ints)

    def __init__(self, *args, **kwargs):
        super(AbstractAnimation, self).__init__(*args, **kwargs)

        self._color_cycle = None

        self._animated_signals = {}  # {path (str): signal (Signal)}

        self._time_array = np.array([])
        self._time_units = 's'

        self._preview_animating = False
        self._animation_time_start = None
        self._animation_time_now = None
        self._requested_signal_patterns: list = self._json_dict.get('requested_signal_patterns', [])

        self.set_signal_patterns(self._requested_signal_patterns)

        # TODO Might want to replace this with something more native (Look into QAnimation API?)
        self._controller.playback_manager.signal_time_passed.connect(self.time_passed)

        self.reset_color_cycle()

    @property
    def max_signal_count(self):
        return len(AbstractAnimation._colors_static)

    @property
    def contains_signals(self):
        return len(self._animated_signals) > 0

    @property
    def animated_signals(self):
        return self._animated_signals

    @property
    def content_str(self):
        return ','.join([path for path, _ in self._animated_signals.items()])

    @property
    def time_start(self):
        # TODO look through all signals and parse through all start times
        return min(self._time_array) if len(self._time_array) else 0.0

    @property
    def time_end(self):
        # TODO look through all signals and parse through all end times
        return max(self._time_array) if len(self._time_array) else 1.0

    @property
    def time_bounds(self):
        return self.time_start, self.time_end

    @property
    def time_span(self):
        return self.time_end - self.time_start

    def set_time_s(self, *args, **kwargs):
        # TODO Might want to replace this with something more native (Look into QAnimation API?)
        raise NotImplementedError

    def animate_preview(self):
        # TODO Might want to replace this with something more native (Look into QAnimation API?)
        raise NotImplementedError

    def reset_color_cycle(self):
        self._color_cycle = cycle(self._colors_static)

    def get_color(self):
        return next(self._color_cycle)

    def generate_json_dict(self):
        return {self.json_key: {
            'title': self.title,
            'requested_signal_patterns': self._requested_signal_patterns
        }}

    def start_preview_animation(self):
        # TODO Might want to replace this with something more native (Look into QAnimation API?)
        self._animation_time_start = time.time()
        self._animation_time_now = 0.0
        self._preview_animating = True

    def stop_preview_animation(self):
        # TODO Might want to replace this with something more native (Look into QAnimation API?)
        self._preview_animating = False

    def time_passed(self, time_step_s):
        # TODO Might want to replace this with something more native (Look into QAnimation API?)
        # TODO just get current time - animation_start_time (Otherwise lagging signals can cause slower content)
        if self._preview_animating:
            self._animation_time_now = self._animation_time_now + time_step_s
            self.animate_preview()

    def patterns_matched(self, matching_signals):
        for pattern, signals_matched in matching_signals.items():
            for signal in signals_matched:
                self.add_signal(signal)

    def set_signal_patterns(self, signal_patterns):

        # Get matching signals frm data store and request updates whenever the specified patterns are matched
        loaded_signals = self._controller.data_store.get_matching_signals(signal_patterns)

        # Find out which signals to remove
        signals_to_remove = []
        for path, signal in self._animated_signals.items():
            if path not in loaded_signals:
                signals_to_remove.append(signal)

        # Remove those signals
        for signal in signals_to_remove:
            self.remove_signal(signal, update_data_store=False)

        # Update the rest
        for path, signal in loaded_signals.items():
            if path in self._animated_signals:
                self.update_signal(signal, update_data_store=False)

            else:
                self.add_signal(signal, update_data_store=False)

        self._controller.data_store.set_listener_signal_patterns(self._requested_signal_patterns, self)

    def add_signals(self, signals):
        for signal in signals:
            self.add_signal(signal)

    def add_signal(self, signal: Signal, update_data_store=True):
        # Update the the graphics
        self._animated_signals[signal.path] = signal
        self._requested_signal_patterns.append(signal.path)

        if update_data_store:
            self._controller.data_store.set_listener_signal_patterns(self._requested_signal_patterns, self)

    def update_signal(self, signal: Signal, update_data_store=True):
        # Update the the graphics
        self._animated_signals[signal.path] = signal
        # Assuming match already exists in _requested_signal_patterns

        if update_data_store:
            self._controller.data_store.set_listener_signal_patterns(self._requested_signal_patterns, self)

    def remove_signal(self, signal: Signal, update_data_store=True):
        # Remove it from the graphics
        self.remove_path_from_signal_patterns(signal.path)
        self._animated_signals.pop(signal.path)

        if update_data_store:
            self._controller.data_store.set_listener_signal_patterns(self._requested_signal_patterns, self)

    def remove_path_from_signal_patterns(self, signal_path: str):
        if signal_path in self._requested_signal_patterns:
            self._requested_signal_patterns.remove(signal_path)

        else:

            # TODO Figure out how to remove a match from an abstract pattern
            # TODO (How to exclude foo/bar from foo/* or */bar)

            raise NotImplementedError

