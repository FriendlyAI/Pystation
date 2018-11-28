import queue
import threading
import time
import configparser

from shout import Shouter

user_params = configparser.ConfigParser()
user_params.read('config/conf.ini')

music_q = queue.Queue()
fallback_q = queue.Queue()

SHOUTER = Shouter(user_params, music_q)


def play():
    # counter = 0
    while True:
        filename = input('filename: ')
        try:
            with open(f'{filename}.mp3', 'rb') as f:
                chunk = f.read(4096)
                print('uploading...')
                while chunk:
                    # if counter > 1000:
                    #     break
                    music_q.put(chunk)
                    chunk = f.read(4096)
                    # counter += 1
                    # print(counter)

                    if int(user_params['GENERAL']['Performance']):  # performance mode on
                        time.sleep(.05)  # read slower, still fast enough for 320Kbps MP3 stream with no buffering

                print('finished')
        except FileNotFoundError:
            print('file not found')


# threading.Thread(target=SHOUTER).start()
SHOUTER.start()
time.sleep(1)
play()
