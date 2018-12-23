from thread_decorator import thread
from track import Track


class Playlist:
    def __init__(self, chunk_size):
        self.tracklist = []  # list of upcoming Track objects
        self.loading_tracklist = []  # list of urls (TODO filenames?) still being loaded

        self.current_track = None  # Track object
        self.next_track = None  # Track object
        self.progress = 0  # number of read chunks this track

        self.chunk_size = chunk_size
        self.paused = False
        self.updated = True  # false tells GUI that tracklist needs updating

    def get_tracks(self):
        return self.tracklist

    def add_track(self, filename):
        track = Track(self.chunk_size, filename=filename)
        self.tracklist.append(track)
        print(f'tracklist: {self.tracklist}\nadded {filename}')
        self.enqueue()
        self.updated = False

    @thread
    def add_youtube_track(self, url):
        print(f'yt download: {url}')
        self.loading_tracklist.append(url)

        try:
            track = Track(self.chunk_size, url=url)
        except FileNotFoundError:
            pass
        else:
            self.tracklist.append(track)
            self.enqueue()
            self.updated = False
        finally:
            self.loading_tracklist.remove(url)

    def remove_track(self, index):
        if len(self.tracklist) > 0:
            self.updated = False
            track = self.tracklist.pop(index)
            if index == 0:
                self.load_next_track(False)
                return track
            else:
                track.delete_file()

    def remove_tracks(self, track_indices):
        if len(self.tracklist) > 0:
            for track_index in track_indices:
                self.remove_track(track_index)

    def move_tracks_up(self, track_indices):
        for index in track_indices:
            self.tracklist.insert(index - 1, self.tracklist.pop(index))

        self.load_next_track(False)
        self.updated = False

    def move_tracks_down(self, track_indices):
        for index in track_indices:
            self.tracklist.insert(index + 1, self.tracklist.pop(index))

        self.load_next_track(False)
        self.updated = False

    def get_next_track(self):
        if len(self.tracklist) > 0:
            return self.tracklist[0]
        return None

    def current_chunk_queue(self):
        if not self.current_track or self.current_track.get_chunk_queue().empty():  # track ended, enqueue next
            if not self.enqueue():  # current track not ready/idling
                return None

        return self.current_track.get_chunk_queue()

    def skip_track(self):
        self.current_track = None

        self.enqueue()

    def enqueue(self):
        """
        called when current_track finished or new track added
        returns True if new current_track ready to play
        """

        if not self.current_track or self.current_track.get_chunk_queue().empty():
            self.reset_progress()
            if self.next_track:
                self.current_track = self.next_track
                self.remove_track(0)
                return True
            else:
                if len(self.tracklist) > 0:
                    self.load_next_track(True)
                else:
                    self.current_track = None
                return False

        elif not self.next_track and len(self.tracklist) > 0:
            self.load_next_track(False)
            return True

    @thread
    def load_next_track(self, now_playing):
        if now_playing:  # loaded track is playing now, remove from track queue
            self.current_track = self.remove_track(0)
            track_slot = self.current_track
            self.reset_progress()
        else:  # preloading next track, keep in queue
            if len(self.tracklist) < 1:
                self.next_track = None
                return
            self.next_track = self.get_next_track()
            track_slot = self.next_track

        if not track_slot.get_read():  # Track has not been loaded before
            print('queueing', track_slot)
            track_slot.read_file()

    def get_current_track(self):
        return self.current_track

    def set_paused(self, value):
        self.paused = value

    def get_paused(self):
        return self.paused

    def reset_progress(self):
        self.progress = 0

    def increment_progress(self):
        self.progress += 1

    def update(self):
        self.updated = True

    def get_updated(self):
        return self.updated
