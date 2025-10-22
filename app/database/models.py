from sqlalchemy import Column, Integer, String, DateTime, func, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    SALES = "sales"

class User(Base):
    """
    User model for authentication and authorization.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    language = Column(String, default='en')
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BillOfMaterials(Base):
    """
    Bill of Materials (BOM) model to define the components of a manufactured product.
    """
    __tablename__ = "bill_of_materials"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, unique=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product")
    items = relationship("BillOfMaterialsItem", back_populates="bom", cascade="all, delete-orphan")


class BillOfMaterialsItem(Base):
    """
    Represents a single component item within a Bill of Materials.
    """
    __tablename__ = "bill_of_materials_items"

    id = Column(Integer, primary_key=True, index=True)
    bom_id = Column(Integer, ForeignKey("bill_of_materials.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    bom = relationship("BillOfMaterials", back_populates="items")
    component = relationship("Product", foreign_keys=[component_id])
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Customer(Base):
    """
    Customer model to store customer information.
    """
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    invoices = relationship("Invoice", back_populates="customer")


class ProductCategory(Base):
    """
    ProductCategory model for categorizing products.
    """
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    """
    Product model for inventory management.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    price = Column(Integer, nullable=False)  # Storing price in cents to avoid floating point issues
    stock_quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("ProductCategory", back_populates="products")
    inventory_movements = relationship("InventoryMovement", back_populates="product", cascade="all, delete-orphan")


class InventoryMovementReason(enum.Enum):
    MANUAL_UPDATE = "manual_update"
    SALE = "sale"
    PURCHASE = "purchase"
    INITIAL_STOCK = "initial_stock"


class InventoryMovement(Base):
    """
    InventoryMovement model to audit stock changes.
    """
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    reason = Column(Enum(InventoryMovementReason), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="inventory_movements")


class Supplier(Base):
    """
    Supplier model to store supplier information.
    """
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    VOID = "void"


class Invoice(Base):
    """
    Invoice model for billing customers.
    """
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False, unique=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    status = Column(Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT)
    due_date = Column(DateTime(timezone=True))
    total_amount = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="invoices")
    order = relationship("SalesOrder", back_populates="invoice")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    """
    InvoiceItem model for individual items on an invoice.
    """
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Integer, nullable=False)

    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product")


class SalesOrder(Base):
    """
    SalesOrder model for tracking sales.
    """
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    total_amount = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer")
    items = relationship("SalesOrderItem", back_populates="order", cascade="all, delete-orphan")
    invoice = relationship("Invoice", uselist=False, back_populates="order", cascade="all, delete-orphan")


class SalesOrderItem(Base):
    """
    SalesOrderItem model for individual items in a sales order.
    """
    __tablename__ = "sales_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Integer, nullable=False)

    order = relationship("SalesOrder", back_populates="items")
    product = relationship("Product")


class PurchaseOrder(Base):
    """
    PurchaseOrder model for tracking purchases.
    """
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    total_amount = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="Pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    supplier = relationship("Supplier")
    items = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    """
    PurchaseOrderItem model for individual items in a purchase order.
    """
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Integer, nullable=False)

    order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")


class AccountType(enum.Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class Account(Base):
    """
    Account model for the chart of accounts.
    """
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    account_type = Column(Enum(AccountType), nullable=False)
    balance = Column(Integer, nullable=False, default=0) # Stored in cents
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class JournalEntry(Base):
    """
    JournalEntry model for double-entry bookkeeping.
    """
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transactions = relationship("Transaction", back_populates="journal_entry", cascade="all, delete-orphan")


from datetime import datetime


class Transaction(Base):
    """
    Transaction model representing a single debit or credit.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # Positive for debit, negative for credit
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    journal_entry = relationship("JournalEntry", back_populates="transactions")
    account = relationship("Account")


class AuditTrail(Base):
    __tablename__ = 'audit_trails'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String)

    user = relationship("User")

    def __repr__(self):
        return f"<AuditTrail(user='{self.user.username}', action='{self.action}')>"


class ExpenseCategory(Base):
    """
    ExpenseCategory model for categorizing expenses.
    """
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)

    expenses = relationship("Expense", back_populates="category")


class Expense(Base):
    """
    Expense model for tracking business expenses.
    """
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)  # Stored in cents
    expense_date = Column(DateTime(timezone=True), nullable=False)
    category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True) # Optional link
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("ExpenseCategory", back_populates="expenses")
    user = relationship("User")
    journal_entry = relationship("JournalEntry")