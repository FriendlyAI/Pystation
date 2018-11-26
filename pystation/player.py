import queue
import threading
import time
import configparser

from pystation.shout import Shouter

user_params = configparser.ConfigParser()
user_params.read('config/conf.ini')

music_q = queue.Queue()

SHOUTER = Shouter(user_params, music_q)


def play():
    # counter = 0
    with open('temp/mg.mp3', 'rb') as f:
        chunk = f.read(4096)
        while chunk:
            # if counter > 1000:
            #     break
            music_q.put(chunk)
            chunk = f.read(4096)
            # print(counter)
            # counter += 1
    # time.sleep(20)
    # with open('temp/shorta.mp3', 'rb') as f:
    #     chunk = f.read(1024)
    #     while chunk:
    #         music_q.put(chunk)
    #         chunk = f.read(1024)


threading.Thread(target=play).start()
SHOUTER.run()
