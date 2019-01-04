from threading import Thread
from time import sleep

import shouty


class Shouter(Thread):

    def __init__(self, user_params, playlist):
        super(Shouter, self).__init__(daemon=True)

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

        self.idle = open(user_params.get('GENERAL', 'IDLE'), 'rb')
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
        if self.playlist.recording_speaker or self.playlist.recording_microphone:
            if self.playlist.recording_track.get_chunk_queue().empty():
                chunk = self.get_idle_chunk()
            else:
                chunk = self.playlist.recording_track.get_chunk_queue().get()

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
