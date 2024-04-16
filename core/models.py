"""
Models
"""
import uuid
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Unicode
from flask import Flask
# from core.config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///memory"

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)


def generate_uuid():
    return str(uuid.uuid4())



class User(db.Model, UserMixin):
    """
    USER MODEL
    """
    __tablename__ = "user"
    id = db.Column("userID", String, primary_key=True, default=generate_uuid)
    username = db.Column("user_name", String, unique=True, nullable=False)
    password = db.Column("password", String, nullable=False)
    email = db.Column("email", String, nullable=False)
    created_rooms: Mapped[list["Room"]] = relationship(back_populates="created_by")
    rooms: Mapped[list["Room"]] = relationship(back_populates="users")
    messages: Mapped[list["Message"]] = relationship(back_populates="sent_by")

    
    def set_password(self, secret):
        # password hash
        return generate_password_hash(secret)
    
    def check_password(self, secret):
        return check_password_hash(self.password, secret)


    def __init__(self, username, password, email):
        self.username = username
        self.password = self.set_password(password)
        self.email = email


    def __repr__(self):
        return '<User %r>' % self.username


class Room(db.Model):
    """
    ROOM MODEL
    """
    __tablename__ = "room"
    room_name = db.Column("room_name", String, nullable=False)
    room_id = db.Column("room_id", String, ForeignKey("user.userID"), primary_key=True, default=generate_uuid)
    room_banner = db.Column("room_banner", String, nullable=True)
    created_by:  Mapped["User"] = relationship(back_populates="created_rooms") # Many To One
    joining_url = db.Column("joining_url", String, nullable=False)
    messages: Mapped[list["Message"]] = relationship(back_populates="sent_to_room")
    users: Mapped[list["User"]] = relationship(back_populates="rooms") # Many To Many


    def __init__(self, room_name: String, room_banner: String,
                joining_url: String, created_by: User):
        self.room_name = room_name
        self.room_banner = room_banner
        self.joining_url = joining_url
        self.created_by = created_by
    


    def __repr__(self):
        return '<User %r>' % self.joining_url


class Message(db.Model):
    """
    MESSAGE MODEL
    """
    __tablename__ = "message"
    message_id = db.Column("message_id", Integer, ForeignKey("user.userID"), ForeignKey("room.room_id"), primary_key=True, autoincrement=True)
    message_body = db.Column("message_body", String)
    # message_body can contain image, gif or sound clip, video, stickers -> BLOB (binary large object)
    sent_to_room: Mapped["Room"] = relationship(back_populates="messages") # Many To One
    sent_by: Mapped["User"] = relationship(back_populates="messages")
    date = db.Column(DateTime(), default=datetime.now)


    def __init__(self, message_body: String, sent_by: User, sent_to_room: Room):
        self.message_body = message_body
        self.sent_to_room = sent_to_room
        self.sent_by = sent_by


    def __repr__(self):
        return '<User %r>' % self.message_body
    

with app.app_context():
    db.create_all()
    user = User(username="daisy", password="password", email="example@example.com")
    db.session.add(user)
    db.session.commit()
    print("database initialized")
