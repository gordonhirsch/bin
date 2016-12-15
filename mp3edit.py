#!/usr/bin/python

# Notes:
# The mid3v2 utility requires the pythyon mutagen package to be installed.
# To avoid Mac protection issues, install with "pip install --user mutagen"
# Add ~/Library/Python/2.7/bin (or similar) to the path to pick it up.
# Other MacOS id3 utilities (id3info, etc.) are buggy at times. 

import os
import subprocess
import sh
import re
import yaml
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Set genres in MP3 files")
    parser.add_argument("root", help="root of all MP3 files")
    parser.add_argument("--rules", type=argparse.FileType('r'), help="rules file")
    parser.add_argument("--overwrite", action="store_true", help="overwrite existing genres")
    parser.add_argument("--dry-run", action="store_true", help="print new genres without changing files")
    parser.add_argument("--verbose", action="store_true", help="print diagnostic info")
    return parser.parse_args()

args = parse_args()
yaml = yaml.load(args.rules)
tags_of_interest = yaml.keys()
tags_of_interest.append('TCON')

def get_mp3_tags(fn):    
    mp3_tags = {}
#    for line in sh.id3info(fn): (line splitting was wrong for Beck Guero Song 2)
    for line in subprocess.check_output(["mid3v2", fn]).splitlines():
        for tag in tags_of_interest:
            match_result = re.match(r'^%s=(.*)' % tag, line.strip())
            if match_result:
                if args.verbose:
                    print "Matched tag: %s with %s" % (tag, match_result.group(1))
                mp3_tags[tag] = match_result.group(1)
    return mp3_tags

def process_mp3(file):
    if args.verbose:
        print "---------- Processing file %s" % file
    fn = os.path.join(root, file)
    mp3_tags = get_mp3_tags(fn)    
    current_genres = mp3_tags.get('TCON', '').split(';')
    new_genres = current_genres if not args.overwrite else []
    for tag, edits in yaml.iteritems():
        if tag in mp3_tags.keys():
            new_genres_str = ";".join(new_genres)
            tag_value = mp3_tags[tag]
            if tag_value in edits:
                requested_genres = edits[tag_value].split(';')
                new_genres.extend(x for x in requested_genres if x not in new_genres)
    if new_genres:
        new_genres_str = ";".join(new_genres)
        print fn, ";".join(current_genres), new_genres_str
        if not args.dry_run:
            sh.mid3v2('--TCON', new_genres_str, fn)
    elif args.verbose:
        print "***** Skipping %s" % fn

for root, dirs, files in os.walk(args.root):
    for file in files:
        if re.match(r'.*\.mp3$', file):
            process_mp3(file)
