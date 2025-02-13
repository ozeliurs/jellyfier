import json
import os
import shutil
import subprocess
import threading
from pathlib import Path

import requests
import typer
from rich import print
from rich.progress import Progress

config_path = Path.home() / ".jellyfier"
temp_transcode_path = Path("/tmp/jellyfier_transcode")
temp_transcode_path.mkdir(exist_ok=True)

app = typer.Typer()

# ========== Config ==========


@app.command()
def set(key: str, value: str):
    print(f"🔧 Setting {key}={value}")

    if not config_path.exists():
        config_path.touch()

    with open(config_path, "a") as config_file:
        config_file.write(f"{key}={value}\n")


def get(key: str) -> str:
    if not config_path.exists():
        print("⚠️ No configuration found")
        raise typer.Exit()

    with open(config_path) as config_file:
        for line in config_file:
            if line.startswith(key):
                return line.split("=")[1].strip()

    raise KeyError(
        f"⚠️ Configuration for {key} not found. Run `jellyfier set {key} <value>`"
    )


# ========== Scanner ==========


@app.command()
def scan(path: Path, server_url: str | None = None, dry_run: bool = False):
    if server_url is None:
        server_url = get("server_url")

    print(f"🔍 Scanning {path}")

    media_extensions = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}
    for root, _, files in os.walk(path):
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
                    "name": stream.get("tags", {}).get("title", "unknown"),
                    "channel": stream.get("tags", {}).get("language", "unknown"),
                    "codec": stream.get("codec_name"),
                }
                file_info["audio_channels"].append(audio_channel)
            elif stream["codec_type"] == "subtitle":
                subtitle_channel = {
                    "name": stream.get("tags", {}).get("title", "unknown"),
                    "subtitle": stream.get("tags", {}).get("language", "unknown"),
                    "codec": stream.get("codec_name"),
                }
                file_info["subtitle_channels"].append(subtitle_channel)

    except FileNotFoundError:
        print(
            "⚠️ ffprobe not found. Please ensure ffmpeg is installed and ffprobe is in your PATH."
        )
        return None
    except Exception as e:
        print(f"⚠️ Error processing file {file_path}: {e}")
        return None

    return file_info


def send_file_info_to_server(file_info, server_url):
    response = requests.post(f"{server_url}/files/", json=file_info)
    if response.status_code == 200:
        print(f"✅ Successfully uploaded: {file_info['filename']}")
    else:
        print(
            f"❌ Failed to upload: {file_info['filename']}. Status code: {response.status_code}, Response: {response.text}"
        )


# ========== Stats ==========


def get_files(base_url):
    response = requests.get(f"{base_url}/files?limit=10000")
    response.raise_for_status()
    return response.json()


def human_readable_size(size, decimal_places=2):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.{decimal_places}f} {unit}"
        size /= 1024


@app.command()
def large(server_url: str | None = None):
    if server_url is None:
        server_url = get("server_url")

    files = get_files(server_url)

    # Sort files by size
    sorted_files = sorted(files, key=lambda x: x["file_size"], reverse=True)

    # Get the largest file
    largest_file = sorted_files[0]
    print(
        f"\n📦 Largest file: {largest_file['filename']} ({human_readable_size(largest_file['file_size'])})"
    )

    # Find files within 1GB of the largest
    gb_in_bytes = 1024 * 1024 * 1024
    similar_size_files = [
        f
        for f in sorted_files[1:]
        if abs(f["file_size"] - largest_file["file_size"]) <= gb_in_bytes
    ]

    if similar_size_files:
        print("\n📋 Files within 1GB of largest:")
        for file in similar_size_files:
            print(f"- {file['filename']} ({human_readable_size(file['file_size'])})")
    else:
        print("\nNo other files within 1GB of largest file")


