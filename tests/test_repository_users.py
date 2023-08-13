import unittest
from datetime import date
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas import ContactModel
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    confirmed_email,
    update_token,
    update_avatar)


class TestUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=4,
                         username="test",
                         email="test@example.com",
                         password="567234",
                         confirmed=True,)
        self.contact_test = Contact(
            id=1,
            first_name='test',
            last_name='test',
            email='test@mail.com',
            phone='0987654321',
            birthday=date(year=2000, month=2, day=20),)

    async def test_get_user_by_email(self):
        self.session.query().filter().first.return_value = self.user
        result = await get_user_by_email(email=self.user.email, db=self.session)
        self.assertEquals(result, self.user)

    async def test_create_user(self):
        body = UserModel(
            username=self.user.username,
            email=self.user.email,
            password=self.user.password,)
        result = await create_user(body=body, db=self.session)
        self.assertEquals(result.username, self.user.username)
        self.assertEquals(result.email, self.user.email)
        self.assertEquals(result.password, self.user.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_confirmed_email(self):
        result = await confirmed_email(email=self.user.email, db=self.session)
        self.assertIsNone(result)

    async def test_update_token(self):
        result = await update_token(user=self.user, token=None, db=self.session)
        self.assertIsNone(result)

    async def test_update_avatar(self):
        avatar = "https://res.cloudinary.com/dfsuu4glh/image/upload/v1691167363/ContactsApp/test.jpg"
        self.session.query().filter().first.return_value = self.user
        result = await update_avatar(email=self.user.email, url=avatar, db=self.session)
        self.assertEquals(result.avatar, avatar)
