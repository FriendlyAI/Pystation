from player import run_player

from shout import Shouter

from playlist import Playlist

import configparser

from queue import Queue


user_params = configparser.ConfigParser()
user_params.read('config/conf.ini')

file_q = Queue()
chunk_q = Queue()

playlist_ = Playlist()

track = 'None'

if __name__ == '__main__':
    shouter = Shouter(user_params, chunk_q)
    shouter.start()

    run_player(shouter, user_params, file_q, chunk_q)
