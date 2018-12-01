import youtube_dl
from ffmpy import FFmpeg
import audioop
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import os

ydl_opts = {
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

# youtube-dl --extract-audio --audio-format mp3 --audio-quality
# filename:  --output "%(title)s.%(ext)s"
# get filename: --get-filename
# -f 'bestaudio[asr=44100]'
# download from youtube as mp3

# ffmpeg -i in.mp3 -c:a libvorbis -q:a 4 out.ogg
# -q 192000?
# ogg

# fallback, devil need resampling


def convert_flac():
    pass


def convert_ogg():
    pass


def convert_m4a():
    pass


def convert_webm():
    pass


def youtube_download(url):
    """
    :return: filename
    """
    out = YDL.extract_info(url, download=True)
    filename = YDL.prepare_filename(out)
    filepath = f'{filename[:filename.rindex(".")]}.mp3'
    return validate(filepath)


def convert_bitrate(filename):
    new_filename = f'{filename[:filename.rindex(".")]} 1.mp3'
    ff = FFmpeg(
        inputs={filename: '-y'},
        outputs={new_filename: '-ab 192k -ar 44100'}
    )
    print(ff.cmd)
    ff.run()

    os.remove(f'{filename}')

    return new_filename


def get_tags(filename):
    """
    :return: f'{artist} - {title}'
    """
    id3 = MP3(filename)

    if id3.info.sample_rate != 44100:
        print('converting sample rate')
        filename = convert_bitrate(filename)  # update filename
        id3 = MP3(filename)  # update id3

    # print(id3.pprint())

    artist = str(id3.get('TPE1', ''))
    title = str(id3.get('TIT2', ''))

    # clear_tags(filename)

    return f'{artist + " - " if artist else ""}{title}' if title else '', filename


def clear_tags(filename):
    mp3 = MP3(filename)
    mp3.delete()
    mp3.save()


def validate(filename):
    """
    channels
    sample rate
    extension
    clear tags
    :return: bool: successful conversion to file format for stream
    """
    track, filename = get_tags(filename)
    clear_tags(filename)
    return track, filename
