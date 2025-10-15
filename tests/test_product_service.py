import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Product, InventoryMovement, InventoryMovementReason
from app.core import product_service

class TestProductService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)
        self.db.close()

    def test_create_product_with_initial_stock(self):
        # Arrange
        product_data = {
            "name": "Test Product",
            "description": "A product for testing",
            "price": 1000,
            "stock_quantity": 50,
            "low_stock_threshold": 10,
        }

        # Act
        product = product_service.create_product(self.db, **product_data)

        # Assert
        self.assertEqual(product.name, product_data["name"])
        self.assertEqual(product.stock_quantity, 50)

        # Verify inventory movement
        movements = self.db.query(InventoryMovement).filter_by(product_id=product.id).all()
        self.assertEqual(len(movements), 1)
        self.assertEqual(movements[0].quantity_change, 50)
        self.assertEqual(movements[0].reason, InventoryMovementReason.INITIAL_STOCK)

    def test_update_product_stock(self):
        # Arrange
        product = product_service.create_product(self.db, name="Initial Product", description="", price=100, stock_quantity=20)

        # Act
        product_service.update_product(self.db, product.id, name="Updated Product", description="Desc", price=150, stock_quantity=15)

        # Assert
        updated_product = self.db.query(Product).get(product.id)
        self.assertEqual(updated_product.stock_quantity, 15)

        movements = self.db.query(InventoryMovement).filter_by(product_id=product.id).order_by(InventoryMovement.id).all()
        self.assertEqual(len(movements), 2)
        self.assertEqual(movements[1].quantity_change, -5)
        self.assertEqual(movements[1].reason, InventoryMovementReason.MANUAL_UPDATE)

    def test_get_low_stock_products(self):
        # Arrange
        product_service.create_product(self.db, name="Product A", description="", price=100, stock_quantity=5, low_stock_threshold=10)
        product_service.create_product(self.db, name="Product B", description="", price=100, stock_quantity=15, low_stock_threshold=10)

        # Act
        low_stock_products = product_service.get_low_stock_products(self.db)

        # Assert
        self.assertEqual(len(low_stock_products), 1)
        self.assertEqual(low_stock_products[0].name, "Product A")

    def test_get_inventory_movements(self):
        # Arrange
        product = product_service.create_product(self.db, name="History Product", description="", price=100, stock_quantity=10)
        product_service.adjust_stock_quantity(self.db, product, -3, InventoryMovementReason.SALE)
        product_service.adjust_stock_quantity(self.db, product, 8, InventoryMovementReason.PURCHASE)

        # Act
        movements = product_service.get_inventory_movements(self.db, product.id)

        # Assert
        self.assertEqual(len(movements), 3)
        reasons = [m.reason for m in movements]
        self.assertIn(InventoryMovementReason.INITIAL_STOCK, reasons)
        self.assertIn(InventoryMovementReason.SALE, reasons)
        self.assertIn(InventoryMovementReason.PURCHASE, reasons)