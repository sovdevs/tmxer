from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import date, datetime


# Now create Pydantic models (schemas) that will be used when reading data, when returning it from the API.
## should have API to clean up TMX ie remove duplocates remove EASY low informational content segments
# class AcceptedDomain(str, Enum):
#     medical = "medical"
#     legal = "legal"
#     lw_corporate = "lw_corporate"
#     lw_aftersales = "lw_aftersales"


# class FileType(str, Enum):
#     tmx = "tmx"
#     xliff = "xliff"
#     sdlxliff = "sdlxliff"
#     csv = "csv"
#     po = "po"


class AcceptedLanguage(str, Enum):
    en = "en"
    de = "de"
    ru = "ru"
    fr = "fr"
    ro = "ro"
    enUS = "en-US"
    enGB = "en-GB"
    deDE = "de-DE"

    @classmethod
    def get_language_code(cls, language):
        if language.lower() in ["de-de", "de-de"]:
            return cls.deDE
        return cls[language]


# segments matter index db (srcText, trgText, timestamp)
class Segment(BaseModel):
    fromFileId: str
    segId: str
    seqNo: int
    categories: List[str] = []
    srcLang: AcceptedLanguage
    trgLang: AcceptedLanguage
    srcText: str  # indexed?
    cleanSrcText: str  # no tags
    trgText: str
    cleanTrgText: str  # no tags
    segNote: str = ""  # timestamps or other info ex from XLIFF
    srcWordCount: int
    timestamp: str

    class Config:
        orm_mode = True

    def __str__(self):
        return f"Segment(segId={self.fromFileId} +'_'+ {self.segId}, seqNo={self.seqNo}, srcLang={self.srcLang}, trgLang={self.trgLang}, srcText={self.srcText}, trgText={self.trgText}, srcCount={self.srcWordCount}, cleanSrcText={self.cleanSrcText}), cleanTrgText={self.cleanTrgText}), timestamp{self.timestamp}"


# create first then
class TMXFile(BaseModel):
    fileId: str
    clientId: str
    fileVersion: str = "1.4"
    fileName: str
    dateAdded: datetime
    segments: List[Segment] = []
    srcWordCount: int
    totalSegs: int

    class Config:
        orm_mode = True

    def __str__(self):
        return f'TMXFile(fileId={self.fileId}, dateCreated={self.dateAdded}, fileName={self.fileName}, fileVersion={self.fileVersion}, segments=[{", ".join(str(u) for u in self.segments[:10])}], srcTextCount={self.srcWordCount}, totalSegs={self.totalSegs})'
