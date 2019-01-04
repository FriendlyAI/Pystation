import lameenc
from queue import Queue
from threading import Thread, Event

import soundcard
from numpy import int16
import time

from thread_decorator import thread


class Recorder(Thread):

    def __init__(self):
        super(Recorder, self).__init__(daemon=True)

        self.speaker = None
        self.microphone = None

        self.encoder = lameenc.Encoder()
        self.encoder.set_bit_rate(192)
        self.encoder.set_channels(2)
        self.encoder.set_quality(2)

        self.int16_max = 32767
        self.int16_min = -32768
        self.num_frames = 10000

        self.recording_speaker = False
        self.recording_microphone = False

        self.speaker_queue = Queue()
        self.microphone_queue = Queue()
        self.track = None

        self.killed = Event()
        self.killed.clear()

        self.init_speaker('0')  # TODO remove

        print(soundcard.all_microphones(include_loopback=True))

    def init_speaker(self, index):
        # TODO index should already be string
        self.speaker = soundcard.get_microphone(f'{index}', include_loopback=True)
        if self.microphone and str(self.microphone) == str(self.speaker):
            self.speaker = None
            print('duplicate microphone and speaker')

    def init_microphone(self, index):
        # TODO index should already be string
        self.microphone = soundcard.get_microphone(f'{index}', include_loopback=False)
        if self.speaker and str(self.microphone) == str(self.speaker):
            self.microphone = None
            print('duplicate microphone and speaker')

    @thread
    def record_speaker_frames(self):
        with self.speaker.recorder(44100, channels=[0, 2]) as r:
            while not self.killed.is_set() and self.recording_speaker:
                numpy_frames = r.record(self.num_frames)
                int16_frames = (numpy_frames * self.int16_max).astype(int16).clip(self.int16_min, self.int16_max)
                self.speaker_queue.put(int16_frames)

    @thread
    def record_microphone_frames(self):
        pass

    def add_chunk(self):
        if self.recording_speaker and self.recording_microphone:
            chunk = None
            pass
        elif self.recording_speaker:
            chunk = bytes(self.encoder.encode(self.speaker_queue.get()))
        else:  # only recording microphone
            chunk = bytes(self.encoder.encode(self.microphone_queue.get()))

        self.track.add_chunk(chunk)

    def set_track(self, track):
        self.track = track

    def set_recording_speaker(self, recording_bool):
        self.recording_speaker = recording_bool
        if self.recording_speaker:
            self.record_speaker_frames()

    def set_recording_microphone(self, recording_bool):
        self.recording_microphone = recording_bool
        if self.recording_speaker:
            self.record_speaker_frames()

    def run(self):
        while not self.killed.is_set():
            if self.recording_speaker or self.recording_microphone:
                self.add_chunk()
            else:
                time.sleep(1)  # reduce CPU usage

    def join(self, timeout=0):
        self.killed.set()
        super(Recorder, self).join(timeout)
