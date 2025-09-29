from sqlalchemy import create_engine, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY
from typing import List

DATABASE_URL = "postgresql+psycopg2://myuser:mypassword@localhost:5432/mydatabase"
engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    fullname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nickname: Mapped[str] = mapped_column(String(20))
    events: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    groups: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    friendships: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    invitions: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    comments: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    