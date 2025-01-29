from sqlmodel import Session, select

from src.models import File


def create_file(session: Session, file: File):
    session.add(file)
    session.commit()
    session.refresh(file)
    return file


def get_file(session: Session, file_id: int):
    return session.get(File, file_id)


def get_files(session: Session, skip: int = 0, limit: int = 10):
    return session.exec(select(File).offset(skip).limit(limit)).all()


def delete_file(session: Session, file_id: int):
    file = session.get(File, file_id)
    if file:
        session.delete(file)
        session.commit()
        return True
    return False
