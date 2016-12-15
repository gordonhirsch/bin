find . -name '*.mp3' -print0 | xargs -0 -L 1 ~/bin/getartist.py | sort --ignore-case | uniq
