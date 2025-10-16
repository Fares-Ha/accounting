# Ajyad Accountant Desktop Application

This is a full-featured, cross-platform desktop application for accounting, inventory, and customer management, built with Python and PyQt6. It is designed to be offline-first, with a local SQLite database, and supports both English and Arabic.

## Features

- **Bilingual Interface:** Supports English and Arabic, including Right-to-Left (RTL) layout for Arabic.
- **Role-Based Access Control:** Pre-defined roles (Admin, Accountant, Sales) with different permissions.
- **Full-Featured Accounting:** Double-entry accounting system, chart of accounts, journal entries, and financial reporting (Profit & Loss, Balance Sheet).
- **Inventory Management:** Manage products, categories, stock levels, and receive low-stock alerts.
- **Sales & Purchasing:** Create and manage sales and purchase orders.
- **Customer & Supplier Management:** Maintain a directory of customers and suppliers.
- **Reporting & Export:** Generate reports for sales, inventory, and finances. Export reports to PDF and Excel.
- **Global Search:** Quickly find customers, products, and invoices.
- **Notifications:** Get alerts for important events like overdue invoices and low stock.

## Architecture

The application follows a clean architecture pattern, separating the code into three main layers:

- **`app/ui` (Presentation Layer):** Contains all the PyQt6 widgets and windows that make up the user interface. This layer is responsible for displaying data and capturing user input.
- **`app/core` (Service/Business Logic Layer):** Contains the application's business logic. Services like `SalesService` or `ReportingService` orchestrate the application's functionality, but they do not directly interact with the database.
- **`app/database` (Data Access Layer):** Responsible for all communication with the SQLite database. It uses SQLAlchemy for object-relational mapping (ORM).

This separation of concerns makes the application easier to maintain, test, and scale.

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

## Running Tests

To run the test suite, use the following command:

```bash
python -m unittest discover tests
```
*Note: The test suite is currently experiencing issues related to Python's import system in some environments. A custom test runner may be required if you encounter problems.*

## Building from Source

The application can be packaged into a standalone executable using PyInstaller. A convenience script is provided to automate this process.

```bash
# Make the script executable
chmod +x package.sh

# Run the script to create the package
./package.sh
```
The final executable will be located in the `dist` directory.

## Contributing

Contributions are welcome! If you would like to contribute to the project, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and ensure the test suite passes.
4.  Submit a pull request with a clear description of your changes.