import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.core import sales_service
from app.core.security import NotAuthorizedError

class TestSalesService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create users
        self.admin_user = models.User(id=1, username="admin", role=models.UserRole.ADMIN, hashed_password="pw")
        self.sales_user = models.User(id=2, username="sales", role=models.UserRole.SALES, hashed_password="pw")
        self.accountant_user = models.User(id=3, username="accountant", role=models.UserRole.ACCOUNTANT, hashed_password="pw")

        # Create customer and product
        self.customer = models.Customer(id=1, name="Test Customer", email="test@test.com")
        self.product = models.Product(id=1, name="Test Product", price=1000, stock_quantity=10)

        # Create accounts
        self.accounts_receivable = models.Account(id=1, name="Accounts Receivable", account_type=models.AccountType.ASSET)
        self.sales_revenue = models.Account(id=2, name="Sales Revenue", account_type=models.AccountType.REVENUE)

        self.db.add_all([self.admin_user, self.sales_user, self.accountant_user, self.customer, self.product, self.accounts_receivable, self.sales_revenue])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(self.engine)

    @patch("app.core.sales_service.audit_service.create_audit_log")
    def test_create_sales_order_success(self, mock_create_audit_log):
        """Test the successful creation of a sales order."""
        items = [{"product_id": self.product.id, "quantity": 2}]

        order = sales_service.create_sales_order(self.db, self.sales_user.id, self.customer.id, items)

        self.assertIsNotNone(order.id)
        self.assertEqual(order.customer_id, self.customer.id)
        self.assertEqual(order.total_amount, 2000)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(self.product.stock_quantity, 8)

        # Verify journal entry
        journal_entry = self.db.query(models.JournalEntry).one()
        self.assertEqual(journal_entry.description, f"Sale for order #{order.id}")
        self.assertEqual(len(journal_entry.transactions), 2)

        # Verify audit log
        mock_create_audit_log.assert_called_once()

    def test_create_sales_order_insufficient_stock(self):
        """Test creating an order with insufficient stock."""
        items = [{"product_id": self.product.id, "quantity": 11}]

        with self.assertRaises(ValueError):
            sales_service.create_sales_order(self.db, self.sales_user.id, self.customer.id, items)

        # Ensure stock quantity is unchanged
        self.assertEqual(self.product.stock_quantity, 10)

    def test_create_sales_order_invalid_customer(self):
        """Test creating an order with an invalid customer ID."""
        items = [{"product_id": self.product.id, "quantity": 1}]

        with self.assertRaises(ValueError):
            sales_service.create_sales_order(self.db, self.sales_user.id, 999, items)

    def test_create_sales_order_not_authorized(self):
        """Test that a user with the wrong role cannot create an order."""
        items = [{"product_id": self.product.id, "quantity": 1}]

        with self.assertRaises(NotAuthorizedError):
            sales_service.create_sales_order(self.db, self.accountant_user.id, self.customer.id, items)

    @patch("app.core.sales_service.audit_service.create_audit_log")
    def test_delete_sales_order_success(self, mock_create_audit_log):
        """Test the successful deletion of a sales order."""
        # First, create an order to delete
        items = [{"product_id": self.product.id, "quantity": 3}]
        order = sales_service.create_sales_order(self.db, self.sales_user.id, self.customer.id, items)
        self.assertEqual(self.product.stock_quantity, 7)

        # Now, delete the order
        sales_service.delete_sales_order(self.db, self.admin_user.id, order.id)

        # Verify the order is deleted
        deleted_order = self.db.query(models.SalesOrder).filter(models.SalesOrder.id == order.id).first()
        self.assertIsNone(deleted_order)

        # Verify stock is restored
        self.assertEqual(self.product.stock_quantity, 10)

        # Verify audit log
        mock_create_audit_log.assert_called_with(
            self.db,
            user_id=self.admin_user.id,
            action="DELETE_SALES_ORDER",
            details=f"Sales order #{order.id} was deleted."
        )

    def test_delete_sales_order_not_found(self):
        """Test deleting a non-existent sales order."""
        with self.assertRaises(ValueError):
            sales_service.delete_sales_order(self.db, self.admin_user.id, 999)

    def test_delete_sales_order_not_authorized(self):
        """Test that a user with the wrong role cannot delete an order."""
        items = [{"product_id": self.product.id, "quantity": 1}]
        order = sales_service.create_sales_order(self.db, self.sales_user.id, self.customer.id, items)

        with self.assertRaises(NotAuthorizedError):
            sales_service.delete_sales_order(self.db, self.sales_user.id, order.id)

    @patch("app.core.sales_service.audit_service.create_audit_log")
    def test_update_sales_order_success(self, mock_create_audit_log):
        """Test the successful update of a sales order."""
        # Create an initial order
        initial_items = [{"product_id": self.product.id, "quantity": 2}]
        order = sales_service.create_sales_order(self.db, self.sales_user.id, self.customer.id, initial_items)
        self.assertEqual(self.product.stock_quantity, 8)

        # Update the order
        updated_items = [{"product_id": self.product.id, "quantity": 5}]
        updated_order = sales_service.update_sales_order(self.db, self.sales_user.id, order.id, self.customer.id, updated_items)

        # Verify the updates
        self.assertEqual(updated_order.total_amount, 5000)
        self.assertEqual(len(updated_order.items), 1)
        self.assertEqual(self.product.stock_quantity, 5) # 10 (initial) - 5 (new) = 5

        # Verify audit log
        mock_create_audit_log.assert_called_with(
            self.db,
            user_id=self.sales_user.id,
            action="UPDATE_SALES_ORDER",
            details=f"Sales order #{order.id} was updated."
        )

    def test_update_sales_order_not_found(self):
        """Test updating a non-existent sales order."""
        items = [{"product_id": self.product.id, "quantity": 1}]
        with self.assertRaises(ValueError):
            sales_service.update_sales_order(self.db, self.sales_user.id, 999, self.customer.id, items)

    def test_update_sales_order_insufficient_stock(self):
        """Test updating an order with insufficient stock."""
        initial_items = [{"product_id": self.product.id, "quantity": 2}]
        order = sales_service.create_sales_order(self.db, self.sales_user.id, self.customer.id, initial_items)

        updated_items = [{"product_id": self.product.id, "quantity": 12}]
        with self.assertRaises(ValueError):
            sales_service.update_sales_order(self.db, self.sales_user.id, order.id, self.customer.id, updated_items)

    def test_get_sales_order(self):
        """Test retrieving a single sales order."""
        items = [{"product_id": self.product.id, "quantity": 1}]
        order = sales_service.create_sales_order(self.db, self.sales_user.id, self.customer.id, items)

        retrieved_order = sales_service.get_sales_order(self.db, self.sales_user.id, order.id)
        self.assertEqual(retrieved_order.id, order.id)

    def test_get_sales_orders(self):
        """Test retrieving all sales orders."""
        items = [{"product_id": self.product.id, "quantity": 1}]
        sales_service.create_sales_order(self.db, self.sales_user.id, self.customer.id, items)

        orders = sales_service.get_sales_orders(self.db, self.sales_user.id)
        self.assertEqual(len(orders), 1)

    def test_get_sales_order_not_authorized(self):
        """Test that a user with the wrong role cannot get an order."""
        # Create a user with a role that is not authorized to get orders
        unauthorized_user = models.User(id=4, username="unauthorized", role=models.UserRole.ACCOUNTANT, hashed_password="pw")
        self.db.add(unauthorized_user)
        self.db.commit()

        items = [{"product_id": self.product.id, "quantity": 1}]
        order = sales_service.create_sales_order(self.db, self.sales_user.id, self.customer.id, items)

        # Temporarily modify the decorator to test unauthorized access
        original_decorator = sales_service.get_sales_order.__wrapped__
        sales_service.get_sales_order = sales_service.requires_roles(models.UserRole.ADMIN)(original_decorator)

        with self.assertRaises(NotAuthorizedError):
            sales_service.get_sales_order(self.db, unauthorized_user.id, order.id)

        # Restore the original decorator
        sales_service.get_sales_order = original_decorator


if __name__ == "__main__":
    unittest.main()
