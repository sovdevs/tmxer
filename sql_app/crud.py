from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text
from . import models, tmx
from uuid import UUID, uuid4


# how to index a file?
def create_tmxfile(tmxfile: tmx.TMXFile, db: Session):
    db_tmxfile = models.TMXFile(
        uuid_str=tmxfile.fileId,
        fileVersion=tmxfile.fileVersion,
        fileName=tmxfile.fileName,
        dateAdded=tmxfile.dateAdded,
        srcWordCount=tmxfile.srcWordCount,
        totalSegs=tmxfile.totalSegs,
    )
    print(db_tmxfile.uuid_str)
    db.add(db_tmxfile)
    db.commit()
    db.refresh(db_tmxfile)
    print(db_tmxfile.uuid_str)
    return db_tmxfile


def get_tmxfile_by_uuid(db: Session, uuid_str: str):
    return db.query(models.TMXFile).filter(models.TMXFile.uuid_str == uuid_str).first()


# def get_tmxfile_by_uuid(db: Session, uuid_str: str):
#     uuid_value = UUID(uuid_str)
#     hex_value = str(uuid_value)
#     hex_value = hex_value.replace("urn:", "").replace("uuid:", "")
#     return db.query(models.TMXFile).filter(models.TMXFile.uuid == hex_value).first()


def get_tmxfiles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TMXFile).offset(skip).limit(limit).all()
