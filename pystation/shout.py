from threading import Thread, Event
from time import sleep

import shouty


class Shouter(Thread):

    def __init__(self, user_params, playlist):
        super(Shouter, self).__init__()

        self.params = {
            'host': user_params.get('ICECAST', 'Host'),
            'port': user_params.getint('ICECAST', 'Port'),
            'user': user_params.get('ICECAST', 'Username'),
            'password': user_params.get('ICECAST', 'Password'),
            'format': shouty.Format.MP3,
            'mount': user_params.get('ICECAST', 'Mount'),
            'name': user_params.get('ICECAST', 'Name'),
            'description': user_params.get('ICECAST', 'Description'),
            'genre': user_params.get('ICECAST', 'Genre'),
            'audio_info': {
                'channels': '2',
                'samplerate': '44100',
            }
        }

        self.chunk_size = user_params.getint('ICECAST', 'ChunkSize')

        self.connected = False

        self.playlist = playlist

        self.killed = Event()
        self.killed.clear()

        self.idle = open(user_params.get('GENERAL', 'IDLE'), 'rb')
        # check if idle is correct format

    def connect(self):
        try:
            with shouty.connect(**self.params) as connection:
                self.connected = True
                while not self.killed.is_set():
                    self.send_chunk(connection)
                # connection.close()
        except Exception as e:
            print(f'{e}\nreconnecting...')
            sleep(5)  # wait for 5 seconds before trying to connect again

        self.connected = False

    def send_chunk(self, connection):
        current_queue = self.playlist.current_chunk_queue()

        if not current_queue or self.playlist.get_paused():  # nothing in queue or idling
            chunk = self.idle.read(self.chunk_size)
            if not chunk:
                self.idle.seek(0)
                chunk = self.idle.read(self.chunk_size)

        else:  # current track playing
            chunk = current_queue.get()
            self.playlist.increment_progress()

        # print(chunk[:10])
        connection.send(chunk)
        connection.sync()
        # connection.free()

    def run(self):
        while not self.killed.is_set():
            if not self.connected:
                self.connect()

    def get_connected(self):
        return self.connected

    def join(self, timeout=0):
        self.killed.set()
        super(Shouter, self).join(timeout)
