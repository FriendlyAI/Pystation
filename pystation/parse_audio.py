import os
from shutil import copyfile

import youtube_dl
from ffmpy import FFmpeg
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


# ffmpeg -i in.flac -ab 320k out.mp3
# 320 kbps encoding flac

# ffmpeg -i in.mp3 -map 0:a -codec:a copy -map_metadata -1 out.mp3
# clear tags

# ffmpeg -i in.mp3 -ab 192k -ar 44100 out.mp3
# convert to 44100 Hz

# youtube-dl --extract-audio --audio-format mp3 --audio-quality 192K
# filename:  --output "%(title)s.%(ext)s"
# get filename: --get-filename
# -f 'bestaudio[asr=44100]'
# download from youtube as mp3

# ffmpeg -i in.mp3 -c:a libvorbis -q:a 4 out.ogg
# -q 192000?
# ogg


def convert_flac():
    pass


def convert_ogg():
    pass


def convert_m4a():
    pass


def convert_webm():
    pass


def convert_bitrate(filename, new_filename):
    ff = FFmpeg(
        inputs={filename: '-y'},
        outputs={new_filename: '-ab 192k -ar 44100'}
    )
    print(ff.cmd)
    ff.run()

    os.remove(filename)


def get_tags(filename):
    """
    :return: f'{artist} - {title}'
    """
    id3 = MP3(filename)
    new_filename = f'{os.getcwd()}/temp{filename[filename.rindex("/"):filename.rindex(".")]} temp.mp3'

    if id3.info.sample_rate != 44100:
        print('converting sample rate')
        convert_bitrate(filename, new_filename)
    else:
        copyfile(filename, new_filename)
        os.remove(filename)

    # print(id3.pprint())

    id3 = MP3(new_filename)
    artist = str(id3.get('TPE1', ''))
    title = str(id3.get('TIT2', ''))

    return f'{artist + " - " if artist else ""}{title}' if title else '', new_filename


def clear_tags(filename):
    mp3 = MP3(filename)
    mp3.delete()
    mp3.save()


def get_length(filename):
    return MP3(filename).info.length


def validate(filename):
    # TODO check extension, convert
    trackname, filename = get_tags(filename)
    clear_tags(filename)

    length = get_length(filename)

    return trackname, filename, length


def youtube_download(url):
    info = YDL.extract_info(url, download=True)
    filename = YDL.prepare_filename(info)
    filepath = f'{os.getcwd()}/{filename[:filename.rindex(".")]}.mp3'
    print(filepath)
    return validate(filepath)
