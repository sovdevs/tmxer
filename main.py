from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import ValidationError

# from db_config.sqlalchemy_async_connect import AsynSessionFactory
# from models.requests.xliff import XLIFF, Unit, Segment, Note
# from models.requests.yandex import (
#     YandexInput,
#     YandexInputOutput,
#     GlossaryData,
#     GlossaryConfig,
#     GlossaryPair,
#     AcceptedLanguage,
# )
from sql_app.tmx import TMXFile, Segment, AcceptedLanguage
from utilities import get_timestamp, make_filename_friendly
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from xml.etree import ElementInclude
from typing import List, Union
from uuid import UUID, uuid4
import os
import io
import re
from rich import print
from sql_app import crud, models, tmx
from sql_app.database import SessionLocal, engine, get_db
from uuid import UUID, uuid4, uuid5, NAMESPACE_DNS

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
# db = SessionLocal()


def add_association(db: Session, category_ids: List[int], segment_id: str):
    association_values = [
        {"category_id": category_id, "segment_id": segment_id}
        for category_id in category_ids
    ]
    db.execute(models.segment_categories.insert().values(association_values))
    db.commit()


def add_categories(db: Session, categories: list[str]) -> list[int]:
    existing_categories = (
        db.query(models.AcceptedCategory)
        .filter(models.AcceptedCategory.category.in_(categories))
        .all()
    )
    print(existing_categories)
    # categories_to_add = [
    #     cat
    #     for cat in categories
    #     if cat not in [existing.category for existing in existing_categories]
    # ]
    # accepted_categories = [
    #     models.AcceptedCategory(category=cat) for cat in categories_to_add
    # ]
    # db.add_all(accepted_categories)
    # db.commit()
    # db.refresh(accepted_categories)

    # category_ids = [
    #     category.id for category in existing_categories + accepted_categories
    # ]
    # return category_ids


def add_languages(db: Session):
    languages = ["en", "de", "ru", "fr", "ro"]
    existing_languages = (
        db.query(models.AcceptedLanguage)
        .filter(models.AcceptedLanguage.language.in_(languages))
        .all()
    )
    languages_to_add = [
        lang
        for lang in languages
        if lang not in [existing.language for existing in existing_languages]
    ]
    accepted_languages = [
        models.AcceptedLanguage(language=lang) for lang in languages_to_add
    ]

    db.add_all(accepted_languages)
    db.commit()


@app.on_event("startup")
async def startup_event():
    db = next(get_db())  # Assuming get_db returns an async generator next to get one
    add_languages(db)


# def add_domains(db: Session):

#     domains = [
#         medical = "medical"
#         legal = "legal"
#         lw_corporate = "lw_corporate"
#         lw_aftersales = "lw_aftersales"
#         # Add more domains as needed
#     ]

#     accepted_domains = [AcceptedDomain(domain=dom) for dom in domains]

#     db.add_all(accepted_domains)
#     db.commit()

# Dependency


# def create_tmxfile(tmxfile: tmx.TMXFile):
#     # db_tmxfile = (
#     #     session.query(models.TMXFile)
#     #     .filter(models.TMXFile.uuid == tmxfile.fileId)
#     #     .first()
#     # )
#     db_tmxfile = crud.get_tmxfile_by_uuid(db, uuid_str=tmxfile.fileId)
#     if db_tmxfile:
#         raise HTTPException(status_code=400, detail="File already in DB thanks")
#     return crud.create_tmxfile(db=db, tmxfile=tmxfile)
def store_segment(segment: tmx.Segment, db: Session):
    db_segment = models.Segment(
        fromFileId=segment.fromFileId,
        segId=segment.segId,
        seqNo=segment.seqNo,
        srcLang=segment.srcLang,
        trgLang=segment.trgLang,
        srcText=segment.srcText,
        cleanSrcText=segment.cleanSrcText,
        trgText=segment.trgText,
        cleanTrgText=segment.cleanTrgText,
        segNote=segment.segNote,
        srcWordCount=segment.srcWordCount,
        timestamp=segment.timestamp,
    )
    db.add(db_segment)
    db.commit()
    db.refresh(db_segment)
    return db_segment


