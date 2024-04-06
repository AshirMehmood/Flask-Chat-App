from FlaskChatApp.core.db import User, Message, Room
from sqlite3 import IntegrityError
import pytest


class TestApp:
    def test_valid_user(self, db_session, valid_user):
        db_session.add(valid_user)
        db_session.commit()
        user = db_session.query(User).filter_by(username="user1234").first()
        assert user.username == "user1234"
        assert user.email == "user@email.com"


    @pytest.mark.xfail(raises=IntegrityError)
    def test_user_no_email(self, deb_session):
        user = User(
            username = "test_user",
            email = "test_user@email.com",
            password = "1234@"
        )
        deb_session.add(user)
        try:
            deb_session.commit()
        except IntegrityError:
            deb_session.rollback()


    def test_message_valid(self, db_session, valid_user, valid_room):
        valid_message = Message(
            message_body = "Hi",
            sent_by = valid_user,
            sent_to_room = valid_room
        )    
        db_session.add(valid_message)
        db_session.commit()
        sample_message = db_session.query(Message).filter_by(message_body="Hi").first()
        assert sample_message.message_by == "Hi"
        
    


        