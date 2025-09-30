from sqlalchemy import create_engine, Integer, String, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from typing import List
from datetime import date, datetime

DATABASE_URL = "postgresql+psycopg2://myuser:mypassword@localhost:5432/mydatabase"
engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass


friendships = Table(
    "friendships",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("friend_id", ForeignKey("users.id"), primary_key=True)
)
class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    place: Mapped[str] = mapped_column(String(200), nullable=False)
    decs: Mapped[str | None]
    
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    fullname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nickname: Mapped[str] = mapped_column(String(20))
    events: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    groups: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    friends: Mapped[List["User"]] = relationship(
        "User", 
        secondary=friendships, 
        primaryjoin=id == friendships.c.user_id, 
        secondaryjoin=id == friendships.c.friend_id, 
        backref="friends_back"
    )
    invitions: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    comments: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    

