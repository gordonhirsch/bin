#!/usr/bin/env ruby

require 'fileutils'
require 'open3'

# L&O Criminal Intent: Volume 0.25
# Without a Trace: Volume 0.25
# Perry Mason: Volume 0.6 
# Columbo: Volume 0.5

# Check arguments
if ARGV.length != 3
  puts "Usage: ruby change_volume.rb <source_dir> <destination_dir> <volume_multiplier>"
  exit 1
end

src_dir = File.expand_path(ARGV[0])
dest_dir = File.expand_path(ARGV[1])
volume_multiplier = ARGV[2]

def get_audio_info(file_path)
  cmd = ["ffmpeg", "-i", file_path]
  _, stderr, _ = Open3.capture3(*cmd)

  audio_line = stderr.each_line.find { |line| line.include?("Audio:") }

  if audio_line
    # Extract codec (4th token after 'Audio:')
    codec = audio_line[/Audio:\s+([^\s,]+)/, 1] || "aac"

    # Extract bitrate (e.g., "128 kb/s")
    bitrate_match = audio_line.match(/(\d+)\s*kb\/s/)
    bitrate = bitrate_match ? "#{bitrate_match[1]}k" : "128k"
    return codec, bitrate
  else
    return "aac", "128k"
  end
end

puts "🚀 Starting volume adjustment..."
puts "Source: #{src_dir}"
puts "Destination: #{dest_dir}"
puts "Volume multiplier: #{volume_multiplier}"

Dir.glob("#{src_dir}/**/*.ts").each do |src_file|
  rel_path = src_file.sub(/^#{Regexp.escape(src_dir)}\/?/, "")
  dest_file = File.join(dest_dir, rel_path)
  dest_path = File.dirname(dest_file)

  puts "🔧 Processing: #{src_file}"
  puts "     Relative: #{rel_path}"
  puts "     Output:   #{dest_file}"

  FileUtils.mkdir_p(dest_path)

  codec, bitrate = get_audio_info(src_file)
  puts "     Codec: #{codec}, Bitrate: #{bitrate}"

  cmd = [
    "ffmpeg", "-i", src_file,
    "-vcodec", "copy",
    "-acodec", codec,
    "-b:a", bitrate,
    "-af", "volume=#{volume_multiplier}",
    dest_file
  ]

  puts "     Running: #{cmd.join(" ")}"

  system(*cmd) or abort("❌ ffmpeg failed for: #{src_file}")

  puts "✅ Done."
end

puts "🎉 All files processed successfully."
