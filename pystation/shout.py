from threading import Thread, Event

import shouty


class Shouter(Thread):

    def __init__(self, user_params, playlist, track=''):
        super(Shouter, self).__init__()

        self.params = {
            'host': user_params.get('ICECAST', 'Host'),
            'port': user_params.getint('ICECAST', 'Port'),
            'user': user_params.get('ICECAST', 'Username'),
            'password': user_params.get('ICECAST', 'Password'),
            'format': shouty.Format.MP3,
            'mount': user_params.get('ICECAST', 'Mount'),
            'name': user_params.get('ICECAST', 'Name'),
            'description': user_params['ICECAST']['Description'],
            'genre': user_params.get('ICECAST', 'Genre'),
            'audio_info': {
                'channels': '2',
                'samplerate': '44100',
            }
        }

        self.chunk_size = user_params.getint('ICECAST', 'Chunk Size')

        self.playlist = playlist

        self.track = track

        # Probably won't need these thanks to queue
        # Pause can be kept just for a check
        # self.skip = Event()
        # self.paused = Event()
        self.killed = Event()
        self.killed.clear()

        self.idle = open(f'{user_params["GENERAL"]["Idle"]}', 'rb')
        # check if idle is correct format

    def send_chunk(self, connection):
        current_queue = self.playlist.current_chunk_queue()

        if not current_queue or self.playlist.get_paused():
            # nothing in queue or idling
            chunk = self.idle.read(self.chunk_size)
            if not chunk:
                self.idle.seek(0)
                chunk = self.idle.read(self.chunk_size)

        else:
            # current track playing
            chunk = current_queue.get()

        # print(chunk[:10])

        connection.send(chunk)
        connection.sync()

        # connection.set_metadata_song(self.track)
        # connection.free()

    def run(self):
        print('running...')

        with shouty.connect(**self.params) as connection:
            print('connected')
            while not self.killed.is_set():
                self.send_chunk(connection)

        print('disconnected')

    # def pause(self):
    #     self.paused.set()
    #
    # def unpause(self):
    #     self.paused.clear()

    def kill(self):
        self.killed.set()

    def join(self, timeout=0):
        self.killed.set()
        super(Shouter, self).join(timeout)
