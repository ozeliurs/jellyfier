from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class AudioChannel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file_id: Optional[int] = Field(default=None, foreign_key="file.id")
    name: str  # Add this line
    channel: str
    codec: str
    file: Optional["File"] = Relationship(back_populates="audio_channels")


class SubtitleChannel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file_id: Optional[int] = Field(default=None, foreign_key="file.id")
    name: str  # Add this line
    subtitle: str
    codec: str
    file: Optional["File"] = Relationship(back_populates="subtitle_channels")


class File(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filepath: str
    filename: str
    file_extension: str
    file_size: int
    video_codec: Optional[str] = None
    video_resolution: Optional[str] = None
    audio_channels: List[AudioChannel] = Relationship(back_populates="file")
    subtitle_channels: List[SubtitleChannel] = Relationship(back_populates="file")
