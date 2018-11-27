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
            'mount': '/main.mp3',
            'audio_info': {
                'channels': '2'
            }
        }

        self.music_q = music_q

        # Probably won't need these thanks to queue
        # Pause can be kept just for a check
        self.skip = Event()
        self.pause = Event()
        self.stop = Event()

        self.idle = open('config/idle.mp3', 'rb')

    def send_chunk(self, connection):
        chunk = self.music_q.get()
        if chunk:  # probably can remove; music_q already checked non-empty
            connection.send(chunk)
            connection.sync()

    def run(self):
        print('running...')
        with shouty.connect(**self.params) as connection:
            print('connected')
            while True:
                if not self.music_q.empty():  # player is running
                    self.send_chunk(connection)
                else:  # player is paused
                    idle_chunk = self.idle.read(4096)
                    if not idle_chunk:
                        self.idle.seek(0)
                        idle_chunk = self.idle.read(4096)
                    connection.send(idle_chunk)
                    connection.sync()

    def join(self, timeout=0):
        self.stop.set()
        super(Shouter, self).join(timeout)
