import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.database.models import Base, Product, InventoryMovement, InventoryMovementReason
from app.core import product_service, warehouse_service

class TestProductService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create a dummy user and warehouse
        self.user = models.User(id=1, username="testuser", hashed_password="password", role=models.UserRole.ADMIN)
        self.db.add(self.user)
        self.db.commit()
        self.warehouse = warehouse_service.create_warehouse(self.db, self.user.id, "Main Warehouse", "Location")

    def tearDown(self):
        Base.metadata.drop_all(self.engine)
        self.db.close()

    def test_create_product_with_initial_stock(self):
        # Arrange
        product_data = {
            "name": "Test Product",
            "description": "A product for testing",
            "price": 1000,
            "low_stock_threshold": 10,
            "initial_stock": [{'warehouse_id': self.warehouse.id, 'quantity': 50}]
        }

        # Act
        product = product_service.create_product(self.db, **product_data)

        # Assert
        self.assertEqual(product.name, product_data["name"])
        stock_level = product_service.get_stock_level(self.db, product.id, self.warehouse.id)
        self.assertEqual(stock_level, 50)

        # Verify inventory movement
        movements = self.db.query(InventoryMovement).filter_by(product_id=product.id).all()
        self.assertEqual(len(movements), 1)
        self.assertEqual(movements[0].quantity_change, 50)
        self.assertEqual(movements[0].reason, InventoryMovementReason.INITIAL_STOCK)

    def test_adjust_stock_level(self):
        # Arrange
        product = product_service.create_product(self.db, name="Initial Product", description="", price=100)
        product_service.adjust_stock_level(self.db, product.id, self.warehouse.id, 20, InventoryMovementReason.INITIAL_STOCK, self.user.id)

        # Act
        product_service.adjust_stock_level(self.db, product.id, self.warehouse.id, -5, InventoryMovementReason.MANUAL_UPDATE, self.user.id)

        # Assert
        stock_level = product_service.get_stock_level(self.db, product.id, self.warehouse.id)
        self.assertEqual(stock_level, 15)

        movements = self.db.query(InventoryMovement).filter_by(product_id=product.id).order_by(InventoryMovement.id).all()
        self.assertEqual(len(movements), 2)
        self.assertEqual(movements[1].quantity_change, -5)
        self.assertEqual(movements[1].reason, InventoryMovementReason.MANUAL_UPDATE)

    def test_get_low_stock_products(self):
        # Arrange
        product1 = product_service.create_product(self.db, name="Product A", description="", price=100, low_stock_threshold=10)
        product_service.adjust_stock_level(self.db, product1.id, self.warehouse.id, 5, InventoryMovementReason.INITIAL_STOCK)

        product2 = product_service.create_product(self.db, name="Product B", description="", price=100, low_stock_threshold=10)
        product_service.adjust_stock_level(self.db, product2.id, self.warehouse.id, 15, InventoryMovementReason.INITIAL_STOCK)

        # Act
        low_stock_products = product_service.get_low_stock_products(self.db)

        # Assert
        self.assertEqual(len(low_stock_products), 1)
        self.assertEqual(low_stock_products[0].name, "Product A")

    def test_get_inventory_movements(self):
        # Arrange
        product = product_service.create_product(self.db, name="History Product", description="", price=100)
        product_service.adjust_stock_level(self.db, product.id, self.warehouse.id, 10, InventoryMovementReason.INITIAL_STOCK)
        product_service.adjust_stock_level(self.db, product.id, self.warehouse.id, -3, InventoryMovementReason.SALE)
        product_service.adjust_stock_level(self.db, product.id, self.warehouse.id, 8, InventoryMovementReason.PURCHASE)

        # Act
        movements = product_service.get_inventory_movements(self.db, product.id)

        # Assert
        self.assertEqual(len(movements), 3)
        reasons = [m.reason for m in movements]
        self.assertIn(InventoryMovementReason.INITIAL_STOCK, reasons)
        self.assertIn(InventoryMovementReason.SALE, reasons)
        self.assertIn(InventoryMovementReason.PURCHASE, reasons)