#!/bin/sh

find $1 -mtime +$2 -exec rm {} \;