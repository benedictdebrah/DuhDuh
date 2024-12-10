from sqlalchemy import (
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
)

from dotenv import load_dotenv
import os

load_dotenv()

database_url = os.getenv("DATABASE_URL")


engine = create_engine(database_url)


class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "post"
    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    title: Mapped[str]
    content: Mapped[str]


Base.metadata.create_all(bind=engine)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)