# def create_file(tmxfile: tmx.TMXFile, db: Session):


# def store_or_update_file(tmxfile: tmx.TMXFile, db: Session):
#     db_tmxfile = crud.get_tmxfile_by_uuid(db, uuid_str=tmxfile.fileId)
#     if db_tmxfile:
#         db_tmxfile.fileVersion = tmxfile.fileVersion
#         db_tmxfile.fileName = tmxfile.fileName
#         db_tmxfile.dateAdded = tmxfile.dateAdded
#         db.commit()
#         return db_tmxfile.uuid_str
#     else:
#         # raise HTTPException(status_code=400, detail="File already in DB thanks")
#         return crud.create_tmxfile(db=db, tmxfile=tmxfile)


async def processTMX(
    tmx: str, clientId: str, categories: List[str], fileName: str, db: Session
) -> TMXFile:
    # Parse the TMX file
    tree = ET.parse(tmx)
    root = tree.getroot()
    file_obj = {}
    # frpom fileName get domain add to each segment
    # AcceptedDomain
    # Extract the prop targetlang text
    # target_lang = root.find('.//prop[@type="targetlang"]')
    # <prop type="name">German-Germany - English-United States for BMW Group - CA-601 ISTA</prop>
    file_obj["fileName"] = fileName
    file_obj["fileVersion"] = root.attrib.get("version")
    # file_obj["fileEncoding"] = root.attrib.get("encoding")
    # fromFileId = str(uuid4())

    file_obj["fileId"] = ""
    file_obj["clientId"] = clientId
    now_utc = datetime.now(timezone.utc)
    file_obj["dateAdded"] = now_utc
    the_units = []
    file_obj["segments"] = the_units
    file_obj["srcWordCount"] = 0
    file_obj["totalSegs"] = 0
    tmxfile = TMXFile(**file_obj)
    print(tmxfile)
    file_id = crud.create_or_update_tmxfile(db=db, tmxfile=tmxfile)
    print(file_id)
    # category_ids = add_categories(db, categories)

    segCount = 0
    srcWordCount = 0
    pattern = re.compile(r"\w+")

    for i, tu in enumerate(root.findall(".//tu")):
        obj2 = {}
        segWordCount = 0
        src_lang = tu.find("./tuv[1]").attrib[
            "{http://www.w3.org/XML/1998/namespace}lang"
        ]
        tar_lang = tu.find("./tuv[2]").attrib[
            "{http://www.w3.org/XML/1998/namespace}lang"
        ]
        src_text = ""
        clean_src_text = ""
        src_tags = []
        for child in tu.find("./tuv[1]/seg").iter():
            if child.tag in ("bpt", "ept", "ph", "it", "sc"):
                src_tags.append(ET.tostring(child, encoding="unicode"))
            elif child.text:
                src_text += child.text.strip()
                segWordCount = len(re.findall(pattern, src_text))
                srcWordCount += segWordCount
                segCount = segCount + 1
                obj2["seqid"] = segCount
        clean_src_text = src_text
        src_text = " ".join([src_text] + src_tags)
        tar_text = ""
        tar_tags = []
        for child in tu.find("./tuv[2]/seg").iter():
            if child.tag in ("bpt", "ept", "ph", "it", "sc"):
                tar_tags.append(ET.tostring(child, encoding="unicode"))
            elif child.text:
                tar_text += child.text.strip()
        tar_text = " ".join([tar_text] + tar_tags)
        clean_trg_text = tar_text
        current_timestamp = get_timestamp()
        # src_text_elem = tu.find("./tuv[1]/seg")
        # if src_text_elem.text is not None:
        #     src_text = src_text_elem.text.strip()
        #     # count words
        #     count = len(re.findall(pattern, src_text))
        #     wordCount += count
        # else:
        #     src_text = src_text_elem
        # tgt_text_elem = tu.find("./tuv[2]/seg")
        # if tgt_text_elem.text is not None:
        #     tgt_text = tgt_text_elem.text.strip()
        # else:
        #     tgt_text = tgt_text_elem

        ## create Segment
        obj2["fromFileId"] = file_id
        obj2["segId"] = str(uuid4())
        obj2["seqNo"] = segCount
        # print(f"src_lang={src_lang}, src_count={segWordCount}, tar_lang={tar_lang}, src_text={src_text}, tar_text={tar_text}")
        obj2["srcLang"] = src_lang
        obj2["trgLang"] = tar_lang
        # print(f"{src_lang}, {tar_lang}")
        obj2["srcText"] = src_text
        obj2["trgText"] = tar_text
        obj2["srcWordCount"] = segWordCount
        obj2["cleanSrcText"] = clean_src_text
        obj2["cleanTrgText"] = clean_trg_text
        obj2["timestamp"] = current_timestamp
        # sg = Segment(**obj2)
        # the_segments.append(sg)
        # segment = store_segment(sg, db)
        # add_association(category_ids, segment.segId)

        # the_units.append(sg)

        # get segid

    #     if (i + 1) % 1000 == 0:
    #         db.bulk_insert_mappings(Segment, the_segments)
    #         db.commit()
    #         the_segments = []

    # if the_segments:
    #     db.bulk_insert_mappings(Segment, the_segments)
    #     db.commit()

    # print(sg)
    # print(sg)
    #
    # for tuv in tu.findall('.//tuv'):
    #     lang = tuv.get('{http://www.w3.org/XML/1998/namespace}lang')
    #     if count ==0:
    #         obj['srcLang'] = lang
    #         count +=1
    #     if count ==1:
    #         obj['tarLang'] = lang
    #         count -=1
    #     seg = tuv.find('seg')
    #     if lang is not None and seg is not None:
    #         if  count ==0:
    #             obj['srcContent'] = seg.text
    #             print(lang, seg.text)
    #         elif count==1:
    #             obj['tarContent'] = seg.text
    #             print(lang, seg.text)
    #         else:
    #             obj['undefined'] = seg.text
    #             print(lang, seg.text)

    # create
    #  update TMXFILE object
    # the_tmx_file_obj = db.query(TMXFile).filter_by(uuid_str=res.uuid_str).first()
    # if the_tmx_file_obj:
    #     the_tmx_file_obj["srcWordCount"] = srcWordCount
    #     the_tmx_file_obj["totalSegs"] = segCount
    #     db.commit()
    # create file object in DB

    # add fileObject UUID to each segment
    # obj["units"] = the_units

    return tmxfile


