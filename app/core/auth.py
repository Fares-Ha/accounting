import bcrypt
from sqlalchemy.orm import Session
from ..database import models

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

def create_user(db: Session, username: str, password: str, role: models.UserRole):
    """
    Creates a new user with a hashed password.
    """
    hashed_pass = hash_password(password)
    db_user = models.User(username=username, hashed_password=hashed_pass, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> models.User | None:
    """
    Authenticates a user by checking the username and password.
    Returns the user object if authentication is successful, otherwise None.
    """
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def get_users(db: Session):
    """
    Retrieves all users.
    """
    return db.query(models.User).all()

def get_user(db: Session, user_id: int):
    """
    Retrieves a single user by their ID.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def update_user(db: Session, user_id: int, username: str, password: str | None, role: models.UserRole):
    """
    Updates an existing user.
    """
    db_user = get_user(db, user_id)
    if db_user:
        db_user.username = username
        if password:
            db_user.hashed_password = hash_password(password)
        db_user.role = role
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """
    Deletes a user.
    """
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user