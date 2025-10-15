import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.core.reporting_service import ReportingService
from app.database.models import Product, SalesOrder, SalesOrderItem, ProductCategory
from datetime import datetime

class TestReportingService(unittest.TestCase):
    """
    Unit tests for the ReportingService.
    """

    def setUp(self):
        """
        Set up an in-memory SQLite database for testing.
        """
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.reporting_service = ReportingService()

    def tearDown(self):
        """
        Clean up the database after each test.
        """
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_get_sales_report(self):
        """
        Test the get_sales_report method.
        """
        # Create test data
        category = ProductCategory(name="Electronics")
        product1 = Product(name="Laptop", price=100000, category=category)
        product2 = Product(name="Mouse", price=2500, category=category)
        self.db.add_all([category, product1, product2])
        self.db.commit()

        order1 = SalesOrder(customer_id=1, total_amount=102500, created_at=datetime(2023, 1, 15))
        order1.items.append(SalesOrderItem(product=product1, quantity=1, price_per_unit=100000))
        order1.items.append(SalesOrderItem(product=product2, quantity=1, price_per_unit=2500))

        order2 = SalesOrder(customer_id=2, total_amount=200000, created_at=datetime(2023, 1, 20))
        order2.items.append(SalesOrderItem(product=product1, quantity=2, price_per_unit=100000))

        self.db.add_all([order1, order2])
        self.db.commit()

        # Generate report
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        report = self.reporting_service.get_sales_report(self.db, start_date, end_date)

        # Assertions
        self.assertEqual(len(report), 2)
        self.assertEqual(report[0].name, "Laptop")
        self.assertEqual(report[0].total_quantity, 3)
        self.assertEqual(report[0].total_revenue, 300000)
        self.assertEqual(report[1].name, "Mouse")
        self.assertEqual(report[1].total_quantity, 1)
        self.assertEqual(report[1].total_revenue, 2500)

    def test_get_inventory_report(self):
        """
        Test the get_inventory_report method.
        """
        # Create test data
        category = ProductCategory(name="Books")
        product1 = Product(name="The Lord of the Rings", price=1500, stock_quantity=10, low_stock_threshold=5, category=category)
        product2 = Product(name="A Game of Thrones", price=2000, stock_quantity=3, low_stock_threshold=5, category=category)
        self.db.add_all([category, product1, product2])
        self.db.commit()

        # Generate report
        report = self.reporting_service.get_inventory_report(self.db)

        # Assertions
        self.assertEqual(len(report), 2)
        self.assertEqual(report[0].name, "A Game of Thrones")
        self.assertEqual(report[0].stock_quantity, 3)
        self.assertEqual(report[1].name, "The Lord of the Rings")
        self.assertEqual(report[1].stock_quantity, 10)

if __name__ == "__main__":
    unittest.main()