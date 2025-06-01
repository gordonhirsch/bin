#!/bin/bash

# This script never completely worked. See change_volume.rb instead

set -euo pipefail

SRC_DIR="$1"
DEST_DIR="$2"
VOLUME_MULTIPLIER="$3"

if [[ -z "$SRC_DIR" || -z "$DEST_DIR" || -z "$VOLUME_MULTIPLIER" ]]; then
  echo "Usage: $0 <source_dir> <destination_dir> <volume_multiplier>"
  echo "Example: $0 \"/Volumes/video/dvr\" \"/Volumes/output\" 0.9"
  exit 1
fi

# Function to extract audio codec and bitrate
get_audio_info() {
  local file="$1"
  ffmpeg -i "$file" 2>&1 | awk '
    /Audio:/ {
      codec=$4
      for (i=1; i<=NF; i++) {
        if ($i ~ /^[0-9]+k$/) {
          print codec, $i
          exit
        }
      }
      print codec, "128k"
    }'
}

echo "🚀 Starting volume adjustment..."
echo "Source: $SRC_DIR"
echo "Destination: $DEST_DIR"
echo "Volume multiplier: $VOLUME_MULTIPLIER"

# Export function and vars for use in find -exec
export VOLUME_MULTIPLIER SRC_DIR DEST_DIR

export -f get_audio_info

# Safe find-exec loop
find "$SRC_DIR" -type f -name '*.ts' -print0 |
while IFS= read -r -d '' src_file; do
  rel_path=$(grealpath --relative-to="$SRC_DIR" "$src_file")
  dest_file="$DEST_DIR/$rel_path"
  dest_dir=$(dirname "$dest_file")

  echo "🔧 Processing: $src_file"
  echo "     Relative: $rel_path"
  echo "     Output:   $dest_file"

  mkdir -p "$dest_dir"

  read -r codec bitrate <<< "$(get_audio_info "$src_file")"
  echo "     Codec: $codec, Bitrate: $bitrate"

  ffmpeg -i "$src_file" -vcodec copy -acodec "$codec" -b:a "$bitrate" -af "volume=${VOLUME_MULTIPLIER}" "$dest_file"
  if [[ $? -ne 0 ]]; then
    echo "❌ FFmpeg failed for: $src_file"
    exit 1
  fi

  echo "✅ Done."
done

echo "🎉 All files processed successfully."
