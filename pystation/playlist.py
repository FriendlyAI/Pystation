from thread_decorator import thread
from track import Track


class Playlist:
    def __init__(self, chunk_size):
        self.tracklist = []  # list of upcoming Track objects
        self.loading_tracklist = []  # list of urls still being loaded

        self.current_track = None  # Track object
        self.next_track = None  # Track object
        self.live_track = None
        self.progress = 0  # number of read chunks this track

        self.chunk_size = chunk_size
        self.paused = False
        self.trackname_updated = True  # true tells GUI that trackname needs updating
        self.playlist_updated = False  # true tells GUI that tracklist needs updating

        self.recording_speaker = False
        self.recording_microphone = False

    def get_tracks(self):
        return self.tracklist

    def add_track(self, filename):
        track = Track(self.chunk_size, filename=filename)
        self.tracklist.append(track)
        print(f'tracklist: {self.tracklist}\nadded {filename}')
        self.enqueue()
        self.playlist_updated = True

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
            self.playlist_updated = True
        finally:
            self.loading_tracklist.remove(url)

    def remove_track(self, index):
        if len(self.tracklist) > 0:
            self.playlist_updated = True
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
        self.playlist_updated = True

    def move_tracks_down(self, track_indices):
        for index in track_indices:
            self.tracklist.insert(index + 1, self.tracklist.pop(index))

        self.load_next_track(False)
        self.playlist_updated = True

    def get_next_track(self):
        if len(self.tracklist) > 0:
            return self.tracklist[0]
        return None

    def current_chunk_queue(self):
        if self.is_recording():
            return self.live_track.get_chunk_queue()

        if not self.is_recording() and (not self.current_track or self.current_track.get_chunk_queue().empty()):
            # track ended, enqueue next
            if not self.enqueue():  # current track not ready/idling
                return None

        return self.current_track.get_chunk_queue()

    def skip_track(self):
        if not self.is_recording():
            self.current_track = None

            self.enqueue()

    def enqueue(self):
        """
        called when current_track finished or new track added
        returns True if new current_track ready to play
        """
        if self.is_recording():
            return True

        if not self.current_track or self.current_track.get_chunk_queue().empty():
            self.reset_progress()
            if self.next_track:
                self.current_track = self.next_track
                self.remove_track(0)
                self.trackname_updated = True
                return True
            else:
                if len(self.tracklist) > 0:
                    self.load_next_track(True)
                    self.trackname_updated = True
                elif self.current_track:
                    self.current_track = None
                    self.trackname_updated = True
                return False

        elif not self.next_track and len(self.tracklist) > 0:
            self.load_next_track(False)
            return True

    @thread
    def load_next_track(self, now_playing):
        if self.is_recording():
            return

        elif now_playing:  # loaded track is playing now, remove from track queue
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

    def set_live_track(self, track):
        self.live_track = track

    def is_recording_speaker(self):
        return self.recording_speaker

    def toggle_recording_speaker(self):
        self.recording_speaker = not self.recording_speaker
        self.trackname_updated = True

    def is_recording_microphone(self):
        return self.recording_microphone

    def toggle_recording_microphone(self):
        self.recording_microphone = not self.recording_microphone
        self.trackname_updated = True

    def is_recording(self):
        return self.recording_speaker or self.recording_microphone

    def get_current_track(self):
        if self.is_recording():
            return self.live_track
        else:
            return self.current_track

    def set_paused(self, value):
        self.paused = value

    def get_paused(self):
        return self.paused

    def reset_progress(self):
        self.progress = 0

    def increment_progress(self):
        self.progress += 1

    def update_trackname(self):
        self.trackname_updated = False

    def get_trackname_updated(self):
        return self.trackname_updated

    def update_playlist(self):
        self.playlist_updated = False

    def get_playlist_updated(self):
        return self.playlist_updated
