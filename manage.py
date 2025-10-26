import argparse
import sys
from sqlalchemy import inspect
from app.database.database import SessionLocal, engine
from app.core.auth import create_initial_admin
from app.core import accounting_service
from app.database.models import UserRole, Base, AccountType

def seed_default_accounts(db):
    """Seeds the database with default accounts if they don't exist."""
    default_accounts = [
        {"name": "Accounts Receivable", "type": AccountType.ASSET},
        {"name": "Sales Revenue", "type": AccountType.REVENUE},
        {"name": "Cash", "type": AccountType.ASSET},
    ]
    for acc in default_accounts:
        if not accounting_service.get_account_by_name(db, acc["name"]):
            accounting_service.create_account(db, acc["name"], acc["type"])
            print(f"Created default account: {acc['name']}")

def is_db_initialized():
    """Checks if the database has been initialized by checking for the 'users' table."""
    inspector = inspect(engine)
    return inspector.has_table("users")

def init_db(args):
    """Initializes the database, creates tables, and seeds default accounts."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
    db = SessionLocal()
    try:
        seed_default_accounts(db)
    finally:
        db.close()

def create_admin(args):
    """Creates a new admin user."""
    if not is_db_initialized():
        print("Error: The database has not been initialized. Please run 'python manage.py init-db' first.")
        sys.exit(1)

    db = SessionLocal()
    try:
        create_initial_admin(db, args.username, args.password)
        print(f"Admin user '{args.username}' created successfully.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Management script for Ajyad Accountant.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Init DB command
    parser_init_db = subparsers.add_parser("init-db", help="Initialize the database.")
    parser_init_db.set_defaults(func=init_db)

    # Create admin user command
    parser_create_admin = subparsers.add_parser("create-admin", help="Create a new admin user.")
    parser_create_admin.add_argument("username", help="The username for the new admin user.")
    parser_create_admin.add_argument("password", help="The password for the new admin user.")
    parser_create_admin.set_defaults(func=create_admin)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()