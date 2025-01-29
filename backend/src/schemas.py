from typing import List, Optional

from sqlmodel import SQLModel


class AudioChannelCreate(SQLModel):
    name: str  # Add this line
    channel: str
    codec: str


class SubtitleChannelCreate(SQLModel):
    name: str  # Add this line
    subtitle: str
    codec: str


class AudioChannelRead(SQLModel):
    id: int
    name: str  # Add this line
    channel: str
    codec: str


class SubtitleChannelRead(SQLModel):
    id: int
    name: str  # Add this line
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


class FileRead(SQLModel):
    id: int
    filepath: str
    filename: str
    file_extension: str
    file_size: int
    video_codec: Optional[str] = None
    video_resolution: Optional[str] = None
    audio_channels: List[AudioChannelRead] = []
    subtitle_channels: List[SubtitleChannelRead] = []
