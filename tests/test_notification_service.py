import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.core import notification_service, product_service, warehouse_service
from app.database import models

class TestNotificationService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.notification_service = notification_service.NotificationService()
        self.user = models.User(id=1, username="testuser", hashed_password="password", role=models.UserRole.ADMIN)
        self.db.add(self.user)
        self.db.commit()
        self.warehouse = warehouse_service.create_warehouse(self.db, self.user.id, "Main Warehouse", "Location")

    def tearDown(self):
        self.db.close()

    def test_get_low_stock_notifications(self):
        # Create a product with low stock
        product_service.create_product(self.db, name="Test Product", description="Test description", price=1000, low_stock_threshold=10, initial_stock=[{'warehouse_id': self.warehouse.id, 'quantity': 5}])

        # Create a product with enough stock
        product_service.create_product(self.db, name="Test Product 2", description="Test description", price=1000, low_stock_threshold=10, initial_stock=[{'warehouse_id': self.warehouse.id, 'quantity': 15}])

        # Get low stock notifications
        notifications = self.notification_service.get_low_stock_notifications(self.db)

        # Verify the notifications
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].name, "Test Product")

if __name__ == "__main__":
    unittest.main()