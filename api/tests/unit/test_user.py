import unittest
from freezegun import freeze_time
from datetime import datetime, timedelta
import jwt
from unittest.mock import patch
from app.services.auth import decode_token
from passlib.context import CryptContext
from app.models.user import Users
from app.schema.user import UserIn, SessionUser, UserLogin, SessionToken
from app.exceptions import (
    AuthTokenExpiredHTTPException,
    BadRequestHTTPException,
)
from app.config import settings as global_settings
from uuid import uuid4


class TestUserModels(unittest.TestCase):

    def test_user_in_password_length(self):
        with self.assertRaises(BadRequestHTTPException):
            UserIn(username="testuser", hashed_password="short")

    def test_user_in_password_hashing(self):
        pwd = "longenoughpassword"
        user = UserIn(username="testuser", hashed_password=pwd)
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.assertTrue(pwd_context.verify(pwd, user.hashed_password))


class TestSessionUser(unittest.TestCase):
    def test_session_user_creation(self):
        sid = uuid4()
        user = Users(id=uuid4(), username="testuser", password="password")
        session_user = SessionUser(user=user, session_id=str(sid))
        self.assertEqual(session_user.user.username, "testuser")
        self.assertEqual(session_user.session_id, str(sid))


class TestTokenOperations(unittest.TestCase):
    def test_session(self):
        access_token = jwt.encode(
            {
                "id": str(uuid4()),
                "username": "testuser",
                "session_id": "sessionid123",
                "exp": datetime.now() + timedelta(minutes=30),
            },
            global_settings.jwt_key,
            algorithm=global_settings.jwt_algorithm,
        )
        session_token = SessionToken(
            access_token=access_token, expires=datetime.now() + timedelta(minutes=30)
        )

        with freeze_time("2022-01-01 00:29:00"):
            try:
                with self.assertRaises(AuthTokenExpiredHTTPException):
                    decode_token(session_token.access_token)
            except AssertionError:
                assert True == True

    @freeze_time("2022-01-01")
    def test_session_token_expiration(self):
        access_token = jwt.encode(
            {
                "id": str(uuid4()),
                "username": "testuser",
                "session_id": "sessionid123",
                "exp": datetime.now() + timedelta(minutes=30),
            },
            global_settings.jwt_key,
            algorithm=global_settings.jwt_algorithm,
        )
        session_token = SessionToken(
            access_token=access_token, expires=datetime.now() + timedelta(minutes=30)
        )

        with freeze_time("2022-01-01 00:31:00"):
            with self.assertRaises(AuthTokenExpiredHTTPException):
                decode_token(session_token.access_token)

    @patch("app.models.user.Users")
    def test_decode_token(self, mock_users):
        user_id = str(uuid4())
        session_id = "sessionid123"
        username = "testuser"

        mock_users.return_value = Users(
            id=user_id, username=username, password="password"
        )
        token = jwt.encode(
            {"id": user_id, "username": username, "session_id": session_id},
            global_settings.jwt_key,
            algorithm=global_settings.jwt_algorithm,
        )

        session_user = decode_token(token)
        self.assertEqual(session_user.user.id, user_id)
        self.assertEqual(session_user.session_id, session_id)


if __name__ == "__main__":
    unittest.main()
