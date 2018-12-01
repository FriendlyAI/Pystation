import youtube_dl
import ffmpeg
import audioop

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


def youtube_download():
    """
    :return: filename
    """
    pass


def convert_bitrate():
    pass


def get_tags():
    """
    :return: f'{artist} - {title}'
    """
    pass


def clear_tags():
    pass
