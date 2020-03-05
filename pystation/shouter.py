from shout import Shout, SHOUT_AI_CHANNELS, SHOUT_AI_SAMPLERATE, ShoutException
from threading import Thread
from thread_decorator import thread
from time import sleep


class Shouter(Thread):

    def __init__(self, user_params, playlist):
        super(Shouter, self).__init__(daemon=True)

        self.connection_params = user_params['ICECAST']
        self.audio_info = {SHOUT_AI_CHANNELS: '2', SHOUT_AI_SAMPLERATE: '44100'}

        self.connection = Shout()
        self.init_connection()

        self.chunk_size = int(self.connection_params['chunksize'])

        self.connected = False

        self.playlist = playlist

        self.idle = open(user_params.get('GENERAL', 'idle'), 'rb')

    def init_connection(self):
        self.connection.host = self.connection_params['host']
        self.connection.port = int(self.connection_params['port'])
        self.connection.user = self.connection_params['username']
        self.connection.password = self.connection_params['password']
        self.connection.mount = self.connection_params['mount']
        self.connection.format = 'mp3'
        self.connection.protocol = 'http'
        self.connection.name = self.connection_params['name']
        self.connection.description = self.connection_params['description']
        self.connection.genre = self.connection_params['genre']
        self.connection.url = self.connection_params['url']
        self.connection.public = 0
        self.connection.audio_info = self.audio_info

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

    @thread
    def update_metadata(self, trackname):
        try:
            self.connection.set_metadata({'song': trackname})
        except ShoutException:
            print('error: couldn\'t update metadata')

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
