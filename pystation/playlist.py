import os
from queue import Queue
from time import time

from thread_decorator import thread
from track import Track


class Playlist:
    def __init__(self, chunk_size):
        print('init playlist')
        self.tracklist = []  # list of Track objects
        self.now_playing = None
        self.start_time = time()

        self.current_track = Queue()  # queue of chunks
        self.next_track = Queue()  # queue of chunks

        self.chunk_size = chunk_size
        self.paused = False

    def get_tracks(self):
        return self.tracklist

    # @thread
    def add_track(self, filename):
        self.tracklist.append(Track(filename=filename))

        print(self.tracklist, 'added', filename)

        self.enqueue()

    @thread
    def add_youtube_track(self, url):
        self.tracklist.append(Track(url=url))

        print(self.tracklist, 'added', url)

        self.enqueue()

    def remove_track(self):
        return self.tracklist.pop(0)

    def get_track(self):
        return self.tracklist[0]

    def current_chunk_queue(self):
        if self.current_track.empty():  # track ended, enqueue next
            self.enqueue()

        return None if self.current_track.empty() else self.current_track

    def skip_track(self):
        if self.tracklist:
            print(self.tracklist)

        self.current_track = self.next_track
        self.next_track = Queue()

        if len(self.tracklist) > 0:
            self.set_now_playing(self.remove_track())

        self.enqueue()

    def enqueue(self):
        # called when current track finished
        # load next track if less than two tracks cached and tracks in queue
        if self.current_track.empty():
            if self.next_track.empty():
                if len(self.tracklist) > 0:
                    self.load_next_track(self.current_track, True)
                else:
                    self.set_now_playing(None)
            else:
                self.current_track = self.next_track
                self.next_track = Queue()
        elif self.next_track.empty() and len(self.tracklist) > 0:
                self.load_next_track(self.next_track, False)

    @thread
    def load_next_track(self, track_slot, now_playing):
        if now_playing:  # loaded track is playing now, remove from track queue
            track = self.remove_track()
            self.set_now_playing(track)
        else:  # preloading next track, keep in queue
            track = self.get_track()

        print('Queueing', track)

        chunk = track.read_chunk(self.chunk_size)

        while chunk:
            track_slot.put(chunk)
            chunk = track.read_chunk(self.chunk_size)

        try:
            os.remove(track.get_filename())
            print(f'loaded {track.get_trackname()}/{track.get_filename()} and deleted')
        except FileNotFoundError:  # file already removed when preloaded as next track
            print('couldnt delete', track.get_filename())
            pass

    def set_paused(self, value):
        self.paused = value

    def get_paused(self):
        return self.paused

    def set_now_playing(self, track):
        self.start_time = time()
        self.now_playing = track

    def get_now_playing(self):
        return self.now_playing

    def get_start_time(self):
        return self.start_time
