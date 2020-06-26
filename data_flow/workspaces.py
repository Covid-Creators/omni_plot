import os
import json

from PyQt5 import QtGui


class Workspace:

    auto_save_name = 'auto_save'

    def __init__(self, controller):

        self.controller = controller

    def save_workspace_as(self, workspace):

        file_path = self.get_file_path()
        if file_path:
            self.controller.settings.loaded_workspace = file_path
            self.save_workspace(workspace, file_path)

    def quick_save_workspace(self, workspace):

        workspace_file = self.controller.settings.loaded_workspace
        if workspace_file:
            self.save_workspace(workspace, workspace_file)

        else:
            raise Exception('Nothing to save to')

    def auto_save_workspace(self, workspace):

        dir_path = os.getcwd() + "/settings"

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        file_path = dir_path + "/" + self.auto_save_name + '.json'

        self.save_workspace(workspace, file_path)

    def save_workspace(self, workspace, file_path):

        # Don't overwrite with bad data - test it first
        try:
            json.dumps(workspace)

        except TypeError as e:
            print(e)
            return

        if workspace:
            try:
                with open(file_path, 'w') as fd:
                    fd.write(json.dumps(workspace, indent=4))
                    fd.close()
                    self.controller.main_window.action_quicksave_workspace.setEnabled(True)

            except Exception as e:
                print(e)
                pass

    def load_workspace_from(self):
        file_path = self.get_file_path(save_not_load=False)
        if file_path:
            self.controller.settings.loaded_workspace = file_path
            return Workspace.load_workspace(file_path)

        else:
            return None

    @staticmethod
    def auto_load_workspace():
        return Workspace.load_workspace(
            os.getcwd() + "/settings/" + Workspace.auto_save_name + '.json')

    @staticmethod
    def load_workspace(file_path):

        try:
            with open(file_path) as fd:
                workspace = json.load(fd)

            return workspace
        except Exception as e:
            print(e)
            return None

    def get_file_path(self, save_not_load=True):

        workspace_file = self.controller.settings.loaded_workspace

        if workspace_file == '':
            workspace_file = os.getcwd()

        if save_not_load:
            file_path = QtGui.QFileDialog.getSaveFileName(
                caption="Save Workspace",
                directory=workspace_file,
                filter="JSON (*.json)")
        else:
            file_path = QtGui.QFileDialog.getOpenFileName(
                caption="Load Workspace",
                directory=workspace_file,
                filter="JSON (*.json)")

        return file_path[0]
