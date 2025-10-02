from sqlalchemy import create_engine, Integer, String, ForeignKey, Table, Column, Date, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from typing import List
from datetime import date, datetime
import enum

DATABASE_URL = "postgresql+psycopg2://myuser:mypassword@localhost:5432/mydatabase"
engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

class Status(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"

friendships = Table(
    "friendships",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("friend_id", ForeignKey("users.id"), primary_key=True)
)

user_events = Table(
    "user_events",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("event_id", ForeignKey("events.id"), primary_key=True)
)

user_group = Table(
    "user_group",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("group_id", ForeignKey("groups.id"), primary_key=True)
)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    place: Mapped[str] = mapped_column(String(200), nullable=False)
    decs: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_in_event = relationship(
        "User",
        secondary=user_events,
        back_populates="events"
    )
    invitations = relationship("Invitation", back_populates="event")
    date_event: Mapped[date] = mapped_column(Date, nullable=False)
    datetime_event: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
class Invitation(Base):
    __tablename__ = "invitations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column("events.id", nullable=False)
    invited_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    inviter_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    event = relationship("Event", back_populates="invitations")
    invited_user = relationship("User", back_populates="recieved_invatat")
    inviter_user = relationship("User", back_populates="sent_user") 
    
class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, nullable=False)
    commenter_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    comment_event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    fullname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nickname: Mapped[str] = mapped_column(String(20))
    events = relationship(
        "Event",
        secondary=user_events,
        back_populates="user_in_event"
    )
    groups = relationship(
        "Group",
        secondary=user_group,
        back_populates="user_in_group"
    )
    friends: Mapped[List["User"]] = relationship(
        "User", 
        secondary=friendships, 
        primaryjoin=id == friendships.c.user_id, 
        secondaryjoin=id == friendships.c.friend_id, 
        backref="friends_back"
    )
    recieved_invat = relationship("Invitation", foreign_keys=[Invitation.invited_user_id], back_populates="invited_user")
    sent_user = relationship("Invitation", foreign_keys=[Invitation.inviter_user_id], back_populates="inviter_user")
    comments_user_id: Mapped[int] = mapped_column("Comments", )
    
class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    desc: Mapped[str | None] = mapped_column(nullable=True)
    user_in_group = relationship(
        "User",
        secondary=user_group,
        back_populates="groups"
    )
    

     