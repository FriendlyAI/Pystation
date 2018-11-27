# ffmpeg -i in.flac -ab 320k out.mp3
# 320 kbps encoding flac

# ffmpeg -i in.mp3 -map 0:a -codec:a copy -map_metadata -1 out.mp3
# clear tags
