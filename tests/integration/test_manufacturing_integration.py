import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.core import manufacturing_service

class TestManufacturingIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create user and products
        self.user = models.User(id=1, username="testuser", role=models.UserRole.ADMIN, hashed_password="pw")
        self.final_product = models.Product(id=1, name="Finished Good", price=5000, stock_quantity=5)
        self.component1 = models.Product(id=2, name="Component A", price=500, stock_quantity=100)
        self.component2 = models.Product(id=3, name="Component B", price=1000, stock_quantity=50)
        self.db.add_all([self.user, self.final_product, self.component1, self.component2])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(self.engine)

    def test_bom_lifecycle(self):
        """
        Tests the full lifecycle of a Bill of Materials, from creation to deletion.
        """
        # 1. Create a Bill of Materials
        bom_items = [
            {"component_id": self.component1.id, "quantity": 2},
            {"component_id": self.component2.id, "quantity": 1},
        ]
        bom = manufacturing_service.create_bom(
            db=self.db,
            user_id=self.user.id,
            product_id=self.final_product.id,
            name="BOM for Finished Good",
            description="Standard BOM",
            items=bom_items
        )

        # Verify BOM creation
        self.assertIsNotNone(bom.id)
        self.assertEqual(bom.product_id, self.final_product.id)
        self.assertEqual(len(bom.items), 2)

        # Verify AuditTrail for creation
        audit_log_create = self.db.query(models.AuditTrail).one()
        self.assertEqual(audit_log_create.action, "CREATE_BOM")

        bom_id = bom.id

        # 2. Delete the Bill of Materials
        manufacturing_service.delete_bom(self.db, self.user.id, bom_id)

        # Verify deletion
        deleted_bom = self.db.query(models.BillOfMaterials).get(bom_id)
        self.assertIsNone(deleted_bom)

        # Verify that the BOM items were also deleted (due to cascade)
        deleted_bom_items = self.db.query(models.BillOfMaterialsItem).filter_by(bom_id=bom_id).count()
        self.assertEqual(deleted_bom_items, 0)

        # Verify AuditTrail for deletion
        audit_logs = self.db.query(models.AuditTrail).order_by(models.AuditTrail.id.desc()).all()
        self.assertEqual(len(audit_logs), 2)
        self.assertEqual(audit_logs[0].action, "DELETE_BOM")


if __name__ == "__main__":
    unittest.main()
