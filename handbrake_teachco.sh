#!/bin/bash

for f in *.mkv; do
  HandBrakeCLI -i $f -o out/$f --encoder x264 --quality 15 --decomb --detelecine --x264-preset medium;
done