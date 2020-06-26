from utilities.worker import TimerWorker
from PyQt5 import QtCore, QtGui, QtWidgets
import time


class PlaybackManager(QtWidgets.QWidget):

    signal_time_passed = QtCore.pyqtSignal(float)
    signal_local_time_is = QtCore.pyqtSignal(float)

    def __init__(self, controller, playback_widget, *args, playback_hz=10.0, **kwargs):
        super(PlaybackManager, self).__init__(*args, **kwargs)

        self.play_status = False  # Play-button status to toggle between play and pause.

        self.controller = controller
        self.playback_widget = playback_widget
        self.playback_widget._play_slider.signal_time_changed.connect(self.set_time_s)
        self.playback_widget._play_slider.signal_time_finished.connect(self.playback_reached_end)
        self.playback_widget.signal_play_pause.connect(self.play_pause_toggle)
        self.playback_widget.signal_forward_button.connect(self.skip_time_forward)
        self.playback_widget.signal_back_button.connect(self.skip_time_backward)
        self.playback_widget.signal_skip_amount.connect(self.new_time_step)

        self.playback_hz = playback_hz
        self.last_time_updated = time.time()
        self.slider_playback_ended = False
        self.slider_time_start_s = None
        self.slider_time_end_s = None
        self.slider_time_skip_s = 1.0

        # Background timer always running for animations and stuff
        self.thread_pool = QtCore.QThreadPool()

        # Declare and connect worker to thread process.
        self.timer_thread = TimerWorker(time_step_s=self.playback_time_step_s)

        # When work signal_time_passed signal propagated call GUI iterate_play method.
        self.timer_thread.signals.time_passed.connect(self.time_passed)
        self.thread_pool.start(self.timer_thread)

    @property
    def playback_time_step_s(self):
        return 1.0 / float(self.playback_hz)

    def new_time_step(self, value):
        self.slider_time_skip_s = float(value)

    def update_time_range(self, time_start_s, time_end_s):
        if not self.slider_time_end_s == time_end_s:
            self.slider_time_end_s = max(self.slider_time_end_s, time_end_s) \
                if self.slider_time_end_s else time_end_s

            self.playback_widget._play_slider.time_end_s = self.slider_time_end_s

        if not self.slider_time_start_s == time_start_s:
            self.slider_time_start_s = min(self.slider_time_start_s, time_start_s) \
                if self.slider_time_start_s else time_start_s

            self.playback_widget._play_slider.time_start_s = self.slider_time_start_s

    def set_time_s(self, time_s, time_changed, source=None):
        # Iterate over tab objects and change their content line location to match the slider's values.

        if time_changed > self.last_time_updated:
            self.last_time_updated = time_changed

            if source is not self.playback_widget._play_slider:
                self.playback_widget._play_slider.slider_time = time_s

            deleted_display_keys = []

            for key, display in self.controller.animations.items():
                if display is not source:
                    try:
                        display.set_time_s(time_s)

                    except RuntimeError:
                        deleted_display_keys.append(key)

            for key in deleted_display_keys:
                self.controller.animations.pop(key)

    def time_passed(self, time_step):
        # When thread process propagated signal_time_passed _signal to GUI this process is called.
        if self.play_status:
            self.playback_widget._play_slider.move_time_step(time_step)

        self.signal_time_passed.emit(time_step)
        self.signal_local_time_is.emit(time.time())

    def play_pause_toggle(self):
        # If paused then begin playing, status to true, change button icon to pause, and start a play thread.
        if self.play_status is False:
            if self.slider_playback_ended:
                self.slider_playback_ended = False
                self.playback_widget._play_slider.set_to_start()

            self.start_playback()

        else:  # Else kill thread to stop play process and change button icon to play.
            self.end_playback()

    def playback_reached_end(self):
        self.slider_playback_ended = True
        self.end_playback()

    def start_playback(self):
        self.play_status = True
        self.playback_widget._play_button.setIcon(QtGui.QIcon("images/icon-pause.svg"))

    def end_playback(self):
        self.play_status = False
        self.playback_widget._play_button.setIcon(QtGui.QIcon("images/icon-play.svg"))

    def skip_time_backward(self):
        # Rewind by fixed amount.
        self.playback_widget._play_slider.move_time_step(0.0 - self.slider_time_skip_s)

    def skip_time_forward(self):
        # Skip forward
        self.playback_widget._play_slider.move_time_step(self.slider_time_skip_s)

    def _kill_time_thread(self):
        # When pause button is hit this is called from play_pause_toggle to kills the play thread process.
        self.timer_thread.kill()
        self.timer_thread = None
        self.thread = None
