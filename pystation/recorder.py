import lameenc
from queue import Queue
from threading import Thread, Event
from time import sleep

import soundcard
from numpy import int16, mean

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

        self.init_speaker('0')  # TODO remove, put in config screen
        self.init_microphone('0')  # TODO remove, put in config screen

        print('loopbacks: ', soundcard.all_microphones(include_loopback=True))
        print('not loopback: ', soundcard.all_microphones(include_loopback=False))

    def init_speaker(self, id_):
        # TODO check is speaker.channels >= 2, maybe simulate stereo with mono
        id_ = 'Soundflower'
        self.speaker = soundcard.get_microphone(f'{id_}', include_loopback=True)
        print(f'speaker: {self.speaker}')
        # print(dir(self.speaker))
        # print(self.speaker.channels, self.speaker.record(1000, 22050))

        if self.microphone and self.microphone.id == self.speaker.id:
            self.speaker = None
            print('duplicate microphone and speaker')

    def init_microphone(self, id_):
        id_ = 'Built-in'
        self.microphone = soundcard.get_microphone(f'{id_}', include_loopback=False)
        print(f'mic: {self.microphone}')

        if self.speaker and self.microphone.id == self.speaker.id:
            self.microphone = None
            print('duplicate microphone and speaker')

    @thread
    def record_speaker_frames(self):
        with self.speaker.recorder(44100, channels=[0, 1]) as speaker_recorder:
            while not self.killed.is_set() and self.recording_speaker:
                numpy_frames = speaker_recorder.record(self.num_frames)
                int16_frames = (numpy_frames * self.int16_max).astype(int16)  # .clip(self.int16_min, self.int16_max)
                self.speaker_queue.put(int16_frames)
        self.speaker_queue = Queue()  # clear queue

    @thread
    def record_microphone_frames(self):
        with self.microphone.recorder(44100, channels=[0, 1]) as microphone_recorder:
            while not self.killed.is_set() and self.recording_microphone:
                numpy_frames = microphone_recorder.record(self.num_frames)
                int16_frames = (numpy_frames * self.int16_max).astype(int16)  # .clip(self.int16_min, self.int16_max)
                self.microphone_queue.put(int16_frames)
        self.microphone_queue = Queue()  # clear queue

    def add_chunk(self):
        if self.recording_speaker and self.recording_microphone:
            microphone_chunk = self.microphone_queue.get()
            speaker_chunk = self.speaker_queue.get()
            mean_chunk = mean([microphone_chunk, speaker_chunk], axis=0, dtype=int16)
            # TODO weighted average towards speaker?

            chunk = bytes(self.encoder.encode(mean_chunk))
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
