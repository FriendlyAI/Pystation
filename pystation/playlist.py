import os
from queue import Queue

from thread_decorator import thread
from track import Track


class Playlist:
    def __init__(self, chunk_size):
        print('init playlist')
        self.tracklist = []  # list of Track objects
        self.current_track = Queue()
        self.next_track = Queue()
        # self.chunklist = []  # list of byte Queue objects
        self.chunk_size = chunk_size
        self.paused = False

    def get_tracks(self):
        return self.tracklist

    # def current_track(self):
    #     return

    # def get_chunklist(self):
    #     return self.chunklist

    # @thread
    def add_track(self, filename=None, url=None):
        print('add', filename, url)
        if filename:
            self.tracklist.append(Track(filename=filename))
        elif url:
            self.tracklist.append(Track(url=url))

        print(self.tracklist)

        self.enqueue()

    def remove_track(self):
        return self.tracklist.pop(0)

    def current_chunk_queue(self):
        if self.current_track.empty():  # track ended, remove empty Queue
            self.enqueue()

        return None if self.current_track.empty() else self.current_track

    # def add_chunk_queue(self):
    #     new_queue = Queue()
    #     self.chunklist.append(new_queue)
    #     return new_queue

    def skip_track(self):
        if self.tracklist: print(self.tracklist)
        self.current_track = self.next_track
        self.next_track = Queue()

        self.enqueue()

    def enqueue(self):
        # load next track if less than two tracks cached and tracks in queue
        if self.current_track.empty():
            if self.next_track.empty():
                if len(self.tracklist) > 0:
                    self.load_next_track(self.current_track)
            else:
                self.current_track = self.next_track
                self.next_track = Queue()
        elif self.next_track.empty() and len(self.tracklist) > 0:
                self.load_next_track(self.next_track)

    @thread
    def load_next_track(self, track_slot):
        track = self.remove_track()
        chunk = track.read_chunk(self.chunk_size)

        while chunk:
            track_slot.put(chunk)
            chunk = track.read_chunk(self.chunk_size)
        print(f'loaded {track.get_trackname()}/{track.get_filename()} and deleted')

        os.remove(track.get_filename())

    def set_paused(self, value):
        self.paused = value

    def get_paused(self):
        return self.paused
