from os import getcwd, remove, rename, sep, path
from shutil import copyfile

from ffmpy import FFmpeg, FFRuntimeError
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from youtube_dl import YoutubeDL

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': f'temp{sep}%(title)s.%(ext)s'
}

YDL = YoutubeDL(ydl_opts)

CACHE = set()


def convert_to_mp3(filename, temp_filename):
    ff = FFmpeg(
        inputs={filename: '-y'},
        outputs={temp_filename: '-vn -ab 192k -ar 44100 -ac 2 -map_metadata -1 -map 0:a'}
    )
    try:
        ff.run()
    except FFRuntimeError:
        print('error converting file to mp3. check there is an audio stream?')


def reformat_mp3(filename, temp_filename):
    ff = FFmpeg(
        inputs={filename: '-y'},
        outputs={temp_filename: '-ab 192k -ar 44100 -ac 2'}
    )
    ff.run()


def get_tags(filename, temp=False):
    extension = filename[filename.rindex('.'):]
    temp_filename = path.join(getcwd(), 'temp', f'{filename[filename.rindex(sep) + 1:filename.rindex(".")]} temp.mp3')

    if extension == '.mp3':
        id3 = MP3(filename)
        artist = str(id3.get('TPE1', ''))
        title = str(id3.get('TIT2', ''))

        if id3.info.sample_rate != 44100 or id3.info.channels != 2:
            reformat_mp3(filename, temp_filename)
            if temp:
                remove(filename)
        elif temp:
            rename(filename, temp_filename)
        else:
            copyfile(filename, temp_filename)

    else:
        if extension == '.flac':
            id3 = FLAC(filename)
            artist = id3.get('ARTIST', [''])[0]
            title = id3.get('TITLE', [''])[0]

        elif extension == '.mp4':
            tags = MP4(filename).tags
            artist = tags.get('\xa9ART', [''])[0]
            title = tags.get('\xa9nam', [''])[0]

        else:  # aac, webm, etc
            artist = ''
            title = ''

        convert_to_mp3(filename, temp_filename)

    if artist or title:
        return f'{artist if artist else "<UNKNOWN>"} - {title if title else "<UNKNOWN>"}', temp_filename
    else:
        return '', temp_filename


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
        filepath = path.join(getcwd(), filename[:filename.rindex(".")] + '.mp3')

        return validate(filepath, temp=True, cache_url=url)
