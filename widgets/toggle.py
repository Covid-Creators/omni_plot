class Editable:

    def __init__(self, edit_mode=False):
        self._edit_mode = edit_mode

    @property
    def edit_mode(self):
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, toggle: bool):
        self._edit_mode = toggle


class Debuggable:

    def __init__(self, debug_mode=False):
        self._debug_mode = debug_mode

    @property
    def debug_mode(self):
        return self._debug_mode

    @debug_mode.setter
    def debug_mode(self, toggle: bool):
        self._debug_mode = toggle


class EditAndDebug(Editable, Debuggable):

    def __init__(self, edit_mode=False, debug_mode=False):
        Editable.__init__(self, edit_mode=edit_mode)
        Debuggable.__init__(self, debug_mode=debug_mode)
