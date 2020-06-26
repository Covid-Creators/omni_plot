import time
import traceback
import sys

from PyQt5 import QtCore


class WorkerSignals(QtCore.QObject):
    """
    Example class copied from
    https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/

    finished
        No _data_store

    error
        tuple containing error information

    result
        return from func

    """
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    time_passed = QtCore.pyqtSignal(float)


class Worker(QtCore.QRunnable):

    def __init__(self, func=None, *args, **kwargs):
        super(Worker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):

        try:
            result = self._call_func()

        except Exception as e:
            traceback.print_exc()
            exception_type, value = sys.exc_info()[:2]
            self.signals.error.emit((exception_type, value, traceback.format_exc()))
            raise e

        else:
            self.signals.result.emit(result)

        finally:
            self.signals.finished.emit()

    def _call_func(self):

        return self.func(*self.args, **self.kwargs)


class LoopingWorker(Worker):

    def __init__(self, loop, setup=None, start_automatically=True, *args, **kwargs):
        super(LoopingWorker, self).__init__(func=loop, *args, **kwargs)
        self._setup = setup
        self._active = start_automatically

    def _call_func(self):

        if self._setup:
            self._setup()

        while self._active is False:
            time.sleep(0.1)

        while self._active is True:
            self.func(*self.args, **self.kwargs)

    def kill(self):
        # When called deactivate work method and wait for cleanup.
        self._active = False
        self.signals.finished.emit()


class TimerWorker(LoopingWorker):

    def __init__(self, parent=None, time_step_s=0.1, *args, **kwargs):
        super(TimerWorker, self).__init__(parent, *args, **kwargs)
        self.func = self.increment_time
        self.time_step_s = time_step_s

    def increment_time(self):
        # While thread is asked to be active by parent emit int values 1 every second.
        self.signals.time_passed.emit(self.time_step_s)
        time.sleep(self.time_step_s)
