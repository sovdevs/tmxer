from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://localhost/TMXStore"
# “Applications can create more than one session through the SessionFactory() call, but having one session per APIRouter is recommended”
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import declarative_base, sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://localhost/TMXStore"
# engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=True)
# AsynSessionFactory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
# Base = declarative_base()
