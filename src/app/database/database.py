from sqlalchemy import (
    create_engine,
    String,
    ForeignKey
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    relationship
)
from app.core.config import settings
from dotenv import load_dotenv
import os

load_dotenv()

# database_url = os.getenv("DATABASE_URL")
database_url = settings.DATABASE_URL


engine = create_engine(database_url)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship to Post
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="user", cascade="all, delete")

class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationship to User
    user: Mapped["User"] = relationship("User", back_populates="posts")


Base.metadata.create_all(bind=engine)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)