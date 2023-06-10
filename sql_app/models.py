from sqlalchemy import (
    Boolean,
    Column,
    Index,
    ForeignKey,
    Integer,
    String,
    Enum,
    DateTime,
    UniqueConstraint,
    CheckConstraint,
    Table,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class TMXFile(Base):
    __tablename__ = "tmxfiles"

    # uuid = Column(UUID(as_uuid=True), primary_key=True, index=True)
    uuid_str = Column(String, primary_key=True, index=True)
    fileVersion = Column(String, default="1.4")
    fileName = Column(String)
    dateAdded = Column(DateTime, default=datetime.utcnow)
    srcWordCount = Column(Integer)
    totalSegs = Column(Integer)
    segments = relationship("Segment", back_populates="fromFile")
    # __table_args__ = (CheckConstraint("srcWordCount>0", name="srcWrdCt_positive"),)
    __table_args__ = (UniqueConstraint("fileName"),)


class AcceptedDomain(Base):
    __tablename__ = "accepted_domains"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String, unique=True)

    def __init__(self, domain):
        self.domain = domain


segment_categories = Table(
    "segment_categories",
    Base.metadata,
    Column(
        "category_id", Integer, ForeignKey("accepted_categories.id"), primary_key=True
    ),
    Column("segment_id", String, ForeignKey("segments.segId"), primary_key=True),
)


class AcceptedCategory(Base):
    __tablename__ = "accepted_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, unique=True)

    segments = relationship(
        "Segment", secondary=segment_categories, back_populates="categories"
    )

    def __init__(self, category):
        self.category = category


class AcceptedLanguage(Base):
    __tablename__ = "accepted_languages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    language = Column(String, unique=True)

    def __init__(self, language):
        self.language = language


class Segment(Base):
    __tablename__ = "segments"

    # uuid = Column(UUID(as_uuid=True), primary_key=True)
    segId = Column(String, primary_key=True, index=True)
    seqNo = Column(Integer)
    srcLang = Column(String)
    trgLang = Column(String)
    srcText = Column(String)
    cleanSrcText = Column(String)
    trgText = Column(String)
    cleanTrgText = Column(String)
    segNote = Column(String, default="")
    srcWordCount = Column(Integer)
    timestamp = Column(String)
    created_on = Column(DateTime(), default=datetime.utcnow)
    fromFileId = Column(String, ForeignKey("tmxfiles.uuid_str"))
    fromFile = relationship("TMXFile", back_populates="segments")

    categories = relationship(
        "AcceptedCategory", secondary=segment_categories, back_populates="segments"
    )

    idx_uuid = Index("idx_segId", segId)
    idx_srcText = Index("idx_srcText", srcText)
    idx_trgText = Index("idx_trgText", trgText)

    # __table_args__ = (UniqueConstraint("srcText", "trgLang", "timestamp"),)
