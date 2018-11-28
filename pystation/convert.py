# ffmpeg -i in.flac -ab 320k out.mp3
# 320 kbps encoding flac

# ffmpeg -i in.mp3 -map 0:a -codec:a copy -map_metadata -1 out.mp3
# clear tags

# youtube-dl --extract-audio --audio-format mp3 --audio-quality 192K
# filename:  --output "%(uploader)s%(title)s.%(ext)s" http://www.youtube.com/watch?v=rtOvBOTyX00
# download from youtube as mp3
