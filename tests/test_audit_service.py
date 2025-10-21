import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.core.audit_service import AuditService

class TestAuditService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create a user
        self.user = models.User(id=1, username="testuser", role=models.UserRole.ADMIN, hashed_password="pw")
        self.db.add(self.user)
        self.db.commit()

        self.audit_service = AuditService()

    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(self.engine)

    def test_create_audit_log(self):
        """Test that an audit log is successfully created."""
        action = "USER_LOGIN"
        details = "User logged in successfully"

        self.audit_service.create_audit_log(self.db, self.user.id, action, details)

        # Verify the log was created
        log_entry = self.db.query(models.AuditTrail).one()

        self.assertEqual(log_entry.user_id, self.user.id)
        self.assertEqual(log_entry.action, action)
        self.assertEqual(log_entry.details, details)

if __name__ == "__main__":
    unittest.main()
