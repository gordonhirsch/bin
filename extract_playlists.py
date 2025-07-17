import plistlib
import os

# CONFIGURE
input_xml = '/Users/gzh/old iTunes/iTunes/iTunes Music Library.xml'  # update path
output_dir = '/Users/gzh/Desktop/iTunes_Playlists'

# Make sure output dir exists
os.makedirs(output_dir, exist_ok=True)

# Load the iTunes XML
with open(input_xml, 'rb') as f:
    plist = plistlib.load(f)

# Build track ID -> path map
tracks = plist['Tracks']
track_paths = {}
for tid, info in tracks.items():
    location = info.get('Location')
    if location and location.startswith('file://'):
        path = location.replace('file://', '')
        path = path.replace('%20', ' ')
        track_paths[int(tid)] = path

# Process each playlist
for playlist in plist['Playlists']:
    name = playlist.get('Name', 'Untitled')
    items = playlist.get('Playlist Items')
    if not items:
        continue

    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
    m3u_path = os.path.join(output_dir, f"{safe_name}.m3u")

    with open(m3u_path, 'w') as out:
        out.write("#EXTM3U\n")
        for item in items:
            tid = item.get('Track ID')
            path = track_paths.get(tid)
            if path:
                out.write(path + "\n")

print(f"Done. Playlists written to: {output_dir}")
