import unittest
from datetime import date
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_all_contacts,
    get_contact,
    create_contact,
    del_contact,
    put_contact,
    birthdays,
)


class TestContact(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contact_test = Contact(
            id=1,
            first_name='test',
            last_name='test',
            email='test@mail.com',
            phone='0987654321',
            birthday=date(year=2000, month=2, day=20),
        )

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_all_contacts(user=self.user, db=self.session)
        self.assertEquals(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEquals(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(
            first_name=self.contact_test.first_name,
            last_name=self.contact_test.last_name,
            email=self.contact_test.email,
            phone=self.contact_test.phone,
            birthday=self.contact_test.birthday,
        )
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEquals(result.first_name, body.first_name)
        self.assertEquals(result.last_name, body.last_name)
        self.assertEquals(result.email, body.email)
        self.assertEquals(result.phone, body.phone)
        self.assertEquals(result.birthday, body.birthday)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await del_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEquals(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await del_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactModel(
            first_name="example",
            last_name="updated",
            email=self.contact_test.email,
            phone=self.contact_test.phone,
            birthday=self.contact_test.birthday,
        )
        self.session.query().filter().first.return_value = self.contact_test
        result = await put_contact(contact_id=self.contact_test.id, first_name=body.first_name,
                                   last_name=body.last_name, email=body.email, phone=body.phone,
                                   user=self.user, db=self.session)
        self.assertEquals(result, self.contact_test)

    async def test_update_contact_not_found(self):
        body = ContactModel(
            first_name="example",
            last_name="updated",
            email=self.contact_test.email,
            phone=self.contact_test.phone,
            birthday=self.contact_test.birthday,
        )
        self.session.query().filter().first.return_value = None
        result = await put_contact(contact_id=self.contact_test.id, first_name=body.first_name,
                                   last_name=body.last_name, email=body.email, phone=body.phone,
                                   user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_birthday(self):
        today = date.today()
        contacts = [
            Contact(id=1, first_name='Example', last_name='testing', email='example@test.com', birthday=today),
            Contact(id=2, first_name='Test', last_name='Example', email='test@example.com', birthday=today)
        ]
        self.session.query().filter().all.return_value = contacts
        result = await birthdays(user=self.user, db=self.session)
        self.assertEquals(result, contacts)


if __name__ == '__main__':
    unittest.main()
