from queue import Queue
# import player
# import shout
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDesktopWidget, QPushButton, QTabWidget, QVBoxLayout, \
    QLabel, QScrollArea, QProgressBar, QInputDialog, QErrorMessage, QLineEdit, QFileDialog
import sys
from send_source import send_files
import threading

class Setup:
    pass


class Player(QMainWindow):
    def __init__(self, shouter, user_params, file_q, chunk_q):
        super().__init__()

        self.shouter = shouter
        # self.user_params = user_params
        self.file_q = file_q
        self.chunk_q = chunk_q

        # self.chunk_size = int(user_params['ICECAST']['Chunk Size'])
        self.chunk_size = user_params.getint('ICECAST', 'Chunk Size')
        self.perfomance_mode = user_params.getboolean('GENERAL', 'Performance')
        # self.perfomance_mode = int(user_params['GENERAL']['Performance'])

        self.paused = False

        self.width = 600
        self.height = 400
        self.screen = QDesktopWidget().screenGeometry()

        self.upload_button = QPushButton('Upload', self)
        self.pause_button = QPushButton('Pause', self)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Pystation Player')
        self.setFixedSize(self.width, self.height)
        self.move((self.screen.width() - self.width) / 2, (self.screen.height() - self.height) / 2)

        self.upload_button.resize(self.upload_button.sizeHint())
        self.upload_button.move((self.width - self.upload_button.width()) / 2, 10)
        self.upload_button.clicked.connect(self.choose_upload)

        self.pause_button.resize(self.pause_button.sizeHint())
        self.pause_button.move((self.width - self.pause_button.width()) / 2, 30)
        self.pause_button.clicked.connect(self.toggle_pause)

        self.show()

    def choose_upload(self):
        print('upload')
        file_dialog = QFileDialog()
        # file_dialog.setFilter("Audio files (*.mp3)")
        # file_dialog.fileMode(QFileDialog.ExistingFiles)
        filenames, _ = QFileDialog.getOpenFileNames(file_dialog, filter='Audio (*.mp3 *.flac)')
        print(f'files uploaded: {filenames}')
        [self.file_q.put(filename) for filename in filenames]
        send_files(self.perfomance_mode, filenames, self.file_q, self.chunk_q, self.chunk_size)
        
    def toggle_pause(self):
        if self.paused:
            self.shouter.unpause()
            self.pause_button.setText('Pause')
        else:
            self.shouter.pause()
            self.pause_button.setText('Paused')
        self.paused = not self.paused
        print('pause toggled')


def run_player(shouter, user_params, file_q, chunk_q):
    app = QApplication(sys.argv)

    # open setup window

    player = Player(shouter, user_params, file_q, chunk_q)

    sys.exit(app.exec_())
