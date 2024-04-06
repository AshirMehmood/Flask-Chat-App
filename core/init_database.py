"""
init database, imports base and session from db.py
"""
from db import Base, session, engine
from models import User, Room, Message


def init_database():
    """
    database initializer method
    """
  
    Base.metadata.create_all(engine)
    user = User(username="mario", password="password", email="example@example.com")
    session.add(user)
    session.commit()
    print("database initialized")


if __name__ == "__main__":
    init_database()