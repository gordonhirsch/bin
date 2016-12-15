#!/usr/bin/python

import os
import sh
import re
import argparse

tags_of_interest = ["TPE2", "TPE1"]

def parse_args():
    parser = argparse.ArgumentParser(description="Get MP3 artist, giving priority to album artist")
    parser.add_argument("file", help="the MP3 file")
    return parser.parse_args()

def get_mp3_tags(fn):    
    mp3_tags = {}
    for line in sh.id3info(fn):
        for tag in tags_of_interest:
            match_result = re.match(r'^=== %s \(.*?\): (.*)' % tag, line.strip())
            if match_result:
                mp3_tags[tag] = match_result.group(1)
    return mp3_tags

args = parse_args()
tags = get_mp3_tags(args.file)

if "TPE2" in tags:
    print tags["TPE2"]
#elif "TPE1" in tags:
#    print tags["TPE1"]
