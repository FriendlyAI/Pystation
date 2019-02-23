import subprocess
import json

METADATA_CMD = 'echo \'{ "command": ["get_property", "filtered-metadata"] }\' | socat - /tmp/mpvsocket'
FILENAME_CMD = 'echo \'{ "command": ["get_property", "filename"] }\' | socat - /tmp/mpvsocket'
PLAYBACK_TIME_CMD = 'echo \'{ "command": ["get_property", "playback-time"] }\' | socat - /tmp/mpvsocket'
DURATION_CMD = 'echo \'{ "command": ["get_property", "duration"] }\' | socat - /tmp/mpvsocket'


def get_mpv_tags():
    p = subprocess.Popen(METADATA_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    out = p.stdout.read()
    if not out:
        return ''

    json_metadata = json.loads(out.decode('utf-8'))

    data = json_metadata.get('data')
    if data is None:
        return ''

    artist = data.get('Artist')
    title = data.get('Title')

    if artist or title:
        return f'{artist if artist else "Unknown"} - {title if title else "Unknown"}'

    else:
        p = subprocess.Popen(FILENAME_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        json_metadata = json.loads(p.stdout.read().decode('utf-8'))
        return json_metadata.get('data')


def get_progress():
    p_playback = subprocess.Popen(PLAYBACK_TIME_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    p_duration = subprocess.Popen(DURATION_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    out_playback = p_playback.stdout.read()
    out_duration = p_duration.stdout.read()

    if not out_playback or not out_duration:
        return 0, 0, 0

    json_playback = json.loads(out_playback.decode('utf-8'))
    json_duration = json.loads(out_duration.decode('utf-8'))

    playback_time = json_playback.get('data')
    duration = json_duration.get('data')

    if playback_time and duration:
        return float(playback_time) / float(duration), playback_time, duration
    return 0, 0, 0
