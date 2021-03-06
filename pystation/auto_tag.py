from json import loads
from json.decoder import JSONDecodeError
from subprocess import Popen, PIPE, DEVNULL

METADATA_CMD = 'echo \'{ "command": ["get_property", "filtered-metadata"] }\' | socat - /tmp/mpvsocket'
ALT_TITLE_CMD = 'echo \'{ "command": ["get_property", "media-title"] }\' | socat - /tmp/mpvsocket'
PLAYBACK_TIME_CMD = 'echo \'{ "command": ["get_property", "playback-time"] }\' | socat - /tmp/mpvsocket'
DURATION_CMD = 'echo \'{ "command": ["get_property", "duration"] }\' | socat - /tmp/mpvsocket'


def get_mpv_tags():
    p = Popen(METADATA_CMD, shell=True, stdout=PIPE, stderr=DEVNULL)
    out = p.stdout.read()
    if not out:
        return ''

    json_metadata = loads(out.decode('utf-8'))

    data = json_metadata.get('data')
    if data is None:
        return ''

    artist = data.get('Artist')
    title = data.get('Title')

    if artist or title:
        return f'{artist if artist else "Unknown"} - {title if title else "Unknown"}'

    else:
        p = Popen(ALT_TITLE_CMD, shell=True, stdout=PIPE, stderr=DEVNULL)
        json_metadata = loads(p.stdout.read().decode('utf-8'))
        return json_metadata.get('data')


def get_progress():
    p_playback = Popen(PLAYBACK_TIME_CMD, shell=True, stdout=PIPE, stderr=DEVNULL)
    p_duration = Popen(DURATION_CMD, shell=True, stdout=PIPE, stderr=DEVNULL)
    out_playback = p_playback.stdout.read()
    out_duration = p_duration.stdout.read()

    if not out_playback or not out_duration:
        return 0, 0, 0

    try:
        json_playback = loads(out_playback.decode('utf-8'))
        json_duration = loads(out_duration.decode('utf-8'))
    except JSONDecodeError:
        return 0, 0, 0

    playback_time = json_playback.get('data')
    duration = json_duration.get('data')

    if playback_time and duration:
        return float(playback_time) / float(duration), playback_time, duration
    return 0, 0, 0
