import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Supplier
from app.core.supplier_service import (
    create_supplier,
    get_all_suppliers,
    get_supplier_by_id,
    update_supplier,
    delete_supplier,
)

class TestSupplierService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)
        self.session.close()

    def test_create_supplier(self):
        supplier = create_supplier(self.session, "Test Supplier", "test@example.com", "1234567890", "123 Test St")
        self.assertIsNotNone(supplier.id)
        self.assertEqual(supplier.name, "Test Supplier")

    def test_get_all_suppliers(self):
        create_supplier(self.session, "Test Supplier 1", "test1@example.com", "1234567890", "123 Test St")
        create_supplier(self.session, "Test Supplier 2", "test2@example.com", "0987654321", "456 Test St")
        suppliers = get_all_suppliers(self.session)
        self.assertEqual(len(suppliers), 2)

    def test_get_supplier_by_id(self):
        supplier = create_supplier(self.session, "Test Supplier", "test@example.com", "1234567890", "123 Test St")
        retrieved_supplier = get_supplier_by_id(self.session, supplier.id)
        self.assertEqual(retrieved_supplier.id, supplier.id)

    def test_update_supplier(self):
        supplier = create_supplier(self.session, "Test Supplier", "test@example.com", "1234567890", "123 Test St")
        updated_supplier = update_supplier(self.session, supplier.id, "Updated Name", "updated@example.com", "1112223333", "456 Updated St")
        self.assertEqual(updated_supplier.name, "Updated Name")
        self.assertEqual(updated_supplier.email, "updated@example.com")

    def test_delete_supplier(self):
        supplier = create_supplier(self.session, "Test Supplier", "test@example.com", "1234567890", "123 Test St")
        delete_supplier(self.session, supplier.id)
        retrieved_supplier = get_supplier_by_id(self.session, supplier.id)
        self.assertIsNone(retrieved_supplier)

if __name__ == '__main__':
    unittest.main()