from shout import Shout
from threading import Thread
from time import sleep


class Shouter(Thread):

    def __init__(self, user_params, playlist, chunk_size):
        super(Shouter, self).__init__(daemon=True)

        self.params = {
            'host': user_params.get('ICECAST', 'host'),
            'port': user_params.getint('ICECAST', 'port'),
            'user': user_params.get('ICECAST', 'username'),
            'password': user_params.get('ICECAST', 'password'),
            'mount': user_params.get('ICECAST', 'mount'),
            'name': user_params.get('ICECAST', 'name'),
            'description': user_params.get('ICECAST', 'description'),
            'genre': user_params.get('ICECAST', 'genre'),
            'audio_info': {
                'channels': '2',
                'samplerate': '44100'
            }
        }
        self.connection = Shout()
        self.init_connection()

        self.chunk_size = chunk_size

        self.connected = False

        self.playlist = playlist

        self.idle = open(user_params.get('GENERAL', 'idle'), 'rb')

        self.trackname = ''

    def init_connection(self):
        host = self.params.get('host')
        mount = self.params.get('mount')

        self.connection.host = host
        self.connection.port = self.params.get('port')
        self.connection.user = self.params.get('username')
        self.connection.password = self.params.get('password')
        self.connection.mount = mount
        self.connection.format = 'mp3'
        self.connection.protocol = 'http'
        self.connection.name = self.params.get('name')
        self.connection.description = self.params.get('description')
        self.connection.genre = self.params.get('genre')
        self.connection.url = f'{host}{mount}'  # TODO set url using config window
        self.connection.public = 0
        self.connection.audio_info = self.params.get('audio_info')

    def connect(self):
        try:
            self.connection.open()
            self.connected = True
            self.update_metadata('IDLE')
            while True:
                self.send_chunk()
        except Exception as e:
            print(f'SHOUTERR: {e}\nreconnecting...')

        self.connection.close()
        self.connected = False

    def send_chunk(self):
        current_queue = self.playlist.current_chunk_queue()

        if self.playlist.is_recording():
            if current_queue.empty():
                chunk = self.get_idle_chunk()
            else:
                chunk = current_queue.get()

        else:
            if not current_queue or self.playlist.get_paused():  # nothing in queue or idling
                chunk = self.get_idle_chunk()

            else:  # current track playing
                chunk = current_queue.get()
                self.playlist.increment_progress()

        self.connection.send(chunk)
        self.connection.sync()

    def update_metadata(self, trackname):
        self.connection.set_metadata({'song': trackname})

    def get_idle_chunk(self):
        chunk = self.idle.read(self.chunk_size)
        if not chunk:
            self.idle.seek(0)
            chunk = self.idle.read(self.chunk_size)
        return chunk

    def get_connected(self):
        return self.connected

    def run(self):
        while True:
            if not self.connected:
                self.connect()
                sleep(3)  # wait for 3 seconds before trying to connect again
