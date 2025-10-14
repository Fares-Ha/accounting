# Al Ameen Desktop Application

This is a full-featured, cross-platform desktop application for accounting, inventory, and customer management.

## Project Structure

- `app/`: Contains the core application source code.
  - `core/`: Business logic and core functionalities.
  - `database/`: Database connection, schema, and models.
  - `ui/`: User interface components (PyQt6 widgets and windows).
  - `assets/`: Static files like images and icons.
  - `locale/`: Translation files for bilingual support.
- `docs/`: User and developer documentation.
- `tests/`: Unit and integration tests.
- `main.py`: The main entry point of the application.
- `requirements.txt`: Python dependencies for the project.

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialize the database:**
   ```bash
   python manage.py init-db
   ```
4. **Create an admin user:**
    ```bash
    python manage.py create-admin <username> <password>
    ```
5. **Run the application:**
   ```bash
   python main.py
   ```