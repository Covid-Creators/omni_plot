import sys
from PyQt5 import QtWidgets, QtGui
from main_controller import Controller


if __name__ == "__main__":

    # Start the application
    app = QtWidgets.QApplication(sys.argv)

    # # Setup appearance
    with open("settings/style.qss", "r") as fh:
        app.setStyleSheet(fh.read())

    app.setWindowIcon(QtGui.QIcon('images/logo.svg'))

    # Controller creates MainWindow too
    controller = Controller(app)

    while True:
        try:
            sys.exit(app.exec_())
        except RuntimeError as e:
            print(e)
