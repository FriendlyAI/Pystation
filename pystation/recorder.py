import lameenc
from queue import Queue
from threading import Thread, Event
from time import sleep

import soundcard
from numpy import int16, average, amax, amin

from thread_decorator import thread


class Recorder(Thread):

    def __init__(self, speaker_id, microphone_id):
        super(Recorder, self).__init__(daemon=True)

        self.speaker = None
        self.microphone = None

        self.encoder = lameenc.Encoder()
        self.encoder.set_bit_rate(192)
        self.encoder.set_channels(2)
        self.encoder.set_quality(7)

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

        self.init_speaker(speaker_id)
        self.init_microphone(microphone_id)

    def init_speaker(self, speaker_id):
        # TODO check is speaker.channels >= 2, maybe simulate stereo with mono
        self.speaker = soundcard.get_microphone(int(speaker_id), include_loopback=True)

        if self.microphone and self.microphone.id == self.speaker.id:
            self.speaker = None
            print('duplicate microphone and speaker')

    def init_microphone(self, microphone_id):
        self.microphone = soundcard.get_microphone(int(microphone_id), include_loopback=False)

        if self.speaker and self.microphone.id == self.speaker.id:
            self.microphone = None
            print('duplicate microphone and speaker')

    @thread
    def record_speaker_frames(self):
        with self.speaker.recorder(44100, channels=[0, 1]) as speaker_recorder:
            while not self.killed.is_set() and self.recording_speaker:
                numpy_frames = speaker_recorder.record(self.num_frames)
                self.speaker_queue.put(numpy_frames)
        self.speaker_queue = Queue()  # clear queue

    @thread
    def record_microphone_frames(self):
        with self.microphone.recorder(44100, channels=[0, 1]) as microphone_recorder:
            while not self.killed.is_set() and self.recording_microphone:
                numpy_frames = microphone_recorder.record(self.num_frames)
                self.microphone_queue.put(numpy_frames)
        self.microphone_queue = Queue()  # clear queue

    def add_chunk(self):
        if self.recording_speaker and self.recording_microphone:
            microphone_chunk = self.microphone_queue.get()
            speaker_chunk = self.speaker_queue.get()
            int16_frames = (average([microphone_chunk, speaker_chunk], axis=0, weights=[5, 1])
                            * self.int16_max).astype(int16)

        elif self.recording_speaker:
            int16_frames = (self.speaker_queue.get() * self.int16_max).astype(int16)

        else:  # only recording microphone

            int16_frames = (self.microphone_queue.get() * self.int16_max).astype(int16)
        if int16_frames.size != 0:
            volume = max(amax(int16_frames), abs(amin(int16_frames))) / self.int16_min * -1
            self.track.set_volume(volume)

            chunk = bytes(self.encoder.encode(int16_frames))

            self.track.add_chunk(chunk)

    def set_track(self, track):
        self.track = track

    def set_recording_speaker(self, recording_bool):
        self.recording_speaker = recording_bool
        if self.recording_speaker:
            self.record_speaker_frames()

    def set_recording_microphone(self, recording_bool):
        self.recording_microphone = recording_bool
        if self.recording_microphone:
            self.record_microphone_frames()

    def run(self):
        while True:
            if self.recording_speaker or self.recording_microphone:
                self.add_chunk()
            else:
                sleep(1)  # reduce CPU usage

    def join(self, timeout=0):
        self.killed.set()
        super(Recorder, self).join(timeout)
