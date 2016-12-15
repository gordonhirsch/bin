#!/bin/bash

#
# Creates an mkv close to the original MakeMKV-ripped size. 
#
# * --quality: improving (lower number) even one notch greatly increases output size
# * --decomb/--detelecine: useful for interlaced video (prob not needed for HD)
# * --encoder: x264 historically least problematic for kodi
# * --x264-preset: slower values seem also to increase file size (?)
# * -a: must list all audio tracks to encode (use --scan to list tracks in input)
# * --aencoder copy:*: pass thru audio with no re-encoding (when supported, 
#     need to use --scan to determine the audio encoding of source. 
#     Then set copy: value accordingly. Need to include one copy: per track, comma
#     separated
# 
HandBrakeCLI -i title09.mkv -o "Portishead Roseland New York.mkv" --encoder x264 --quality 13 --decomb --detelecine --x264-preset medium -a 1,2 --aencoder copy:ac3,copy:ac3
