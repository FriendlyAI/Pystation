from os import remove, listdir, getcwd
from os.path import isfile

from player import run_player

temp_path = f'{getcwd()}/temp'

if __name__ == '__main__':
    run_player()

    # delete temp files if any were left over
    for file in listdir(temp_path):
        try:
            remove(f'{temp_path}/{file}')
        except (PermissionError, IsADirectoryError):
            pass

    if isfile('/tmp/mpvsocket'):
        remove('/tmp/mpvsocket')
