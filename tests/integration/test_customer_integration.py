import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.core import customer_service

class TestCustomerIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(self.engine)

    def test_customer_crud_lifecycle(self):
        """
        Tests the full CRUD lifecycle of a customer.
        """
        # 1. Create a customer
        customer = customer_service.create_customer(
            db=self.db,
            name="John Doe",
            email="john.doe@example.com",
            phone="1234567890",
            address="123 Main St"
        )
        self.assertIsNotNone(customer.id)
        self.assertEqual(customer.name, "John Doe")
        customer_id = customer.id

        # 2. Read the customer
        retrieved_customer = customer_service.get_customer_by_id(self.db, customer_id)
        self.assertEqual(retrieved_customer.name, "John Doe")

        # 3. Update the customer
        updated_customer = customer_service.update_customer(
            db=self.db,
            customer_id=customer_id,
            name="Jane Doe",
            email="jane.doe@example.com",
            phone="0987654321",
            address="456 Oak Ave"
        )
        self.assertEqual(updated_customer.name, "Jane Doe")

        # 4. Delete the customer
        customer_service.delete_customer(self.db, customer_id)
        deleted_customer = customer_service.get_customer_by_id(self.db, customer_id)
        self.assertIsNone(deleted_customer)

if __name__ == "__main__":
    unittest.main()
