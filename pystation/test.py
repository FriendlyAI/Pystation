'''
import pyaudio
import wave
import sys

# length of data to read.
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# validation. If a wave file hasn't been specified, exit.

# open the file for reading.
# wf = wave.open('a.wav', 'rb')

# create an audio object
p = pyaudio.PyAudio()

default = p.get_default_input_device_info()
print(default)

# open stream based on the wave object which has been input.
stream = p.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)

# read data (based on the chunk size)
# data = wf.readframes(chunk)

# play stream (looping from beginning of file to the end)
# f = open('../temp/mic.mp3', 'wb+')
# while True:
#     # writing to the stream is what *actually* plays the sound.
#     chunk = stream.read(CHUNK)
#     # f.write(chunk)

# cleanup stuff.
stream.close()
p.terminate()
'''
import os

print(os.getcwd())