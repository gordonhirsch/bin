import os
import argparse
import shutil
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, ID3NoHeaderError
from PIL import Image, ImageCms
import io

print("✅ Script is loading...")

MAX_DIM = 600
MAX_SIZE_BYTES = 500 * 1024

def convert_image_to_jpeg(image_data, mime_type):
    image = Image.open(io.BytesIO(image_data))

    changes = {
        "resized": False,
        "converted_profile": False,
        "format_converted": mime_type == "image/png",
        "original_profile": "None",
        "final_size_kb": 0
    }

    if image.mode != "RGB":
        image = image.convert("RGB")

    if image.width > MAX_DIM or image.height > MAX_DIM:
        image.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)
        changes["resized"] = True

    icc_data = image.info.get("icc_profile")
    if icc_data:
        try:
            profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_data))
            changes["original_profile"] = ImageCms.getProfileName(profile)
        except Exception:
            changes["original_profile"] = "Unknown"
    else:
        changes["original_profile"] = "Missing"
        try:
            srgb_profile = ImageCms.createProfile("sRGB")
            image = ImageCms.profileToProfile(image, srgb_profile, srgb_profile)
            changes["converted_profile"] = True
        except Exception:
            pass

    output = io.BytesIO()
    image.save(output, format="JPEG", quality=85)
    jpeg_data = output.getvalue()
    changes["final_size_kb"] = len(jpeg_data) // 1024

    return jpeg_data, changes

def describe_changes(changes, force=False):
    lines = []
    if force:
        lines.append("✔️  Forcing re-embed of album art")
    if changes["format_converted"]:
        lines.append("✔️  Converted PNG → JPEG")
    if changes["resized"]:
        lines.append("✔️  Resized image to max 600x600")
    if changes["converted_profile"]:
        lines.append("✔️  Ensured sRGB color profile")
    lines.append(f"🖼️  Original color profile: {changes['original_profile']}")
    if changes["final_size_kb"] > (MAX_SIZE_BYTES // 1024):
        lines.append(f"⚠️  JPEG size is {changes['final_size_kb']} KB (over 500 KB)")
    if not force and not any(key for key in changes if key != "final_size_kb" and changes[key]):
        lines.append("✅ No changes needed")
    return lines

def process_mp3(input_path, output_path, dry_run=False, force=False):
    print(f"\n🎵 Processing: {input_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    shutil.copy(input_path, output_path)
    audio = MP3(output_path)
    if audio.tags is None:
        audio.add_tags()
    tags = audio.tags

    changed = False
    for frame in list(tags.getall("APIC")):
        jpeg_data, changes = convert_image_to_jpeg(frame.data, frame.mime)
        output_lines = describe_changes(changes, force=force)
        for line in output_lines:
            print(line)

        if any(key for key in changes if key != "final_size_kb" and changes[key]) or force:
            changed = True
            if not dry_run:
                tags.delall("APIC")
                tags.add(APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=3,  # front cover
                    desc="",
                    data=jpeg_data
                ))

    if changed and not dry_run:
        audio.save(v2_version=3)

def scan_directory(base_dir, output_dir, dry_run=False, force=False, incremental=False):
    for root, _, files in os.walk(base_dir):
        for name in files:
            full_path = Path(root) / name
            relative_path = full_path.relative_to(base_dir)
            output_path = Path(output_dir) / relative_path

            if incremental and output_path.exists():
                print(f"⏩ Skipping existing file: {output_path}")
                continue

            if name.lower().endswith(".mp3"):
                process_mp3(str(full_path), str(output_path), dry_run, force)

def main():
    parser = argparse.ArgumentParser(
        description="Fix album art in MP3 files: convert to JPEG, resize, and ensure sRGB profile."
    )
    parser.add_argument("directory", help="Directory to scan recursively")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--force", action="store_true", help="Force re-embed of album art even if valid")
    parser.add_argument("--output-dir", default="converted_output", help="Output directory for processed files")
    parser.add_argument("--incremental", action="store_true", help="Allow existing output directory and skip already processed files")
    args = parser.parse_args()

    if os.path.exists(args.output_dir) and not args.incremental:
        print(f"❌ Output directory already exists: {args.output_dir}")
        print("Please choose a different directory, remove the existing one, or use --incremental.")
        exit(1)

    scan_directory(args.directory, args.output_dir, args.dry_run, args.force, args.incremental)

if __name__ == "__main__":
    main()
