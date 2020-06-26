from PyQt5 import QtWidgets, QtGui, QtCore
import time
from itertools import cycle
from widgets.buttons import SquareButton


class TimeSlider(QtWidgets.QSlider):
    # https://gist.github.com/dennis-tra/994a65d6165a328d4eabaadbaedac2cc

    signal_time_changed = QtCore.pyqtSignal(float, float, object)
    signal_time_finished = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(TimeSlider, self).__init__(*args, **kwargs)
        self.decimals = 5
        self._max_int = 10 ** self.decimals
        self.setRange(0, self._max_int)

        self._time_start_s = 0.0
        self._time_end_s = 1.0
        self._time_s = 0.0

        self.valueChanged.connect(lambda event: self.notify_time_changed(time.time()))

    @property
    def time_span_s(self):
        return self._time_end_s - self._time_start_s

    @property
    def time_start_s(self):
        return self._time_start_s

    @time_start_s.setter
    def time_start_s(self, value):
        self._time_start_s = value
        self.slider_time = value

    @property
    def time_end_s(self):
        return self._time_end_s

    @time_end_s.setter
    def time_end_s(self, value):
        self._time_end_s = value
        self.slider_time = self.time_start_s

    def notify_time_changed(self, time_changed):
        self._time_s = self.slider_time
        self.signal_time_changed.emit(self.slider_time, time_changed, self)

    @property
    def slider_time(self):
        return float(super(TimeSlider, self).value()) / self.maximum() * self.time_span_s + self._time_start_s

    @slider_time.setter
    def slider_time(self, time_s):
        if time_s >= self.time_end_s:
            self.signal_time_finished.emit()

        self._time_s = max(self.time_start_s, min(time_s, self.time_end_s))

        self.setValue(int(
            (self._time_s - self._time_start_s) / self.time_span_s * self.maximum()))

        self.signal_time_changed.emit(self._time_s, time.time(), self)

    def set_to_start(self):
        self.slider_time = self.time_start_s

    def move_time_step(self, time_step, forward=True):
        self.slider_time = self._time_s + (time_step if forward else 0.0 - time_step)


class PlaybackWidget(QtWidgets.QWidget):

    signal_back_button = QtCore.pyqtSignal()
    signal_play_pause = QtCore.pyqtSignal()
    signal_forward_button = QtCore.pyqtSignal()
    signal_skip_amount = QtCore.pyqtSignal(float)

    def __init__(self, *args, **kwargs):
        super(PlaybackWidget, self).__init__(*args, **kwargs)

        self._outer_h_box = QtWidgets.QHBoxLayout()
        self._back_button = SquareButton()
        self._play_button = SquareButton()
        self._forward_button = SquareButton()
        self._play_slider = TimeSlider(QtCore.Qt.Horizontal)

        self._skip_amounts = [
            (1.0, QtGui.QIcon("./images/icon-replay-1.svg"), QtGui.QIcon("./images/icon-forward-1.svg")),
            (5.0, QtGui.QIcon("./images/icon-replay-5.svg"), QtGui.QIcon("./images/icon-forward-5.svg")),
            (10.0, QtGui.QIcon("./images/icon-replay-10.svg"), QtGui.QIcon("./images/icon-forward-10.svg")),
            (30.0, QtGui.QIcon("./images/icon-replay-30.svg"), QtGui.QIcon("./images/icon-forward-30.svg"))]
        self._skip_cycle = cycle(self._skip_amounts)

        self.installEventFilter(self)
        self.setup_ui()

    def setup_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)

        # Horizontal track buttons layout - Back-skip, play, pause, forward-skip.
        self.setLayout(self._outer_h_box)
        self._outer_h_box.setContentsMargins(0, 0, 0, 0)

        # Button - Skip-Back.
        self._back_button.setFixedWidth(25)
        self._back_button.clicked.connect(lambda: self.signal_back_button.emit())
        self._back_button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self._outer_h_box.addWidget(self._back_button)

        # Button - Play/Pause.
        self._play_button.setIcon(QtGui.QIcon("./images/icon-play.svg"))
        self._play_button.clicked.connect(lambda: self.signal_play_pause.emit())
        self._play_button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self._outer_h_box.addWidget(self._play_button)

        # Button - Skip-Forward.
        self._forward_button.clicked.connect(lambda: self.signal_forward_button.emit())
        self._forward_button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self._outer_h_box.addWidget(self._forward_button)

        # Slider - Time Sequence
        self._play_slider.setMinimumWidth(300)
        self._play_slider.setRange(0, 100)
        self._play_slider.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        self._outer_h_box.addWidget(self._play_slider)

        self.cycle_time_step()

    def eventFilter(self, q_object, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.RightButton:
                self.cycle_time_step()
                return False

        # TODO Need to set focus to widget or MainWindow to filter arrow keys and space bar
        # This doesn't work because the interactive layouts somehow steal the focus for arrow keys and space bar
        # if obj.type() == QtCore.QEvent.KeyPress:
        #     if obj.name() == QtCore.Qt.Key:
        #         # TODO Arrow keys to skip in time and space bar to play/pause
        #         return False
        return super(PlaybackWidget, self).eventFilter(q_object, event)

    def cycle_time_step(self):

        new_time_step, replay_icon, forward_icon = next(self._skip_cycle)
        self._back_button.setIcon(replay_icon)
        self._forward_button.setIcon(forward_icon)
        self.signal_skip_amount.emit(new_time_step)
