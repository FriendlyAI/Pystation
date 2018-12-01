from queue import Queue


class Playlist:
    def __init__(self):
        self.tracklist = []
        self.chunklist = []

    def get_tracks(self):
        return self.tracklist

    def get_chunks(self):
        try:
            return self.chunklist.pop(0)
        except IndexError:
            return None

    def add_chunks(self):
        new_queue = Queue()
        self.chunklist.append(new_queue)
        return new_queue

    def next_chunks(self):
        self.chunklist.pop(0)
        return self.get_chunks()
