from threading import Thread, Event
import shouty


class Shouter(Thread):

    def __init__(self, music_q):
        self.params = {
            'host': '172.16.186.128',
            'port': 8000,
            'user': 'admin',
            'password': 'hackme',
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

    def send_chunk(self, connection):
        chunk = self.music_q.get()
        if chunk:
            connection.send(chunk)
            connection.sync()

    def run(self):
        print('run')
        with shouty.connect(**self.params) as connection:
            print('connected')
            while True:
                self.send_chunk(connection)

    def join(self, timeout=0):
        self.stop.set()
        super(Shouter, self).join(timeout)
