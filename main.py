from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from sqlalchemy.orm import Session


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
from sql_app.tmx import TMXFile, Segment, AcceptedDomain, AcceptedLanguage
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

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
# db = SessionLocal()


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


def store_file(tmxfile: tmx.TMXFile, db: Session):
    db_tmxfile = crud.get_tmxfile_by_uuid(db, uuid_str=tmxfile.fileId)
    print(db_tmxfile)
    if db_tmxfile:
        return db_tmxfile.uuid_str
        # raise HTTPException(status_code=400, detail="File already in DB thanks")
    return crud.create_tmxfile(db=db, tmxfile=tmxfile)


async def processTMX(tmx: str, fileName: str, db: Session) -> TMXFile:
    # Parse the TMX file
    tree = ET.parse(tmx)
    root = tree.getroot()
    obj = {}
    # frpom fileName get domain add to each segment
    # AcceptedDomain
    # Extract the prop targetlang text
    target_lang = root.find('.//prop[@type="targetlang"]')
    # <prop type="name">German-Germany - English-United States for BMW Group - CA-601 ISTA</prop>
    if root.find('.//prop[@type="name"]'):
        obj["fileName"] = make_filename_friendly(
            root.find('.//prop[@type="name"]').text
        )  # name defDomain
    else:
        obj["fileName"] = "unknown"
    obj["fileVersion"] = root.attrib.get("version")
    obj["fileEncoding"] = root.attrib.get("encoding")
    fromFileId = str(uuid4())
    obj["fileId"] = fromFileId
    now_utc = datetime.now(timezone.utc)
    obj["dateAdded"] = now_utc
    the_units = []
    obj["segments"] = the_units
    obj["srcWordCount"] = 0
    obj["totalSegs"] = 0
    tmxo = TMXFile(**obj)
    res = store_file(tmxo, db)
    print(res.uuid_str)
    segCount = 0
    srcWordCount = 0
    pattern = re.compile(r"\w+")
    the_segments = []
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
        obj2["fromFileId"] = res.uuid_str
        obj2["segId"] = str(uuid4())
        obj2["seqNo"] = segCount
        # print(f"src_lang={src_lang}, src_count={segWordCount}, tar_lang={tar_lang}, src_text={src_text}, tar_text={tar_text}")
        obj2["srcLang"] = src_lang
        obj2["trgLang"] = tar_lang
        obj2["srcText"] = src_text
        obj2["trgText"] = tar_text
        obj2["srcWordCount"] = segWordCount
        obj2["cleanSrcText"] = clean_src_text
        obj2["cleanTrgText"] = clean_trg_text
        obj2["timestamp"] = current_timestamp

        sg = Segment(**obj2)
        the_segments.append(sg.__dict__)

        if (i + 1) % 1000 == 0:
            db.bulk_insert_mappings(Segment, the_segments)
            db.commit()
            the_segments = []

    if the_segments:
        db.bulk_insert_mappings(Segment, the_segments)
        db.commit()
        # store_segment(sg, db)
        # the_units.append(sg)
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
    the_tmx_file_obj = db.query(TMXFile).filter_by(uuid_str=res.uuid_str).first()
    if the_tmx_file_obj:
        the_tmx_file_obj["srcWordCount"] = srcWordCount
        the_tmx_file_obj["totalSegs"] = segCount
        db.commit()
    # create file object in DB

    # add fileObject UUID to each segment
    # obj["units"] = the_units

    return res


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


@app.get("/tmxs/", response_model=list[tmx.TMXFile])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    tmxfiles = crud.get_tmxfiles(db, skip=skip, limit=limit)
    return tmxfiles


# def store_file(file_object:TMXFile):


async def storeTMX(
    clientId: str, domains: List[AcceptedDomain], file: UploadFile, db: Session
):
    contents = await file.read()  # bytes object
    contents_str = contents.decode("utf-8")
    contents_bytes = contents_str.encode("utf-8")
    fileobj = io.BytesIO(contents_bytes)
    file_size_kb = len(contents) / (1024)
    wordCount = 0
    # domains: List[AcceptedDomain] = []
    # create file db here

    # what kind of file is it? call tjat function
    filename_without_extension = os.path.splitext(file.filename)[0]
    fileName = filename_without_extension
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension == ".tmx":
        # write file to DB return ID
        res = await processTMX(fileobj, fileName, db)


@app.post("/tmxs/")
async def store_tmx(
    clientId: str,
    domains: List[AcceptedDomain],
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await storeTMX(clientId, domains, file, db)

    # res2 = create_tmxfile(res)  # deals with already created
    # create segms res2.units
    # create segments and add?
    # return res
