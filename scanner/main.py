import json
import os
import subprocess
import sys
from pathlib import Path

import requests


def get_file_info(file_path):
    try:
        file_info = {
            "filepath": str(file_path),
            "filename": file_path.name,
            "file_extension": file_path.suffix,
            "file_size": file_path.stat().st_size,
            "video_codec": None,
            "video_resolution": None,
            "audio_channels": [],
            "subtitle_channels": [],
        }

        # Run ffprobe to get detailed information about the file
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-print_format",
                "json",
                "-show_streams",
                str(file_path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        ffprobe_output = json.loads(result.stdout)

        for stream in ffprobe_output.get("streams", []):
            if stream["codec_type"] == "video":
                file_info["video_codec"] = stream.get("codec_name")
                file_info["video_resolution"] = (
                    f"{stream.get('width')}x{stream.get('height')}"
                )
            elif stream["codec_type"] == "audio":
                audio_channel = {
                    "channel": stream.get("tags", {}).get("language", "unknown"),
                    "codec": stream.get("codec_name"),
                }
                file_info["audio_channels"].append(audio_channel)
            elif stream["codec_type"] == "subtitle":
                subtitle_channel = {
                    "subtitle": stream.get("tags", {}).get("language", "unknown"),
                    "codec": stream.get("codec_name"),
                }
                file_info["subtitle_channels"].append(subtitle_channel)

    except FileNotFoundError:
        print(
            "ffprobe not found. Please ensure ffmpeg is installed and ffprobe is in your PATH."
        )
        return None
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

    return file_info


def scan_directory(directory, server_url, dry_run):
    media_extensions = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in media_extensions:
                file_info = get_file_info(file_path)
                if file_info is None:
                    continue
                if dry_run:
                    print(json.dumps(file_info, indent=4))
                else:
                    send_file_info_to_server(file_info, server_url)


def send_file_info_to_server(file_info, server_url):
    response = requests.post(f"{server_url}/files/", json=file_info)
    if response.status_code == 200:
        print(f"Successfully uploaded: {file_info['filename']}")
    else:
        print(
            f"Failed to upload: {file_info['filename']}. Status code: {response.status_code}, Response: {response.text}"
        )


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python main.py <folder> <fastapi_server_url> [--dry-run]")
        sys.exit(1)

    folder = sys.argv[1]
    fastapi_server_url = sys.argv[2]
    dry_run = "--dry-run" in sys.argv

    scan_directory(folder, fastapi_server_url, dry_run)
