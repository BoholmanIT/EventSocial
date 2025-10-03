from sqlalchemy import create_engine, Integer, String, ForeignKey, Table, Column, Date, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from typing import List
from datetime import date, datetime
import enum
from filter_event import filter_event

DATABASE_URL = "postgresql+psycopg2://myuser:mypassword@localhost:5432/mydatabase"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

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
    comments = relationship("Comment", back_populates="event")
    date_event: Mapped[date] = mapped_column(Date, nullable=False)
    datetime_event: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    
    
class Invitation(Base):
    __tablename__ = "invitations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    invited_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    inviter_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.pending)
    event = relationship("Event", back_populates="invitations")
    invited_user = relationship("User", back_populates="recieved_invatat")
    inviter_user = relationship("User", back_populates="sent_user") 
    
    def accept(self, session):
        self.status = Status.accepted
        session.commit()
    
    def decline(self, session):
        self.status = Status.declined
        session.commit()
        
    
    
class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    commenter_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    comment_event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    commenter_user = relationship("User", back_populates="comments")
    event = relationship("Event", back_populates="comments")
    
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
    
    friends = relationship(
        "User", 
        secondary=friendships, 
        primaryjoin=id == friendships.c.user_id, 
        secondaryjoin=id == friendships.c.friend_id, 
        backref="friends_back"
    )
    
    recieved_invat = relationship("Invitation", foreign_keys=[Invitation.invited_user_id], back_populates="invited_user")
    sent_user = relationship("Invitation", foreign_keys=[Invitation.inviter_user_id], back_populates="inviter_user")
    comments= relationship("Comment", foreign_keys=[Comment.commenter_user_id], back_populates="commenter_user")
    
    def add_friend(self, other_user: "User", session):
        if other_user not in self.friends:
            self.friends.append(other_user)
            session.comit()
            
    def remove_friend(self, other_user: "User", session):
        if other_user in self.friends:
            self.friends.remove(other_user)
            session.commit()
    
    def can_invite(self, event: Event) -> bool:
        return self in event.user_in_event
    
    def send(self, event: Event, invited_user: "User", session) -> bool:
        if not self.can_invite(event):
            return False
        
        existing_invatation = session.query(Invitation).filter_by(
            event_id=event.id,
            invited_user_id=invited_user.id
        ).first()
        
        if existing_invatation:
            return False
        
        Invitation = Invitation(
            event_id=event.id,
            invited_user_id=invited_user.id,
            inviter_user=self.id,
            status=Status.pending
        )
        session.add(Invitation)
        session.commit()
        return True
        
    
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

         