from shout import Shouter
import queue
import threading
import time

music_q = queue.Queue()
SHOUTER = Shouter(music_q)


def play():
    counter = 0
    with open('Temp_Audio/a.mp3', 'rb') as f:
        chunk = f.read(1024)
        while chunk:
            if counter > 400:
                break
            music_q.put(chunk)
            chunk = f.read(1024)
            print(counter)
            counter += 1
    time.sleep(20)
    with open('Temp_Audio/shorta.mp3', 'rb') as f:
        chunk = f.read(1024)
        while chunk:
            music_q.put(chunk)
            chunk = f.read(1024)


threading.Thread(target=play).start()
SHOUTER.run()
