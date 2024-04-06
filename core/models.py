"""
Models
"""
import uuid
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Unicode
from core.db import Base, engine
from flask import current_app
from flask_sqlalchemy import SQLAlchemy


def generate_uuid():
    return str(uuid.uuid4())



class User(Base, UserMixin):
    """
    USER MODEL
    """
    __tablename__ = "user"
    id = Column("userID", String, primary_key=True, default=generate_uuid)
    username = Column("user_name", String, unique=True, nullable=False)
    password = Column("password", String, nullable=False)
    email = Column("email", String, nullable=False)
    created_rooms: Mapped[list["Room"]] = relationship(back_populates="created_by")
    rooms: Mapped[list["Room"]] = relationship(back_populates="users")
    messages: Mapped[list["Message"]] = relationship(back_populates="sent_by")


    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email


class Room(Base):
    """
    ROOM MODEL
    """
    __tablename__ = "room"
    room_name = Column("room_name", String, nullable=False)
    room_id = Column("room_id", String, ForeignKey("user.userID"), primary_key=True, default=generate_uuid)
    room_banner = Column("room_banner", String, nullable=True)
    created_by:  Mapped["User"] = relationship(back_populates="created_rooms") # Many To One
    joining_url = Column("joining_url", String, nullable=False)
    messages: Mapped[list["Message"]] = relationship(back_populates="sent_to_room")
    users: Mapped[list["User"]] = relationship(back_populates="rooms") # Many To Many


    def __init__(self, room_name: String, room_banner: String,
                joining_url: String, created_by: User):
        self.room_name = room_name
        self.room_banner = room_banner
        self.joining_url = joining_url
        self.created_by = created_by


class Message(Base):
    """
    MESSAGE MODEL
    """
    __tablename__ = "message"
    message_id = Column("message_id", Integer, ForeignKey("user.userID"), ForeignKey("room.room_id"), primary_key=True, autoincrement=True)
    message_body = Column("message_body", String)
    # message_body can contain image, gif or sound clip, video, stickers -> BLOB (binary large object)
    sent_to_room: Mapped["Room"] = relationship(back_populates="messages") # Many To One
    sent_by: Mapped["User"] = relationship(back_populates="messages")
    date = Column(DateTime(), default=datetime.now)


    def __init__(self, message_body: String, sent_by: User, sent_to_room: Room):
        self.message_body = message_body
        self.sent_to_room = sent_to_room
        self.sent_by = sent_by

# user table not found, we need an initial database ?, possible solution -> absolute path instead of in-memory sqlite
from flask import current_app

db = SQLAlchemy()
current_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
current_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(current_app)


def init_database():
    """
    database initializer method
    """

    db.create_all()
    user = User(username="mario", password="password", email="example@example.com")
    db.session.add(user)
    db.session.commit()
    print("database initialized")


with current_app.app_context():
    init_database()
