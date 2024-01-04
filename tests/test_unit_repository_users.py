import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from src.repository.users import get_user_by_email, create_user, update_token, confirmed_email
from src.database.models import User
from src.schemas import UserModel


class TestUserRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    @patch('src.repository.users.Gravatar')
    async def test_create_user(self, mock_gravatar):
        mock_gravatar.return_value.get_image.return_value = "mocked_avatar_url"
        user_model = UserModel(username="testuser", email="test@example.com", password="testpassword")
        db_session = MagicMock(spec=Session)

        with patch('src.repository.users.User', spec=User) as mock_user:
            result = await create_user(user_model, db_session)

        mock_gravatar.assert_called_once_with(user_model.email)
        mock_gravatar.return_value.get_image.assert_called_once()
        mock_user.assert_called_once_with(username=user_model.username, email=user_model.email,
                                          password=user_model.password, avatar="mocked_avatar_url")

        db_session.add.assert_called_once_with(mock_user.return_value)
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once_with(mock_user.return_value)

        self.assertEqual(result, mock_user.return_value)

    async def test_get_user_by_email(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email="test@example.com", db=self.session)
        self.assertEqual(result, user)

    async def test_update_token(self):
        user = MagicMock(spec=User)
        token = "new_token"
        db_session = MagicMock(spec=Session)

        await update_token(user, token, db_session)

        self.assertEqual(user.refresh_token, token)
        db_session.commit.assert_called_once()

    @patch('src.repository.users.get_user_by_email', return_value=MagicMock(confirmed=False))
    async def test_confirmed_email(self, mock_get_user):
        email = "test@example.com"
        db_session = MagicMock(spec=Session)

        await confirmed_email(email, db_session)

        mock_get_user.assert_called_once_with(email, db_session)
        self.assertTrue(mock_get_user.return_value.confirmed)


if __name__ == '__main__':
    unittest.main()