@app.get("/")
async def read_root():
    return {"Hello": "World"}


# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


# @app.get("/tmxs/{tmxfile_uuid}", response_model=tmx.TMXFile)
# def read_txmfile(file_id: str):
#     db_tmxfile = crud.get_tmxfile(db, uuid=tmxfile_uuid)
#     if db_tmxfile is None:
#         raise HTTPException(status_code=404, detail="TMXFILE not found")
#     return db_tmxfile


# @app.get("/tmxs/", response_model=list[tmx.TMXFile])
# def read_users(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
# ):
#     tmxfiles = crud.get_tmxfiles(db, skip=skip, limit=limit)
#     return tmxfiles


# def store_file(file_object:TMXFile):


async def storeTMX(clientId: str, categories: List[str], file: UploadFile, db: Session):
    contents = await file.read()  # bytes object
    contents_str = contents.decode("utf-8")
    contents_bytes = contents_str.encode("utf-8")
    fileobj = io.BytesIO(contents_bytes)
    file_size_kb = len(contents) / (1024)
    wordCount = 0
    # what kind of file is it? call tjat function
    filename_without_extension = os.path.splitext(file.filename)[0]
    fileName = filename_without_extension
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension == ".tmx":
        # write file to DB return ID
        res = await processTMX(fileobj, clientId, categories, fileName, db)


# Entry Point for TMX -> DB
@app.post("/tmxs/")
async def store_tmx(
    clientId: str,
    categories: List[str],
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await storeTMX(clientId, categories, file, db)

    # res2 = create_tmxfile(res)  # deals with already created
    # create segms res2.units
    # create segments and add?
    # return res
