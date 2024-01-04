import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactBase, ContactResponse, UserModel, UserDb, UserResponse
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    remove_contact,
    update_contact,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactBase(firstname="John", lastname="Doe", email="john.doe@example.com", phone="1234567890",
                           birthdate="2000-01-01", additional_data="2000-01-01", user_id="id")
        contact = Contact()
        self.session.query(Contact).filter().all.return_value = [contact]
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.lastname, body.lastname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthdate, body.birthdate)
        self.assertEqual(result.additional_data, body.additional_data)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactBase(firstname="John", lastname="Doe", email="john.doe@example.com", phone="1234567890",
                           birthdate="2000-01-01", additional_data="2000-01-01", user_id="id")
        contact = Contact()
        self.session.query(Contact).filter().all.return_value = [contact]
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.lastname, body.lastname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthdate, body.birthdate)
        self.assertEqual(result.additional_data, body.additional_data)
        self.assertTrue(hasattr(result, "id"))

if __name__ == '__main__':
    unittest.main()