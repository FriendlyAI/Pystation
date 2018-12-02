from os.path import isfile

from parse_audio import validate, youtube_download


class Track:
    def __init__(self, filename=None, url=None):
        if filename and isfile(filename):
            self.trackname, self.filename, self.length = validate(filename)
        elif url:
            self.trackname, self.filename, self.length = youtube_download(url)

        self.file_reader = open(self.filename, 'rb')

    def read_chunk(self, chunk_size):
        return self.file_reader.read(chunk_size)

    def get_trackname(self):
        return self.trackname

    def get_filename(self):
        return self.filename

    def get_length(self):
        return self.length

    def __str__(self):
        return self.trackname if self.trackname \
            else self.filename[self.filename.rindex['/'] + 1, self.filename.rindex['.']]
