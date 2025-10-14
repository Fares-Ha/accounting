import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, UserRole, User
from app.core.auth import create_user, authenticate_user

class TestAuth(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_create_and_authenticate_user(self):
        # Create a new user
        username = "testuser"
        password = "testpassword"
        role = UserRole.ADMIN
        user = create_user(self.db, username, password, role)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, username)

        # Authenticate the user
        authenticated_user = authenticate_user(self.db, username, password)
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.username, username)

        # Test authentication with wrong password
        authenticated_user = authenticate_user(self.db, username, "wrongpassword")
        self.assertIsNone(authenticated_user)

if __name__ == '__main__':
    unittest.main()