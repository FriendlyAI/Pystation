import os

from thread_decorator import thread
from track import Track


class Playlist:
    def __init__(self, chunk_size):
        print('init playlist')
        self.tracklist = []  # list of upcoming Track objects
        self.loading_tracklist = []  # list of urls (filenames?) still being loaded
        self.play_time = 0

        self.current_track = None  # Track object
        self.next_track = None  # Track object

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
        self.loading_tracklist.append(url)
        try:
            track = Track(url=url)
        except FileNotFoundError:
            pass
        else:
            self.loading_tracklist.remove(url)
            self.tracklist.append(track)
            print(self.tracklist, 'added', url)
            self.enqueue()
        finally:
            self.loading_tracklist.remove(url)

    def remove_track(self):
        if len(self.tracklist) > 0:
            return self.tracklist.pop(0)

    def get_next_track(self):
        return self.tracklist[0]

    def current_chunk_queue(self):
        if not self.current_track or self.current_track.get_chunk_queue().empty():  # track ended, enqueue next
            self.enqueue()
            return None

        return self.current_track.get_chunk_queue()

    def skip_track(self):
        if self.tracklist:
            print(self.tracklist)

        self.current_track = self.next_track
        self.next_track = None

        self.remove_track()
        self.reset_playtime()

        self.enqueue()

    def enqueue(self):
        # called when current track finished
        # load next track if less than two tracks cached and tracks in queue
        if not self.current_track or self.current_track.get_chunk_queue().empty():
            if not self.next_track:
                if len(self.tracklist) > 0:
                    # self.load_next_track(self.current_track, True)
                    self.load_next_track(True)
                else:
                    self.reset_playtime()
            else:
                self.skip_track()

        elif not self.next_track and len(self.tracklist) > 0:
                # self.load_next_track(self.next_track, False)
                self.load_next_track(False)

    @thread
    def load_next_track(self, now_playing):
        if now_playing:  # loaded track is playing now, remove from track queue
            self.current_track = self.remove_track()
            track_slot = self.current_track
            self.reset_playtime()
        else:  # preloading next track, keep in queue
            self.next_track = self.get_next_track()
            track_slot = self.next_track

        if track_slot.get_chunk_queue().empty():  # Track has not been loaded before
            print('Queueing', track_slot)
            chunk = track_slot.read_chunk(self.chunk_size)

            while chunk:
                track_slot.get_chunk_queue().put(chunk)
                chunk = track_slot.read_chunk(self.chunk_size)

        try:
            os.remove(track_slot.get_filename())
            print(f'loaded {track_slot.get_trackname()}|{track_slot.get_filename()} and deleted')
        except FileNotFoundError:  # file already removed when preloaded as next track
            print('couldnt delete', track_slot.get_filename())
            # should never be called

    def get_current_track(self):
        return self.current_track

    def set_paused(self, value):
        self.paused = value

    def get_paused(self):
        return self.paused

    def reset_playtime(self):
        self.play_time = 0

    def get_play_time(self):
        return self.play_time

    def increment_play_time(self, milliseconds):
        self.play_time += milliseconds / 1000
