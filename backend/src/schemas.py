from typing import List, Optional

from sqlmodel import SQLModel


class AudioChannelCreate(SQLModel):
    channel: str
    codec: str


class SubtitleChannelCreate(SQLModel):
    subtitle: str
    codec: str


class FileCreate(SQLModel):
    filepath: str
    filename: str
    file_extension: str
    file_size: int
    video_codec: Optional[str] = None
    video_resolution: Optional[str] = None
    audio_channels: Optional[List[AudioChannelCreate]] = []
    subtitle_channels: Optional[List[SubtitleChannelCreate]] = []
