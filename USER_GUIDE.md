# Ajyad Accountant - User Guide

Welcome to Ajyad Accountant! This guide will help you get started with the application.

## Installation

To install Ajyad Accountant, you will need to have Python installed on your computer. You can download it from [python.org](https://www.python.org/downloads/).

Once you have Python installed, follow these steps:

1.  Download the application files.
2.  Open a terminal or command prompt and navigate to the application directory.
3.  Install the required dependencies by running the following command:

    ```
    pip install -r requirements.txt
    ```

4.  Initialize the database by running the following command:

    ```
    python manage.py init-db
    ```

5.  Create an admin user by running the following command:

    ```
    python manage.py create-admin <username> <password>
    ```

    Replace `<username>` and `<password>` with your desired username and password.

## Getting Started

To start the application, run the following command:

```
python main.py
```

You will be prompted to log in with the username and password you created in the previous step.

## Features

### Dashboard

The dashboard provides an overview of your business, including key metrics and notifications.

### Customers

The Customers tab allows you to manage your customers. You can add, edit, and delete customers.

### Suppliers

The Suppliers tab allows you to manage your suppliers. You can add, edit, and delete suppliers.

### Products

The Products tab allows you to manage your products. You can add, edit, and delete products. You can also set a low stock threshold to receive notifications when a product is running low.

### Sales

The Sales tab allows you to create and manage sales orders.

### Purchases

The Purchases tab allows you to create and manage purchase orders.

### Chart of Accounts

The Chart of Accounts tab allows you to manage your accounts. You can add, edit, and delete accounts.

### Journal Entries

The Journal Entries tab allows you to create and manage journal entries.

### Reporting

The Reporting tab allows you to generate various reports, including:

*   Profit & Loss
*   Balance Sheet
*   Inventory Reports

### Notifications

The Notifications tab displays important alerts, including:

*   Low stock notifications
*   Overdue invoices
*   Upcoming payment dues

### Audit Trail

The application now includes a comprehensive audit trail that logs all important events, such as:

*   Sales order creation
*   Purchase order creation
*   User login attempts
*   Manual stock adjustments

This provides a complete history of all actions performed in the application, which can be useful for auditing and security purposes.

### Exporting Reports

You can export reports to PDF and Excel by clicking the "Export to PDF" or "Export to Excel" buttons in the Reporting tab. This allows you to easily share reports with others or use them in other applications.