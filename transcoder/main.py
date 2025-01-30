import requests
import typer


def get_files(base_url):
    response = requests.get(f"{base_url}/files?limit=10000")
    response.raise_for_status()
    return response.json()


def filter_files(files):
    filtered_files = []
    for file in files:
        if file["video_codec"] == "h264":
            continue
        if any(audio["codec"] == "aac" for audio in file["audio_channels"]):
            continue
        if any(subtitle["codec"] == "srt" for subtitle in file["subtitle_channels"]):
            continue
        filtered_files.append(file)
    return filtered_files


def main(base_url, limit: int = 10):
    files = get_files(base_url)
    filtered_files = filter_files(files)
    for file in filtered_files[:limit]:
        print(file)


if __name__ == "__main__":
    typer.run(main)
