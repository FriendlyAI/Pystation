from os import getcwd, remove
from shutil import copyfile

import youtube_dl
from ffmpy import FFmpeg
from mutagen.flac import FLAC
from mutagen.mp3 import MP3

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'temp/%(title)s.%(ext)s'
}

YDL = youtube_dl.YoutubeDL(ydl_opts)

CACHE = set()


def convert_flac(filename, mp3_filename):
    ff = FFmpeg(
        inputs={filename: '-y'},
        outputs={mp3_filename: '-ab 192k -ar 44100 -map_metadata -1 -map 0:a'}
    )
    print(ff.cmd)
    ff.run()


def convert_ogg():
    pass


def convert_aac():
    pass


def convert_webm():
    pass


def convert_mp4():
    pass


def convert_bitrate(filename, new_filename):
    ff = FFmpeg(
        inputs={filename: '-y'},
        outputs={new_filename: '-ab 192k -ar 44100'}
    )
    print(ff.cmd)
    ff.run()


def get_tags(filename, temp=False):
    extension = filename[filename.rindex('.'):]
    new_filename = f'{getcwd()}/temp{filename[filename.rindex("/"):filename.rindex(".")]} temp.mp3'

    if extension == '.mp3':
        id3 = MP3(filename)
        artist = str(id3.get('TPE1', ''))
        title = str(id3.get('TIT2', ''))

        if id3.info.sample_rate != 44100:
            print('converting sample rate')
            convert_bitrate(filename, new_filename)
        else:
            copyfile(filename, new_filename)

    elif extension == '.flac':
        id3 = FLAC(filename)
        artist = id3.get('ARTIST', [''])[0]
        title = id3.get('TITLE', [''])[0]
        convert_flac(filename, new_filename)

    elif extension == '.aac':
        artist = ''
        title = ''
        convert_aac()

    elif extension == '.webm':
        artist = ''
        title = ''
        convert_webm()

    elif extension == '.mp4':
        artist = ''
        title = ''
        convert_mp4()

    else:  # should never be called
        artist = ''
        title = ''

    if temp:
        remove(filename)

    return f'{artist + " - " if artist else ""}{title}' if title else '', new_filename


def clear_tags(filename):
    mp3 = MP3(filename)
    mp3.delete()
    mp3.save()


def get_length(filename):
    return MP3(filename).info.length


def validate(filename, temp=False, cache_url=None):
    trackname, filename = get_tags(filename, temp)

    clear_tags(filename)

    length = get_length(filename)

    if cache_url:  # youtube url downloaded, can download again
        CACHE.remove(cache_url)

    return trackname, filename, length


def youtube_download(url):
    if url in CACHE:  # url currently being downloaded already
        print('url already added')
        return None, None, None
    else:
        CACHE.add(url)
        info = YDL.extract_info(url, download=True)
        filename = YDL.prepare_filename(info)
        filepath = f'{getcwd()}/{filename[:filename.rindex(".")]}.mp3'
        return validate(filepath, temp=True, cache_url=url)