@app.command()
def stats(server_url: str | None = None):
    if server_url is None:
        server_url = get("server_url")

    files = get_files(server_url)
    total_files = len(files)
    total_size = sum(file["file_size"] for file in files)

    print("📊 ==== File Stats ====")
    print(f"📁 Total files scanned: {total_files}")
    print(f"💾 Total size of all files: {human_readable_size(total_size)}")

    # Calculate the proportion of files needing transcoding
    files_needing_transcoding = filter_files(files)
    percent_needing_transcoding = round(
        (len(files_needing_transcoding) / total_files) * 100
    )

    with Progress() as progress:
        progress.add_task(
            "[cyan]Percent of files needing transcoding",
            total=100,
            completed=percent_needing_transcoding,
        )

    # Calculate the proportion of video codecs
    print("\n🎥 ==== Video Codecs ====")
    codec_counts = {}
    for file in files:
        codec = file["video_codec"]
        if codec:
            codec_counts[codec] = codec_counts.get(codec, 0) + 1

    # Display progress bars for video codecs
    with Progress() as progress:
        for codec, count in codec_counts.items():
            progress.add_task(f"[cyan]{codec}", total=total_files, completed=count)

    print("\n🔊 ==== Audio Codecs ====")
    audio_codec_counts = {}
    for file in files:
        for audio_channel in file["audio_channels"]:
            codec = audio_channel["codec"]
            audio_codec_counts[codec] = audio_codec_counts.get(codec, 0) + 1

    total_audios = sum(audio_codec_counts.values())

    with Progress() as progress:
        for codec, count in audio_codec_counts.items():
            progress.add_task(f"[cyan]{codec}", total=total_audios, completed=count)

    print("\n💬 ==== Subtitle Codecs ====")
    subtitle_codec_counts = {}
    for file in files:
        for subtitle_channel in file["subtitle_channels"]:
            codec = subtitle_channel["codec"]
            subtitle_codec_counts[codec] = subtitle_codec_counts.get(codec, 0) + 1

    total_subtitles = sum(subtitle_codec_counts.values())

    with Progress() as progress:
        for codec, count in subtitle_codec_counts.items():
            progress.add_task(f"[cyan]{codec}", total=total_subtitles, completed=count)


# ========== Problems ==========


@app.command()
def problems(server_url: str | None = None):
    if server_url is None:
        server_url = get("server_url")

    files = get_files(server_url)
    pgs_files = []
    for file in files:
        if any(
            [sub["codec"] == "hdmv_pgs_subtitle" for sub in file["subtitle_channels"]]
        ):
            pgs_files.append(file)

    print(f"\n⚠️ Found {len(pgs_files)} files with PGS subtitles:")
    for file in pgs_files:
        print(file_to_string(file))


# ========== Transcoder ==========


def filter_files(files):
    filtered_files = []
    for file in files:
        if any(
            [sub["codec"] == "hdmv_pgs_subtitle" for sub in file["subtitle_channels"]]
        ):
            continue

        if file["video_codec"] != "h264":
            filtered_files.append(file)
            continue

        if len(file["audio_channels"]) > 0 and not all(
            audio["codec"] in ["aac", "flac"] for audio in file["audio_channels"]
        ):
            filtered_files.append(file)
            continue

        if len(file["subtitle_channels"]) > 0 and not all(
            subtitle["codec"] in ["srt", "ass", "subrip"]
            for subtitle in file["subtitle_channels"]
        ):
            filtered_files.append(file)
            continue

    return filtered_files


def file_to_string(file):
    audio_str = ", ".join(
        f"{audio['channel']} ({audio['codec']})" for audio in file["audio_channels"]
    )
    subtitle_str = ", ".join(
        f"{subtitle['subtitle']} ({subtitle['codec']})"
        for subtitle in file["subtitle_channels"]
    )
    return f"{file['id']}. {file['filename']} - {file['video_codec']}{' - ' if audio_str != '' else ''}{audio_str}{' - ' if subtitle_str != '' else ''}{subtitle_str}"


def transcode_file(file):
    """Runs ffmpeg -i input.mkv -c:v libx264 -pix_fmt yuv420p -c:a aac -c:s srt output.mkv"""
    output_file = file.with_suffix(".jellyfied.mkv")

    print(f"🎬 Transcoding {file}")

    command = [
        "ffmpeg",
        "-i",
        file,
        "-map",
        "0",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-c:s",
        "srt",
        output_file,
    ]

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3600
    )

    if result.returncode == 0:
        print(f"✅ Transcoded {file} to {output_file}")
    else:
        print(f"❌ Failed to transcode {file}: {result.stderr}")


def delete_file(file, server_url):
    response = requests.delete(f"{server_url}/files/{file['id']}")
    if response.status_code == 200:
        print(f"🗑️ Successfully deleted: {file['filename']}")
    else:
        print(
            f"❌ Failed to delete: {file['filename']}. Status code: {response.status_code}, Response: {response.text}"
        )


