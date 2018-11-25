#! /usr/bin/env python

""" A simple demo using aubio and pyaudio to play beats in real time

Note you will need to have pyaudio installed: `pip install pyaudio`.

Examples:
    ./demo_tapthebeat.py ~/Music/track1.ogg

When compiled with ffmpeg/libav, you should be able to open remote streams. For
instance using youtube-dl (`pip install youtube-dl`):

    ./demo_tapthebeat.py `youtube-dl -xg https://youtu.be/zZbM9n9j3_g`

"""

import sys
import time
import pyaudio
import wave
import requests
# import aubio
# import numpy as np

win_s = 1024                # fft size
hop_s = win_s // 2          # hop size

# parse command line arguments
# if len(sys.argv) < 2:
#     print("Usage: %s <filename> [samplerate]" % sys.argv[0])
#     sys.exit(1)
#
# filename = sys.argv[1]
#
# samplerate = 0
# if len(sys.argv) > 2:
#     samplerate = int(sys.argv[2])

# # create aubio source
# a_source = aubio.source(filename, samplerate, hop_s)
# samplerate = a_source.samplerate
#
# # create aubio tempo detection
# a_tempo = aubio.tempo("default", win_s, hop_s, samplerate)
#
# # create a simple click sound
# click = 0.7 * np.sin(2. * np.pi * np.arange(hop_s) / hop_s * samplerate / 3000.)
#
#
# # pyaudio callback
# def pyaudio_callback(_in_data, _frame_count, _time_info, _status):
#     samples, read = a_source()
#     is_beat = a_tempo(samples)
#     if is_beat:
#         samples += click
#         # print ('tick') # avoid print in audio callback
#     audiobuf = samples.tobytes()
#     if read < hop_s:
#         return audiobuf, pyaudio.paComplete
#     return audiobuf, pyaudio.paContinue
#
#
# # create pyaudio stream with frames_per_buffer=hop_s and format=paFloat32
p = pyaudio.PyAudio()
pyaudio_format = pyaudio.paFloat32
frames_per_buffer = hop_s
n_channels = 1
# stream = p.open(format=pyaudio_format, channels=n_channels, rate=samplerate,
#                 output=True, frames_per_buffer=frames_per_buffer,
#                 stream_callback=pyaudio_callback)

# FORMAT = pyaudio.paFloat32
# CHANNELS = 2
# RATE = 22050
CHUNK_SIZE = 1024

filename = input('file: ')
wf = wave.open(f'Temp_Audio/{filename}', 'rb')

# p.get_device_info_by_index(i)
default = p.get_default_input_device_info()
print(default)

FORMAT = p.get_format_from_width(wf.getsampwidth())
CHANNELS = wf.getnchannels()
RATE = wf.getframerate()
print(type(FORMAT))

print(f'Format: {FORMAT}\nChannels: {CHANNELS}\nFramerate: {RATE}')

stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                output=True)


data = wf.readframes(CHUNK_SIZE)

# wait for stream to finish
while data:
    # data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
    # print(data)
    stream.write(data)
    data = wf.readframes(CHUNK_SIZE)

stream.close()
# close pyaudio
p.terminate()
