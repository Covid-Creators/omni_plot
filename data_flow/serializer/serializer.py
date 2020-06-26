import random
import os
from PyQt5 import QtGui
from data_flow.serializer.file_loader import FileLoader
from data_flow.workspaces import Workspace


class Serializer:

    def __init__(self, controller):

        self.controller = controller
        self.workspace = Workspace(controller)
        self.file_loader = FileLoader(controller)

    @staticmethod
    def get_new_image_path():
        return "images/empty_plot_photos/"+random.choice(os.listdir("images/empty_plot_photos"))

    @staticmethod
    def get_plot_btn_path():
        return 'images/logo.svg'

    def get_plot_icon(self):
        file_name = self.get_new_image_path()
        return QtGui.QIcon(file_name)

    def file_format_by_key(self, key):
        return self.file_loader.data_format_dict[key]
