import argparse
from app.database.database import SessionLocal, engine
from app.core.auth import create_user
from app.database.models import UserRole, Base

def init_db(args):
    """Initializes the database and creates tables."""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

def create_admin(args):
    """Creates a new admin user."""
    db = SessionLocal()
    try:
        create_user(db, args.username, args.password, UserRole.ADMIN)
        print(f"Admin user '{args.username}' created successfully.")
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