from parse_audio import validate
from os.path import isfile


class Track:
    def __init__(self, filename):
        if isfile(filename):
            self.track, self.filename, self.length = validate(filename)
            self.length = None
            self.file_reader = open(self.filename, 'rb')
        else:
            raise FileNotFoundError(f'No file {filename}')

    def read_chunk(self, chunk_size):
        return self.file_reader.read(chunk_size)

    def get_track(self):
        return self.track

    def get_filename(self):
        return self.filename

    def get_length(self):
        return self.length
