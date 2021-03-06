# Pystation ![](https://raw.githubusercontent.com/FriendlyAI/Pystation-Stream/master/favicon/32.png)

## Features

- Built-in music player supporting multiple filetypes, including mp3, flac, webm, mp4, etc.
- Player supports music queue, reordering/modifying queue, pause/play, and idle tracks.
- Play youtube videos using links.
- Support for streaming directly from speakers (with loopback) and microphone simultaneously.
    - Boost master volume up to 2x or microphone volume up to 10x
- Automatically get tags and playback data from your mpv player when streaming from your speakers.
  - Run mpv with `mpv file.mkv --input-ipc-server=/tmp/mpvsocket`

## System Requirements

[Python 3.6](https://www.python.org/downloads/)

[ffmpeg](https://www.ffmpeg.org/)

[youtube-dl](https://rg3.github.io/youtube-dl/)

[libshout2](https://ftp.osuosl.org/pub/xiph/releases/libshout/)

[LAME](http://lame.sourceforge.net/download.php)

## Installation
Ensure you have all of the above requirements and refer to the `INSTALL.md` file.

### Linux
You must install tkinter using `sudo apt-get install python3-tk`

### macOS
Because macOS doesn't natively support loopback audio (recording from your speaker's output), it is recommended that you
install Soundflower or similar loopback software and create an aggregate output device to stream to both your preferred
output and the loopback.

## Config
You can set your own default profile by creating a `conf.ini` file in the `config` folder. An example configure file is 
provided.

The default `idle.mp3` is a silent file that will play when the player is idling i.e. there is no track playing or 
queued. You may choose a different idle track by changing the idle file location.

Note: the idle track must be in the correct format or it may cause client disconnects on certain music players (like 
web browsers).

## Troubleshooting
If your listeners are hearing light static when you are streaming from your speakers or microphone, it is likely due to
your (system, not Pystation) output volume being too high.

###### train train, i love pystation
