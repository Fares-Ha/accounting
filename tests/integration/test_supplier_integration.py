import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.core.supplier_service import SupplierService

class TestSupplierIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.supplier_service = SupplierService()

    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(self.engine)

    def test_supplier_crud_lifecycle(self):
        """
        Tests the full CRUD lifecycle of a supplier.
        """
        # 1. Create a supplier
        supplier = self.supplier_service.create_supplier(
            db=self.db,
            name="Supplier A",
            email="contact@suppliera.com",
            phone="111222333",
            address="456 Supplier St"
        )
        self.assertIsNotNone(supplier.id)
        self.assertEqual(supplier.name, "Supplier A")
        supplier_id = supplier.id

        # 2. Read the supplier
        retrieved_supplier = self.supplier_service.get_supplier_by_id(self.db, supplier_id)
        self.assertEqual(retrieved_supplier.name, "Supplier A")

        # 3. Update the supplier
        updated_supplier = self.supplier_service.update_supplier(
            db=self.db,
            supplier_id=supplier_id,
            name="Supplier B",
            email="contact@supplierb.com",
            phone="444555666",
            address="789 Supplier Ave"
        )
        self.assertEqual(updated_supplier.name, "Supplier B")

        # 4. Delete the supplier
        self.supplier_service.delete_supplier(self.db, supplier_id)
        deleted_supplier = self.supplier_service.get_supplier_by_id(self.db, supplier_id)
        self.assertIsNone(deleted_supplier)

if __name__ == "__main__":
    unittest.main()
