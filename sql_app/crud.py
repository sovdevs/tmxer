from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text
from . import models, tmx
from uuid import UUID, uuid4, uuid5, NAMESPACE_DNS
from datetime import datetime, timezone

"""
UUIDS for bothSegmentsand Files
"""


def generate_uuid(file_name: str) -> str:
    # Get the current timestamp
    current_time = datetime.now()

    # Concatenate the file name and timestamp as a string
    input_string = f"{file_name}{current_time}"

    # Generate a UUID from the input string
    generated_uuid = uuid5(NAMESPACE_DNS, input_string)

    # Return the UUID as a string
    return str(generated_uuid)


"""
TMX FILE
"""


def update_tmxfile_with_segment_info(tmxfile: tmx.TMXFile, db: Session):
    db_tmxfile = get_tmxfile_by_uuid(db, uuid_str=tmxfile.fileId)
    db_tmxfile = models.TMXFile(
        srcWordCount=tmxfile.srcWordCount,
        totalSegs=tmxfile.totalSegs,
    )
    db.commit()
    return db_tmxfile.uuid_str


def create_or_update_tmxfile(tmxfile: tmx.TMXFile, db: Session):
    db_tmxfile = (
        db.query(models.TMXFile)
        .filter(
            models.TMXFile.fileName == tmxfile.fileName,
            models.TMXFile.clientId == tmxfile.clientId,
        )
        .first()
    )
    if db_tmxfile:
        # update instead
        db_tmxfile.dateUpdated = (datetime.now(timezone.utc),)
        db_tmxfile.srcWordCount = tmxfile.srcWordCount
        db_tmxfile.totalSegs = tmxfile.totalSegs
        db.commit()
    else:
        # new has no segment info yet
        db_tmxfile = models.TMXFile(
            uuid_str=generate_uuid(tmxfile.fileName),
            fileVersion=tmxfile.fileVersion,
            fileName=tmxfile.fileName,
            clientId=tmxfile.clientId,
            dateAdded=datetime.now(timezone.utc),
            dateUpdated=datetime.now(timezone.utc),
        )
        db.add(db_tmxfile)
        db.commit()
        db.refresh(db_tmxfile)
    return db_tmxfile.uuid_str


def get_tmxfile_by_uuid(db: Session, uuid_str: str):
    res = db.query(models.TMXFile).filter(models.TMXFile.uuid_str == uuid_str).first()
    print(uuid_str, res)
    return res


def get_tmxfiles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TMXFile).offset(skip).limit(limit).all()


"""
CATEGORIES
"""


def create_categories(db: Session, categories: list[str]):
    existing_categories = (
        db.query(models.AcceptedCategory)
        .filter(models.AcceptedCategory.category.in_(categories))
        .all()
    )
    print(f"existing> {existing_categories}")
    categories_to_add = [
        cat
        for cat in categories
        if cat not in [existing.category for existing in existing_categories]
    ]

    accepted_categories = [
        models.AcceptedCategory(category=cat) for cat in categories_to_add
    ]
    print(f" accepted_categories > { accepted_categories }")
    db.add_all(accepted_categories)
    db.commit()
    # db.refresh(accepted_categories)

    category_ids = [
        category.id for category in existing_categories + accepted_categories
    ]
    print(f" newly accepted_category ids > { category_ids}")
    return category_ids


"""
SEGMENT
"""
