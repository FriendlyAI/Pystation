import configparser

from player import run_player
from playlist import Playlist
from shout import Shouter

user_params = configparser.ConfigParser()
user_params.read('config/conf.ini')

playlist_ = Playlist(user_params.getint('ICECAST', 'Chunk Size'))

if __name__ == '__main__':
    shouter = Shouter(user_params, playlist_)
    shouter.start()

    run_player(user_params, playlist_)
