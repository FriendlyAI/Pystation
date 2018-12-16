from os import remove
from os.path import isfile
from queue import Queue

from parse_audio import validate, youtube_download


class Track:
    def __init__(self, filename=None, url=None):
        if filename and isfile(filename):
            self.trackname, self.filename, self.length = validate(filename)
        elif url:
            self.trackname, self.filename, self.length = youtube_download(url)

        if not self.filename:  # file failed to download/validate
            raise FileNotFoundError

        self.file_reader = open(self.filename, 'rb')

        self.chunk_queue = Queue()

        self.read = False

    def read_chunk(self, chunk_size):
        return self.file_reader.read(chunk_size)

    def delete_file(self):
        try:
            remove(self.filename)
            print(f'loaded {self.trackname}|{self.filename} and deleted')
        except FileNotFoundError:  # file already removed
            print(f'couldnt delete {self.trackname}|{self.filename}')

    def get_trackname(self):
        return self.trackname

    def get_filename(self):
        return self.filename

    def get_length(self):
        return self.length

    def get_chunk_queue(self):
        return self.chunk_queue

    def set_chunk_queue(self, queue):
        self.chunk_queue = queue

    def get_read(self):
        return self.read

    def set_read(self):
        self.read = True

    def __repr__(self):
        if self.trackname:
            return self.trackname
        else:
            return self.filename[self.filename.rindex('/') + 1:self.filename.rindex(' temp')]
