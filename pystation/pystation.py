from os import remove, listdir, getcwd
from os.path import isfile
from sys import exit

from config import run_config
from player import run_player

# Check cwd
if not getcwd().endswith('Pystation'):
    print('Error: Pystation must be run from the base directory (Pystation/)\nExiting...')
    exit()

temp_path = f'{getcwd()}/temp'

if __name__ == '__main__':
    run_config()
    run_player()

    # delete temp files if any were left over
    for file in listdir(temp_path):
        try:
            remove(f'{temp_path}/{file}')
        except (PermissionError, IsADirectoryError):
            pass

    if isfile('/tmp/mpvsocket'):
        remove('/tmp/mpvsocket')
