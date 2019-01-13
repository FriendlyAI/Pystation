from lameenc import Encoder
from queue import Queue
from threading import Thread, Event
from time import sleep

from numpy import int16, average, amax, amin
from soundcard import get_microphone

from thread_decorator import thread
from track import Track


class Recorder(Thread):

    def __init__(self, speaker_id, microphone_id):
        super(Recorder, self).__init__(daemon=True)

        self.speaker = None
        self.microphone = None

        self.encoder = Encoder()
        self.encoder.set_bit_rate(192)
        self.encoder.set_channels(2)
        self.encoder.set_quality(2)  # highest quality

        self.int16_max = 32767
        self.num_frames = 5000

        self.recording_speaker = False
        self.recording_microphone = False

        self.speaker_queue = Queue()
        self.microphone_queue = Queue()
        self.track = Track(0)

        self.volume = 1.0

        self.amplification = 1.0

        self.killed = Event()
        self.killed.clear()

        self.init_speaker(speaker_id)
        self.init_microphone(microphone_id)

    def init_speaker(self, speaker_id):
        # TODO check is speaker.channels >= 2, maybe simulate stereo with mono
        self.speaker = get_microphone(int(speaker_id), include_loopback=True)

        if self.microphone and self.microphone.id == self.speaker.id:
            self.speaker = None
            print('duplicate microphone and speaker')

    def init_microphone(self, microphone_id):
        self.microphone = get_microphone(int(microphone_id), include_loopback=False)

        if self.speaker and self.microphone.id == self.speaker.id:
            self.microphone = None
            print('duplicate microphone and speaker')

    @thread
    def record_speaker_frames(self):
        with self.speaker.recorder(44100, channels=[0, 1]) as speaker_recorder:
            speaker_recorder.record(1)  # initialize recorder to reduce latency
            self.recording_speaker = True
            while not self.killed.is_set() and self.recording_speaker:
                numpy_frames = speaker_recorder.record(self.num_frames)
                self.speaker_queue.put(numpy_frames)

        self.speaker_queue = Queue()  # clear queue

    @thread
    def record_microphone_frames(self):
        with self.microphone.recorder(44100, channels=[0, 1]) as microphone_recorder:
            microphone_recorder.record(1)  # initialize recorder to reduce latency
            self.recording_microphone = True
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
            volume = max(amax(int16_frames), abs(amin(int16_frames))) / self.int16_max

            if volume != 0 and self.amplification != 1:
                max_amplification = 1 / volume
                amplification = min(self.amplification, max_amplification)

                int16_frames = (int16_frames * amplification).astype(int16)
                volume *= amplification

            self.volume = volume

            chunk = bytes(self.encoder.encode(int16_frames))
            self.track.add_chunk(chunk)

    def get_track(self):
        return self.track

    def set_recording_speaker(self, recording_bool):
        if recording_bool:
            self.record_speaker_frames()
        else:
            self.recording_speaker = False

    def set_recording_microphone(self, recording_bool):
        if recording_bool:
            self.record_microphone_frames()
        else:
            self.recording_microphone = False

    def get_volume(self):
        return self.volume

    def set_amplification(self, amplification):
        self.amplification = amplification

    def run(self):
        while True:
            if self.recording_speaker or self.recording_microphone:
                self.add_chunk()
            else:
                sleep(.1)  # reduce CPU usage

    def join(self, timeout=0):
        self.killed.set()
        super(Recorder, self).join(timeout)
