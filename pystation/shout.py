from threading import Thread
from time import sleep

import shouty


class Shouter(Thread):

    def __init__(self, user_params, playlist, chunk_size):
        super(Shouter, self).__init__(daemon=True)

        self.params = {
            'host': user_params.get('ICECAST', 'host'),
            'port': user_params.getint('ICECAST', 'port'),
            'user': user_params.get('ICECAST', 'username'),
            'password': user_params.get('ICECAST', 'password'),
            'format': shouty.Format.MP3,
            'mount': user_params.get('ICECAST', 'mount'),
            'name': user_params.get('ICECAST', 'name'),
            'description': user_params.get('ICECAST', 'description'),
            'genre': user_params.get('ICECAST', 'genre'),
            'audio_info': {
                'channels': '2',
                'samplerate': '44100',
            }
        }

        self.chunk_size = chunk_size

        self.connected = False

        self.playlist = playlist

        self.idle = open(user_params.get('GENERAL', 'idle'), 'rb')
        # check if idle is correct format

    def connect(self):
        try:
            with shouty.connect(**self.params) as connection:
                self.connected = True
                while True:
                    self.send_chunk(connection)
                # connection.close()
        except Exception as e:
            print(f'SHOUTERR: {e}\nreconnecting...')

        self.connected = False

    def send_chunk(self, connection):
        if self.playlist.is_recording():
            if self.playlist.get_current_track().get_chunk_queue().empty():
                chunk = self.get_idle_chunk()
            else:
                chunk = self.playlist.get_current_track().get_chunk_queue().get()

        else:
            current_queue = self.playlist.current_chunk_queue()

            if not current_queue or self.playlist.get_paused():  # nothing in queue or idling
                chunk = self.get_idle_chunk()

            else:  # current track playing
                chunk = current_queue.get()
                self.playlist.increment_progress()

        connection.send(chunk)
        connection.sync()

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
