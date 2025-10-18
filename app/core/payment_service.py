from sqlalchemy.orm import Session
from app.database.models import Payment, Invoice, PurchaseOrder, PaymentMethod, Account
from app.core import accounting_service
from app.core.audit_service import AuditService
from datetime import datetime

class PaymentService:
    def __init__(self, db_session: Session, user_id: int):
        self.db = db_session
        self.user_id = user_id
        self.audit_service = AuditService(db_session)

    def _create_payment_journal_entry(self, date, description, debit_account_name, credit_account_name, amount):
        debit_account = self.db.query(Account).filter_by(name=debit_account_name).one()
        credit_account = self.db.query(Account).filter_by(name=credit_account_name).one()

        transactions = [
            {'account_id': debit_account.id, 'amount': amount},
            {'account_id': credit_account.id, 'amount': -amount}
        ]
        return accounting_service.create_journal_entry(self.db, description, transactions, date)

    def record_invoice_payment(self, invoice_id: int, amount: int, payment_date: datetime, payment_method: PaymentMethod, payment_account_name: str) -> Payment:
        """
        Records a payment for a customer invoice.
        - Creates a new Payment record.
        - Creates a journal entry to debit the payment account (e.g., Cash) and credit Accounts Receivable.
        - Updates the invoice status if it's fully paid.
        - Creates an audit trail for the action.
        """
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError("Invoice not found")

        total_paid = sum(p.amount for p in invoice.payments)
        if amount > (invoice.total_amount - total_paid):
            raise ValueError("Payment amount cannot exceed the outstanding invoice amount.")

        # Create Journal Entry
        description = f"Payment for Invoice #{invoice.id}"
        journal_entry = self._create_payment_journal_entry(
            date=payment_date,
            description=description,
            debit_account_name=payment_account_name,
            credit_account_name="Accounts Receivable",
            amount=amount
        )

        # Create Payment
        new_payment = Payment(
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            invoice_id=invoice.id,
            journal_entry_id=journal_entry.id
        )
        self.db.add(new_payment)

        # Update Invoice Status
        if (total_paid + amount) >= invoice.total_amount:
            invoice.status = "paid"

        self.db.commit()

        # Audit Trail
        self.audit_service.create_audit_trail(
            user_id=self.user_id,
            action="Record Invoice Payment",
            details=f"Recorded payment of {amount} for Invoice ID {invoice.id}"
        )

        return new_payment

    def record_purchase_payment(self, purchase_order_id: int, amount: int, payment_date: datetime, payment_method: PaymentMethod, payment_account_name: str) -> Payment:
        """
        Records a payment for a supplier's purchase order.
        - Creates a new Payment record.
        - Creates a journal entry to debit Accounts Payable and credit the payment account (e.g., Cash).
        - Updates the purchase order status.
        - Creates an audit trail for the action.
        """
        purchase_order = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_id).first()
        if not purchase_order:
            raise ValueError("Purchase Order not found")

        total_paid = sum(p.amount for p in purchase_order.payments)
        if amount > (purchase_order.total_amount - total_paid):
            raise ValueError("Payment amount cannot exceed the outstanding purchase order amount.")

        # Create Journal Entry
        description = f"Payment for Purchase Order #{purchase_order.id}"
        journal_entry = self._create_payment_journal_entry(
            date=payment_date,
            description=description,
            debit_account_name="Accounts Payable",
            credit_account_name=payment_account_name,
            amount=amount
        )

        # Create Payment
        new_payment = Payment(
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            purchase_order_id=purchase_order.id,
            journal_entry_id=journal_entry.id
        )
        self.db.add(new_payment)

        # Update Purchase Order Status
        if (total_paid + amount) >= purchase_order.total_amount:
            purchase_order.status = "Paid"

        self.db.commit()

        # Audit Trail
        self.audit_service.create_audit_trail(
            user_id=self.user_id,
            action="Record Purchase Payment",
            details=f"Recorded payment of {amount} for Purchase Order ID {purchase_order.id}"
        )

        return new_payment