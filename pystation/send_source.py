import time
from track import Track
import os


def send_files(performance_mode, filenames, file_q, chunk_q, chunk_size):
    for filename in filenames:
        try:
            for file in file_q.queue:
                print(file, end='')
            print()
            track = Track(filename)
        except FileNotFoundError:
            pass
        else:
            chunk = track.read_chunk(chunk_size)
            while chunk:
                chunk_q.put(chunk)
                chunk = track.read_chunk(chunk_size)
                if performance_mode:  # performance mode on
                    time.sleep(.05)  # read slower, still fast enough for 320Kbps MP3 stream with no buffering

            # with open(f'{filename}.mp3', 'rb') as f:
            #     # set track metadata
            #     chunk = f.read(chunk_size)
            #     print('uploading...')
            #     while chunk:
            #         # if counter > 1000:
            #         #     break
            #         chunk_q.put(chunk)
            #         chunk = f.read(chunk)
            #         # counter += 1
            #         # print(counter)
            #
            #         if int(self.user_params['GENERAL']['Performance']):  # performance mode on
            #             time.sleep(.05)  # read slower, still fast enough for 320Kbps MP3 stream with no buffering

            print(f'finished uploading {filename}\ndeleting')
            file_q.get()
            os.remove(filename)
            # while not chunk_q.empty():
            #     time.sleep(.1)


def send_file(performance_mode, filename, file_q, chunk_q, chunk_size):
    try:
        for file in file_q.queue:
            print(file, end='')
        print()
        track = Track(filename)
        chunk = track.read_chunk(chunk_size)

        while chunk:
            chunk_q.put(chunk)
            chunk = track.read_chunk(chunk_size)
            if performance_mode:  # performance mode on
                time.sleep(.05)  # read slower, still fast enough for 320Kbps MP3 stream with no buffering

        print(f'finished uploading {filename}\ndeleting')
        file_q.get()

    except FileNotFoundError:
        pass
