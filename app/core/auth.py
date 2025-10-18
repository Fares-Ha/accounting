import bcrypt
from sqlalchemy.orm import Session
from ..database import models
from .audit_service import AuditService
from .security import requires_roles

audit_service = AuditService()

def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@requires_roles(models.UserRole.ADMIN)
def create_user(db: Session, current_user_id: int, username: str, password: str, role: models.UserRole):
    """
    Creates a new user with a hashed password. Only Admins can create users.
    """
    hashed_pass = hash_password(password)
    db_user = models.User(username=username, hashed_password=hashed_pass, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    audit_service.create_audit_log(
        db,
        user_id=current_user_id,
        action="CREATE_USER",
        details=f"Admin user #{current_user_id} created new user #{db_user.id} with role {role.value}"
    )
    db.commit()

    return db_user

def create_initial_admin(db: Session, username: str, password: str) -> models.User:
    """
    Creates the initial administrator user.
    This function is intended for command-line setup and does not have security checks.
    """
    # Check if an admin already exists
    if db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).first():
        raise ValueError("An admin user already exists.")

    hashed_pass = hash_password(password)
    db_user = models.User(username=username, hashed_password=hashed_pass, role=models.UserRole.ADMIN)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    audit_service.create_audit_log(
        db,
        user_id=db_user.id, # Attribute action to the new admin
        action="CREATE_INITIAL_ADMIN",
        details=f"Initial admin user '{username}' created via command line."
    )
    db.commit()

    return db_user

def authenticate_user(db: Session, username: str, password: str) -> models.User | None:
    """
    Authenticates a user by checking the username and password.
    Returns the user object if authentication is successful, otherwise None.
    """
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        audit_service.create_audit_log(
            db,
            user_id=user.id if user else None,
            action="LOGIN_FAILURE",
            details=f"Failed login attempt for username '{username}'"
        )
        return None

    audit_service.create_audit_log(
        db,
        user_id=user.id,
        action="LOGIN_SUCCESS",
        details=f"User '{username}' logged in successfully"
    )
    return user

@requires_roles(models.UserRole.ADMIN)
def get_users(db: Session, current_user_id: int):
    """
    Retrieves all users. Only Admins can retrieve all users.
    """
    return db.query(models.User).all()

def get_user(db: Session, user_id: int):
    """
    Retrieves a single user by their ID.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

@requires_roles(models.UserRole.ADMIN)
def update_user(db: Session, current_user_id: int, user_id: int, username: str, password: str | None, role: models.UserRole):
    """
    Updates an existing user. Only Admins can update users.
    """
    db_user = get_user(db, user_id)
    if db_user:
        db_user.username = username
        if password:
            db_user.hashed_password = hash_password(password)
        db_user.role = role

        audit_service.create_audit_log(
            db,
            user_id=current_user_id,
            action="UPDATE_USER",
            details=f"Admin user #{current_user_id} updated user #{user_id}"
        )
        db.commit()
        db.refresh(db_user)
    return db_user

@requires_roles(models.UserRole.ADMIN)
def delete_user(db: Session, current_user_id: int, user_id: int):
    """
    Deletes a user. Only Admins can delete users.
    """
    db_user = get_user(db, user_id)
    if db_user:
        audit_service.create_audit_log(
            db,
            user_id=current_user_id,
            action="DELETE_USER",
            details=f"Admin user #{current_user_id} deleted user #{user_id}"
        )
        db.delete(db_user)
        db.commit()
    return db_user

def update_user_language(db: Session, user_id: int, language: str):
    """
    Updates the language preference for a specific user.
    """
    db_user = get_user(db, user_id)
    if db_user:
        db_user.language = language
        db.commit()
        db.refresh(db_user)
    return db_user