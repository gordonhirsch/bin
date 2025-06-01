#!/usr/bin/env ruby

require 'fileutils'
require 'open3'

# Usage check
if ARGV.length != 2
  puts "Usage: ruby normalize_audio.rb <source_dir> <destination_dir>"
  exit 1
end

src_dir = File.expand_path(ARGV[0])
dest_dir = File.expand_path(ARGV[1])

# Extract codec and bitrate from the audio stream of a .ts file
def get_audio_info(file_path)
  cmd = ["ffmpeg", "-i", file_path]
  _, stderr, _ = Open3.capture3(*cmd)

  audio_line = stderr.each_line.find { |line| line.include?("Audio:") }

  if audio_line
    codec = audio_line[/Audio:\s+([^\s,]+)/, 1] || "aac"
    bitrate_match = audio_line.match(/(\d+)\s*kb\/s/)
    bitrate = bitrate_match ? "#{bitrate_match[1]}k" : "128k"
    return codec, bitrate
  else
    return "aac", "128k"
  end
end

puts "🎵 Starting audio normalization with ffmpeg-normalize..."
puts "Source: #{src_dir}"
puts "Destination: #{dest_dir}"

Dir.glob("#{src_dir}/**/*.{ts,mkv}", File::FNM_CASEFOLD).each do |src_file|
  rel_path = src_file.sub(/^#{Regexp.escape(src_dir)}\/?/, "")
  dest_file = File.join(dest_dir, rel_path)
  dest_dir_path = File.dirname(dest_file)

  # Skip if output file already exists
  if File.exist?(dest_file)
    puts "⏭️  Skipping (already exists): #{dest_file}"
    next
  end

  puts "🔧 Processing: #{src_file}"
  puts "     Relative path: #{rel_path}"
  puts "     Output path:   #{dest_file}"

  FileUtils.mkdir_p(dest_dir_path)

  codec, bitrate = get_audio_info(src_file)
  puts "     Codec: #{codec}, Bitrate: #{bitrate}"

  # Build normalization command
  cmd = [
    "ffmpeg-normalize", src_file,
    "-c:a", codec,
    "-b:a", bitrate,
    "-c:v", "copy",
    "-o", dest_file,
    "--normalization-type", "ebu",
    "--dual-mono"
  ]

  puts "     Running: #{cmd.join(" ")}"

  system(*cmd) or abort("❌ ffmpeg-normalize failed for: #{src_file}")

  puts "✅ Done."
end

puts "🎉 All files normalized successfully."
