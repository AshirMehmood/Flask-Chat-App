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

from sqlalchemy import create_engine
from sqlalchemy.orm import  sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import g, current_app
from flask_sqlalchemy import SQLAlchemy


db = None


def get_db():
    """
    Adding db to global context, so db stays same in every
    module
    """
    global db
    if not db:
        db = SQLAlchemy(current_app)
    return db


engine = create_engine("sqlite:///:memory:", echo=True)
Base = declarative_base()


# database methods
        
# def create_room(room_name: String, room_banner: String, joining_url: String, session, created_by: User):
#     """
#     create room method
#     """
#     new_room = Room(room_name, room_banner, joining_url, created_by)
#     session.add(new_room)
#     session.commit()



# def send_message(message_body: String, sent_to_room: Room, sent_by: User, session):
#     """
#     send message method
#     """
#     new_message = Message(message_body, sent_to_room, sent_by)
#     session.add(new_message)
#     session.commit()

Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()
