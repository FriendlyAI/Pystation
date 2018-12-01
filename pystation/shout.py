from threading import Thread, Event

import shouty


class Shouter(Thread):

    def __init__(self, user_params, music_q):
        super(Shouter, self).__init__()

        self.params = {
            'host': user_params['ICECAST']['Host'],
            'port': int(user_params['ICECAST']['Port']),
            'user': user_params['ICECAST']['Username'],
            'password': user_params['ICECAST']['Password'],
            'format': shouty.Format.MP3,
            'mount': user_params['ICECAST']['Mount'],
            'name': user_params['ICECAST']['Name'],
            'description': user_params['ICECAST']['Description'],
            'genre': user_params['ICECAST']['Genre'],
            'audio_info': {
                'channels': '2',
                'samplerate': '44100',
            }
        }

        self.chunk_size = int(user_params['ICECAST']['Chunk Size'])

        self.music_q = music_q

        # Probably won't need these thanks to queue
        # Pause can be kept just for a check
        self.skip = Event()
        self.paused = Event()
        self.killed = Event()
        self.killed.clear()

        self.idle = open(f'{user_params["GENERAL"]["Idle"]}', 'rb')
        # check if idle is correct format

    def send_chunk(self, connection):
        if self.music_q.empty() or self.paused.is_set():  # player is paused/idling
            chunk = self.idle.read(self.chunk_size)
            if not chunk:
                self.idle.seek(0)
                chunk = self.idle.read(self.chunk_size)

        else:  # player is running
            chunk = self.music_q.get()

        connection.send(chunk)
        # print(chunk)
        # connection.set_metadata_song(songname)
        connection.sync()
        # connection.free()

    def run(self):
        print('running...')

        with shouty.connect(**self.params) as connection:
            print('connected')
            while not self.killed.is_set():
                self.send_chunk(connection)

        print('disconnected')

    def pause(self):
        self.paused.set()

    def unpause(self):
        self.paused.clear()

    def kill(self):
        self.killed.set()

    def join(self, timeout=0):
        self.killed.set()
        super(Shouter, self).join(timeout)
