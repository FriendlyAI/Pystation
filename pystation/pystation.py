from configparser import ConfigParser
from os import remove, listdir, getcwd

from player import run_player
from playlist import Playlist
from shout import Shouter

user_params = ConfigParser()
user_params.read('config/conf.ini')

playlist_ = Playlist(user_params.getint('ICECAST', 'ChunkSize'))

temp_path = f'{getcwd()}/temp'

if __name__ == '__main__':
    shouter = Shouter(user_params, playlist_)
    shouter.start()

    run_player(user_params, playlist_)

    # delete temp files if any were left over
    for file in listdir(temp_path):
        try:
            remove(f'{temp_path}/{file}')
        except PermissionError:
            pass
