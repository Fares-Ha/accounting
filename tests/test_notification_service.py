import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.core import notification_service, product_service
from app.database import models

class TestNotificationService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.notification_service = notification_service.NotificationService()

    def tearDown(self):
        self.db.close()

    def test_get_low_stock_notifications(self):
        # Create a product with low stock
        product_service.create_product(self.db, name="Test Product", description="Test description", price=1000, stock_quantity=5, low_stock_threshold=10)

        # Create a product with enough stock
        product_service.create_product(self.db, name="Test Product 2", description="Test description", price=1000, stock_quantity=15, low_stock_threshold=10)

        # Get low stock notifications
        notifications = self.notification_service.get_low_stock_notifications(self.db)

        # Verify the notifications
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].name, "Test Product")

if __name__ == "__main__":
    unittest.main()