@app.command()
def transcode(
    server_url: str | None = None, count: int = 1, delete_after: bool = False
):
    if server_url is None:
        server_url = get("server_url")

    files = get_files(server_url)
    filtered_files = filter_files(files)

    if count == 0:
        files_to_transcode = filtered_files
    else:
        files_to_transcode = filtered_files[:count]

    print(f"⚙️ You are about to transcode {len(files_to_transcode)} files")
    for file in files_to_transcode:
        print(file_to_string(file))

    if typer.confirm("Do you want to continue?"):
        total_files = len(files_to_transcode)
        threads = []

        with Progress() as progress:
            task_transcode = progress.add_task(
                "[cyan]Transcoding...", total=total_files
            )
            task_transfer = progress.add_task(
                "[green]Transferring...", total=total_files
            )

            for o_file in files_to_transcode:
                file = Path(o_file["filepath"])

                # Copy the file to a temporary location
                temp_file = temp_transcode_path / file.name
                print(
                    f"📂 Making temporary copy of [blue]{file}[/blue] at [red]{temp_file}[/red]"
                )
                shutil.copy(file, temp_file)

                # Transcode the file
                transcode_file(temp_file)
                progress.update(task_transcode, advance=1)

                # Start post-transcoding operations in a separate thread
                thread = threading.Thread(
                    target=post_transcode_operations,
                    args=(
                        temp_file,
                        file,
                        o_file,
                        server_url,
                        delete_after,
                        progress,
                        task_transfer,
                    ),
                )
                thread.start()
                threads.append(thread)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()


def post_transcode_operations(
    temp_file, file, o_file, server_url, delete_after, progress, task_transfer
):
    """Handle all operations after transcoding in a separate thread"""
    # Delete the temporary file
    print(f"🗑️ Deleting [red]{temp_file}[/red]")
    temp_file.unlink()

    # Check transcoded file exists and is not empty
    temp_transcoded_file = temp_file.with_suffix(".jellyfied.mkv")
    if not temp_transcoded_file.exists() or temp_transcoded_file.stat().st_size == 0:
        print(
            f"❌ Transcoding failed for [blue]{file}[/blue] - output file is empty or missing"
        )
        if temp_transcoded_file.exists():
            temp_transcoded_file.unlink()
        progress.update(task_transfer, advance=1)
        delete_file(o_file, server_url)
        return

    transcoded_file = file.with_suffix(temp_transcoded_file.suffix)

    # Move file to file.old
    if delete_after:
        print(f"🗑️ Deleting [blue]{file}[/blue]")
        file.unlink()
    else:
        old_file = file.with_suffix(f"{file.suffix}.old")
        print(f"🔄 Renaming [blue]{file}[/blue] to [blue]{old_file}[/blue]")
        file.rename(old_file)

    print(
        f"📂 Copying [red]{temp_transcoded_file}[/red] to [blue]{transcoded_file}[/blue]"
    )
    shutil.copy(temp_transcoded_file, transcoded_file)
    print(f"🗑️ Deleting [red]{temp_transcoded_file}[/red]")
    temp_transcoded_file.unlink()

    # Delete the file from the server
    delete_file(o_file, server_url)

    # Update transfer progress
    progress.update(task_transfer, advance=1)


@app.command()
def delete(id: str, server_url: str | None = None):
    if server_url is None:
        server_url = get("server_url")

    if id == "all":
        if typer.confirm(
            "Are you sure you want to delete all files from the http server?"
        ):
            files = get_files(server_url)
            for file in files:
                delete_file(file, server_url)
        return

    response = requests.delete(f"{server_url}/files/{id}")
    if response.status_code == 200:
        print(f"🗑️ Successfully deleted file with ID {id}")
    else:
        print(
            f"❌ Failed to delete file with ID {id}. Status code: {response.status_code}, Response: {response.text}"
        )


@app.command()
def rollback(path: Path, dry_run: bool = True):
    """Find all empty .mkv files and restore their .old versions if available"""
    file_count = 0
    empty_files_found = 0
    restored_count = 0

    for root, _, files in os.walk(path):
        for file in files:
            file_count += 1
            file_path = Path(root) / file

            # Check for empty .mkv files
            if file_path.suffix.lower() == ".mkv" and file_path.stat().st_size == 0:
                empty_files_found += 1
                old_file = file_path.with_suffix(file_path.suffix + ".old")

                if old_file.exists():
                    print(
                        f"Found empty file: [blue]{file_path}[/blue] ({file_path.stat().st_size} bytes)"
                    )
                    print(
                        f"🗑️ {'Would delete' if dry_run else 'Deleting'} empty file [blue]{file_path}[/blue]"
                    )
                    print(
                        f"🔄 {'Would restore' if dry_run else 'Restoring'} [blue]{old_file}[/blue] to [blue]{file_path}[/blue]"
                    )

                    if not dry_run:
                        file_path.unlink()  # Delete empty file
                        old_file.rename(file_path)  # Restore .old file
                        restored_count += 1
                else:
                    print(
                        f"⚠️ Found empty file but no .old version: [blue]{file_path}[/blue]"
                    )

    print("\n📊 Summary:")
    print(f"Scanned: {file_count} files")
    print(f"Found: {empty_files_found} empty files")
    print(f"Restored: {restored_count} files")
    if dry_run:
        print(
            "\nThis was a dry run. Use --no-dry-run to actually perform the operations."
        )


if __name__ == "__main__":
    app()
