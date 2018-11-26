#! /usr/bin/env python

import sys
import time
import pyaudio
import wave
import requests
import shouty

p = pyaudio.PyAudio()


def connect_icecast():
    print('Initial request: ',
          requests.put('http://172.16.186.128:8000/main.mp3',
                       auth=('admin', 'hackme'),
                       headers={'host': 'localhost:8000',
                                'authorization': 'Basic c291cmNlOmhhY2ttZQ==',
                                'User-Agent': 'curl/7.51.0',
                                'Accept': '*/*',
                                'Transfer-Encoding': 'chunked',
                                'Content-Type': 'audio/mpeg',
                                'Ice-Public': '1',
                                'Ice-Name': 'Teststream',
                                'Ice-Description': 'This is just a simple test stream',
                                'Ice-URL': 'http://example.org',
                                'Ice-Genre': 'Various',
                                'Expect': '100-continue'})
          )


def send_chunk():
    # start = time.time()
    # # return
    # print('Chunk PUT: ',
    #       requests.put('http://172.16.186.128:8000/main.mp3',
    #                    auth=('admin', 'hackme'),
    #                    headers={'host': 'localhost:8000',
    #                             'authorization': 'Basic c291cmNlOmhhY2ttZQ==',
    #                             'User-Agent': 'curl/7.51.0',
    #                             'Accept': '*/*',
    #                             'Transfer-Encoding': 'chunked',
    #                             'Content-Type': 'audio/mpeg',
    #                             'Ice-Public': '1',
    #                             'Ice-Name': 'Teststream',
    #                             'Ice-Description': 'This is just a simple test stream',
    #                             'Ice-URL': 'http://example.org',
    #                             'Ice-Genre': 'Various',
    #                             'Expect': '100-continue'},
    #                    data={'audio/mpeg': b'1'})
    #       )
    # print(time.time() - start, chunk)
    params = {
        'host': '172.16.186.128',
        'port': 8000,
        'user': 'admin',
        'password': 'hackme',
        'format': shouty.Format.MP3,
        'mount': '/main.mp3',
        'audio_info': {
            'channels': '2'
        }
    }
    with shouty.connect(**params) as connection:
        with open('Temp_Audio/shorta.mp3', 'rb') as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                print(chunk)
                connection.send(chunk)
                connection.sync()
        time.sleep(10)
        with open('Temp_Audio/shorta.mp3', 'rb') as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                print(chunk)
                connection.send(chunk)
                connection.sync()


send_chunk()

# CHUNK_SIZE = 1024
#
# filename = input('file: ')
# wf = wave.open(f'Temp_Audio/{filename}', 'rb')
#
# # p.get_device_info_by_index(i)
# default = p.get_default_input_device_info()
# print(default)
#
# FORMAT = p.get_format_from_width(wf.getsampwidth())
# CHANNELS = wf.getnchannels()
# RATE = wf.getframerate()
# print(type(FORMAT))
#
# print(f'Format: {FORMAT}\nChannels: {CHANNELS}\nFramerate: {RATE}')
#
# stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
#                 output=True)
#
# # connect_icecast()
# data = wf.readframes(CHUNK_SIZE)
#
# # wait for stream to finish
# while data:
#     # data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
#     # print(data)
#     # stream.write(data)
#     send_chunk(data)
#     data = wf.readframes(CHUNK_SIZE)
#
# stream.close()
# # close pyaudio
# p.terminate()
