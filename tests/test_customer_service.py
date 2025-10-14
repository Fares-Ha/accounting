import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Customer
from app.core.customer_service import (
    create_customer,
    get_customers,
    get_customer_by_id,
    update_customer,
    delete_customer,
)

class TestCustomerService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)
        self.session.close()

    def test_create_customer(self):
        customer = create_customer(self.session, "Test Customer", "test@example.com", "1234567890", "123 Test St")
        self.assertIsNotNone(customer.id)
        self.assertEqual(customer.name, "Test Customer")

    def test_get_customers(self):
        create_customer(self.session, "Test Customer 1", "test1@example.com", "1234567890", "123 Test St")
        create_customer(self.session, "Test Customer 2", "test2@example.com", "0987654321", "456 Test St")
        customers = get_customers(self.session)
        self.assertEqual(len(customers), 2)

    def test_get_customer_by_id(self):
        customer = create_customer(self.session, "Test Customer", "test@example.com", "1234567890", "123 Test St")
        retrieved_customer = get_customer_by_id(self.session, customer.id)
        self.assertEqual(retrieved_customer.id, customer.id)

    def test_update_customer(self):
        customer = create_customer(self.session, "Test Customer", "test@example.com", "1234567890", "123 Test St")
        updated_customer = update_customer(self.session, customer.id, "Updated Name", "updated@example.com", "1112223333", "456 Updated St")
        self.assertEqual(updated_customer.name, "Updated Name")
        self.assertEqual(updated_customer.email, "updated@example.com")

    def test_delete_customer(self):
        customer = create_customer(self.session, "Test Customer", "test@example.com", "1234567890", "123 Test St")
        delete_customer(self.session, customer.id)
        retrieved_customer = get_customer_by_id(self.session, customer.id)
        self.assertIsNone(retrieved_customer)

if __name__ == '__main__':
    unittest.main()