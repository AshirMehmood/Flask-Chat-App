"""
Models
"""
from typing import List
import uuid
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Unicode, Table
from flask import Flask
# from core.config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///memory"

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)
migrate = Migrate(app, db, render_as_batch=True)

def generate_uuid():
    return str(uuid.uuid4())


association_table = Table( # many to many users -> rooms
    "association_table",
    Base.metadata,
    db.Column("left_id", ForeignKey("user.userID"), primary_key=True),
    db.Column("right_id", ForeignKey("room.room_id"), primary_key=True),
)


class User(db.Model, UserMixin):
    """
    USER MODEL
    """
    __tablename__ = "user"
    id: Mapped[str] = db.mapped_column("userID", String, primary_key=True, default=generate_uuid)
    username = db.Column("user_name", String, unique=True, nullable=False)
    password = db.Column("password", String, nullable=False)
    email = db.Column("email", String, nullable=False)
    about_me = db.Column("about_me", String(255))
    created_rooms: Mapped[List["Room"]] = db.relationship(back_populates="creator")
    rooms: Mapped[List["Room"]] = db.relationship(secondary=association_table, back_populates="users")
    messages: Mapped[List["Message"]] = db.relationship(back_populates="sent_by")
    date_joined= db.mapped_column(DateTime(), default=datetime.now())

   
    def set_password(self, secret):
        """
        set password method, sets the password by converting it in to a hash
        and then stores that hash in the database
        """
        # password hash
        return generate_password_hash(secret)
   
    def check_password(self, secret):
        """
        check password method, checks the password validity by comparing the entered password
        during login, with stored hash of the loaded column's password field, the column is
        loaded in the login view function, using db.session.scalar(...)
        """
        return check_password_hash(self.password, secret)


    def __init__(self, username, password, email):
        self.username = username
        self.password = self.set_password(password)
        self.email = email


    def __repr__(self):
        return f'<User %r> {self.username}'


class Room(db.Model):
    """
    ROOM MODEL
    """
    __tablename__ = "room"
    room_name: Mapped[str] = db.Column("room_name", String, nullable=False)
    room_id: Mapped[str] = db.mapped_column("room_id", ForeignKey(User.id), primary_key=True, default=uuid)
    room_banner = db.Column("room_banner", String, nullable=True)
    creator: Mapped["User"] = db.relationship(foreign_keys=[room_id], back_populates="created_rooms")
    joining_url = db.Column("joining_url", String, nullable=False)
    users: Mapped[List["User"]] = db.relationship(secondary=association_table, back_populates="rooms") # Many To Many
    messages: Mapped[List["Message"]] = db.relationship(back_populates="sent_to_room")


    def __init__(self, room_name: String, room_banner: String,
                joining_url: String, created_by: User):
        self.room_name = room_name
        self.room_banner = room_banner
        self.joining_url = joining_url
        self.created_by = created_by


    def __repr__(self):
        return '<User %r>' % self.room_name


class Message(db.Model):
    """
    MESSAGE MODEL
    """
    __tablename__ = "message"
    message_id: Mapped[int] = mapped_column("message_id", Integer, primary_key=True, autoincrement=True)
    message_body = db.Column("message_body", String)
    # message_body can contain image, gif or sound clip, video, stickers -> BLOB (binary large object)
    sent_to_room_id: Mapped[str] = db.mapped_column(ForeignKey(Room.room_id)) # Many To One
    sent_to_room: Mapped["Room"] = db.relationship(foreign_keys=[sent_to_room_id], back_populates="messages")
    sent_id: Mapped[str] = db.mapped_column(ForeignKey("user.userID"))
    sent_by: Mapped["User"] = relationship(foreign_keys=[sent_id], back_populates="messages")
    date = db.Column(DateTime(), default=datetime.now)


    def __init__(self, message_body: String, sent_by: User, sent_to_room: Room):
        self.message_body = message_body
        self.sent_to_room = sent_to_room
        self.sent_by = sent_by


    def __repr__(self):
        return '<User %r>' % self.message_body


# This context manager is used here to initialize the database if it does not exist in the first place
with app.app_context():
    db.create_all()
    user = User(username=f"daisy {generate_uuid()}", password="password", email="example@example.com")
    db.session.add(user)
    db.session.commit()
    print("database initialized")
