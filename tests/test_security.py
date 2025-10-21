import unittest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database import models
from app.core.security import requires_roles, NotAuthorizedError

# Dummy function to be decorated
@requires_roles(models.UserRole.ADMIN)
def admin_only_function(db: Session, user_id: int):
    return "Success"

@requires_roles(models.UserRole.SALES)
def sales_only_function(db: Session, user_id: int = None):
     return "Success"

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create mock users
        self.admin_user = models.User(id=1, username="admin", role=models.UserRole.ADMIN, hashed_password="hashed_password")
        self.sales_user = models.User(id=2, username="sales", role=models.UserRole.SALES, hashed_password="hashed_password")
        self.accountant_user = models.User(id=3, username="accountant", role=models.UserRole.ACCOUNTANT, hashed_password="hashed_password")

        self.db.add_all([self.admin_user, self.sales_user, self.accountant_user])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(self.engine)

    def test_requires_roles_authorized(self):
        """Test that a user with the required role is granted access."""
        result = admin_only_function(self.db, self.admin_user.id)
        self.assertEqual(result, "Success")

    def test_requires_roles_not_authorized(self):
        """Test that a user without the required role is denied access."""
        with self.assertRaises(NotAuthorizedError):
            admin_only_function(self.db, self.sales_user.id)

    def test_requires_roles_invalid_user(self):
        """Test that an invalid user ID raises a ValueError."""
        with self.assertRaises(ValueError):
            admin_only_function(self.db, 999)

    def test_requires_roles_kwargs(self):
        """Test that the decorator works with keyword arguments."""
        result = sales_only_function(db=self.db, user_id=self.sales_user.id)
        self.assertEqual(result, "Success")

    def test_requires_roles_missing_db(self):
        """Test that a ValueError is raised if the db session is missing."""
        with self.assertRaises(ValueError):
            admin_only_function(user_id=self.admin_user.id)

    def test_requires_roles_missing_user_id(self):
        """Test that a ValueError is raised if the user_id is missing."""
        # This will fail because the decorator can't find user_id
        with self.assertRaises(ValueError):
            sales_only_function(db=self.db)

if __name__ == "__main__":
    unittest.main()
