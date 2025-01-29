from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from src.crud import create_file, delete_file, get_file, get_files
from src.database import get_session
from src.models import AudioChannel, File, SubtitleChannel
from src.schemas import FileCreate, FileRead

file_router = APIRouter()


@file_router.post("/", response_model=FileRead)
def create_new_file(file: FileCreate, session: Session = Depends(get_session)):
    db_file = File(
        filepath=file.filepath,
        filename=file.filename,
        file_extension=file.file_extension,
        file_size=file.file_size,
        video_codec=file.video_codec,
        video_resolution=file.video_resolution,
        audio_channels=[
            AudioChannel(channel=audio.channel, codec=audio.codec)
            for audio in file.audio_channels
        ]
        if file.audio_channels
        else [],
        subtitle_channels=[
            SubtitleChannel(subtitle=subtitle.subtitle, codec=subtitle.codec)
            for subtitle in file.subtitle_channels
        ]
        if file.subtitle_channels
        else [],
    )
    return create_file(session, db_file)


@file_router.get("/{file_id}", response_model=FileRead)
def read_file(file_id: int, session: Session = Depends(get_session)):
    file = get_file(session, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file


@file_router.get("/", response_model=list[FileRead])
def read_files(skip: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    return get_files(session, skip=skip, limit=limit)


@file_router.delete("/{file_id}", response_model=bool)
def delete_existing_file(file_id: int, session: Session = Depends(get_session)):
    return delete_file(session, file_id)
