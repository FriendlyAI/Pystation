from os import remove, sep
from os.path import isfile
from queue import Queue

from parse_audio import validate, youtube_download


class Track:
    def __init__(self, chunk_size, filename=None, url=None):
        if filename and isfile(filename):
            self.trackname, self.filename, self.length = validate(filename)
        elif url:
            self.trackname, self.filename, self.length = youtube_download(url)
        else:
            self.filename = None
            self.trackname = 'LIVE'

        if self.filename:
            self.file_reader = open(self.filename, 'rb')

        self.chunk_size = chunk_size

        self.chunk_queue = Queue()

        self.read = False

        self.num_chunks = 0

    def read_file(self):
        chunk = self.file_reader.read(self.chunk_size)
        while chunk:
            self.chunk_queue.put(chunk)
            chunk = self.file_reader.read(self.chunk_size)
            self.num_chunks += 1

        self.delete_file()
        self.read = True

    def delete_file(self):
        try:
            remove(self.filename)
        except FileNotFoundError:  # file already removed
            print(f'couldn\'t delete {self.trackname}|{self.filename}')

    def add_chunk(self, chunk):
        """
        Used only for speaker/microphone
        """
        self.chunk_queue.put(chunk)

    def get_filename(self):
        return self.filename

    def get_length(self):
        return self.length

    def get_num_chunks(self):
        return self.num_chunks

    def get_chunk_queue(self):
        return self.chunk_queue

    def set_chunk_queue(self, queue):
        self.chunk_queue = queue

    def get_read(self):
        return self.read

    def set_trackname(self, name):
        self.trackname = name

    def get_trackname(self):
        if self.trackname:
            return self.trackname
        else:
            return self.filename[self.filename.rindex(sep) + 1:self.filename.rindex(' temp')]

    def __repr__(self):
        return self.get_trackname()
