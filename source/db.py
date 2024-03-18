'''
The Engine, when first returned by create_engine(), has not actually tried to connect to the database yet;
that happens only the first time it is asked to perform a task against the database. This is a software design pattern known as lazy initialization.

with engine.connect() as conn:
    conn.execute(text("query"))
    conn.execute(
        "insert into some_table (x, y) values (:x, :y)",
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
    )
    conn.commit()

# There is also another style of committing data, which is that we can declare our “connect” block to be a transaction block up front. For this mode of operation, we use the Engine.begin() method to acquire the connection, rather than the Engine.connect() method. This method will both manage the scope of the Connection and also enclose everything inside of a transaction with COMMIT at the end, assuming a successful block, or ROLLBACK in case of exception raise. This style is known as begin once: 
    
with engine.begin() as conn:
    conn.execute(text("query"))
    conn.execute(
        "insert into some_table (x, y) values (:x, :y)",
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
    )
    

'''

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Unicode, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError


engine = create_engine("sqlite:///:memory:", echo=True)
Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())



class User(Base):
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
    room_id = Column("room_id", String, ForeignKey("user.id"), primary_key=True, default=generate_uuid)
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
    message_id = Column("message_id", Integer, ForeignKey("user.id"), unique=True, primary_key=True, autoincrement=True)
    message_body = Column("message_body", String)
    # message_body can contain image, gif or sound clip, video, stickers -> BLOB (binary large object)
    sent_to_room: Mapped["Room"] = relationship(back_populates="messages") # Many To One
    sent_by: Mapped["User"] = relationship(back_populates="messages")
    date = Column(DateTime(), default=datetime.now)


    def __init__(self, message_body: String, sent_by: User, sent_to_room: Room):
        self.message_body = message_body
        self.sent_to_room = sent_to_room
        self.sent_by = sent_by


# database methods
        

def add_user(user_name: String, password: String, email: String, session):
    """
    add user method
    """
    exist = session.query(User).filter(User.email==email).all()
    if len(exist) == 0:
        new_user = User(user_name, email, password)
        session.add(new_user)
        session.commit()
    else:
        print("Email already exists !")


def create_room(room_name: String, room_banner: String, joining_url: String, session, created_by: User):
    """
    create room method
    """
    new_room = Room(room_name, room_banner, joining_url, created_by)
    session.add(new_room)
    session.commit()



def send_message(message_body: String, sent_to_room: Room, sent_by: User, session):
    """
    send message method
    """
    new_message = Message(message_body, sent_to_room, sent_by)
    session.add(new_message)
    session.commit()






Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()
