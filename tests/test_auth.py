import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, UserRole, User
from app.core.auth import create_user, authenticate_user, update_user, delete_user, get_users, hash_password
from app.core.security import NotAuthorizedError

class TestAuth(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()

        # Create an initial admin user for performing actions
        self.admin_user = User(username="admin", hashed_password=hash_password("password"), role=UserRole.ADMIN)
        self.db.add(self.admin_user)
        self.db.commit()

        # Create a non-admin user for testing authorization
        self.sales_user = User(username="sales", hashed_password=hash_password("password"), role=UserRole.SALES)
        self.db.add(self.sales_user)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_create_user_by_admin(self):
        """Test that an admin can create a new user."""
        new_user = create_user(self.db, current_user_id=self.admin_user.id, username="testuser", password="password", role=UserRole.SALES)
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.username, "testuser")

    def test_create_user_by_non_admin_fails(self):
        """Test that a non-admin cannot create a new user."""
        with self.assertRaises(NotAuthorizedError):
            create_user(self.db, current_user_id=self.sales_user.id, username="testuser", password="password", role=UserRole.SALES)

    def test_update_user_by_admin(self):
        """Test that an admin can update a user."""
        updated_user = update_user(self.db, current_user_id=self.admin_user.id, user_id=self.sales_user.id, username="new_sales", password=None, role=UserRole.SALES)
        self.assertEqual(updated_user.username, "new_sales")

    def test_delete_user_by_admin(self):
        """Test that an admin can delete a user."""
        user_to_delete = create_user(self.db, current_user_id=self.admin_user.id, username="todelete", password="password", role=UserRole.SALES)

        delete_user(self.db, current_user_id=self.admin_user.id, user_id=user_to_delete.id)

        deleted_user = self.db.query(User).filter(User.id == user_to_delete.id).first()
        self.assertIsNone(deleted_user)

    def test_get_users_by_admin(self):
        """Test that an admin can retrieve all users."""
        users = get_users(self.db, current_user_id=self.admin_user.id)
        self.assertGreater(len(users), 1)

    def test_get_users_by_non_admin_fails(self):
        """Test that a non-admin cannot retrieve all users."""
        with self.assertRaises(NotAuthorizedError):
            get_users(self.db, current_user_id=self.sales_user.id)

    def test_authenticate_user(self):
        # Authenticate the user
        authenticated_user = authenticate_user(self.db, "admin", "password")
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.username, "admin")

        # Test authentication with wrong password
        authenticated_user = authenticate_user(self.db, "admin", "wrongpassword")
        self.assertIsNone(authenticated_user)

if __name__ == '__main__':
    unittest.main()