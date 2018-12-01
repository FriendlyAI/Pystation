from queue import Queue
import player
import shout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDesktopWidget, QPushButton, QTabWidget, QVBoxLayout, \
    QLabel, QScrollArea, QProgressBar, QInputDialog, QErrorMessage, QLineEdit
import sys

MUSIC_Q = Queue()


class Setup:
    pass


class Player:
    pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # open setup window

    sys.exit(app.exec_())
