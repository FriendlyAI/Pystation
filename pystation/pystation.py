from queue import Queue
# import player
# import shout
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDesktopWidget, QPushButton, QTabWidget, QVBoxLayout, \
    QLabel, QScrollArea, QProgressBar, QInputDialog, QErrorMessage, QLineEdit
import sys


MUSIC_Q = Queue()


class Setup:
    pass


class Player(QMainWindow):
    def __init__(self):
        super().__init__()
        self.width = 600
        self.height = 400
        self.screen = QDesktopWidget().screenGeometry()

        self.upload_button = QPushButton('Upload', self)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Pystation Player')
        self.setFixedSize(self.width, self.height)
        self.move((self.screen.width() - self.width) / 2, (self.screen.height() - self.height) / 2)

        self.upload_button.resize(self.upload_button.sizeHint())
        self.upload_button.move((self.width - self.upload_button.width()) / 2, 10)
        self.upload_button.clicked.connect(self.upload)

        self.show()

    def upload(self):
        print('clicked')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # open setup window
    player = Player()

    sys.exit(app.exec_())
