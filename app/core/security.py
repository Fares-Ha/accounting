"""
This module provides security-related utilities, including decorators for
role-based access control (RBAC).
"""

from functools import wraps
from sqlalchemy.orm import Session
from ..database import models

class NotAuthorizedError(Exception):
    """Custom exception raised when a user is not authorized to perform an action."""
    def __init__(self, message="User is not authorized to perform this action"):
        self.message = message
        super().__init__(self.message)

def requires_roles(*roles: models.UserRole):
    """
    A decorator to enforce role-based access control on service functions.

    This decorator checks if the user performing the action has one of the
    specified roles. It expects the decorated function to have a `db: Session`
    and a `user_id: int` in its arguments.

    Args:
        *roles: A variable number of UserRole enums that are permitted to
                execute the function.

    Raises:
        NotAuthorizedError: If the user does not have any of the required roles.
        ValueError: If the user cannot be found or if function signature is wrong.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Find db session and user_id in the decorated function's arguments
            db = next((arg for arg in args if isinstance(arg, Session)), kwargs.get("db"))
            user_id = next((arg for arg in args if isinstance(arg, int)), kwargs.get("user_id"))

            if db is None or user_id is None:
                raise ValueError("Decorated function must have 'db: Session' and 'user_id: int' arguments.")

            user = db.query(models.User).filter(models.User.id == user_id).first()

            if not user:
                raise ValueError(f"User with ID {user_id} not found.")

            if user.role not in roles:
                raise NotAuthorizedError(f"User role '{user.role.value}' is not authorized. Required roles: {[r.value for r in roles]}")

            return func(*args, **kwargs)
        return wrapper
    return decorator