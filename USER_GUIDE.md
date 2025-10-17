# Ajyad Accountant - User Guide

Welcome to Ajyad Accountant! This guide will help you understand and use the application to manage your business effectively.

---

## 1. Installation

1.  Download the installer for your operating system (Windows, macOS, or Linux) from the official source.
2.  Run the installer and follow the on-screen instructions.
3.  Once the installation is complete, you can launch Ajyad Accountant from your applications menu or desktop shortcut.

The first time you run the application, it will automatically set up the local database for you.

## 2. Getting Started: Your First Login

The first time you launch the application, you will be prompted to create an **Admin** user. This user has full access to all features.

1.  On the first launch, an "Admin User Creation" screen will appear.
2.  Enter your desired username and a strong password.
3.  Click "Create Admin".

After creating the admin user, you will be taken to the login screen.

### Language Selection

On the login screen, you can choose your preferred language (English or Arabic) from a dropdown menu before logging in. The application interface will be translated accordingly, and the layout will automatically switch to Right-to-Left for Arabic.

---

## 3. Walkthrough: Creating a Sale and Invoicing a Customer

This walkthrough will guide you through a common business workflow: adding a new product, creating a sales order for a customer, and generating an invoice.

### Step 1: Add a Product

First, let's add a product to our inventory.

1.  Log in with an **Admin** or **Sales** account.
2.  Navigate to the **Products** tab.
3.  Click the **"Add Product"** button.
4.  Fill in the product details:
    *   **Name:** e.g., "Wireless Mouse"
    *   **Description:** e.g., "Ergonomic wireless mouse"
    *   **Price:** Enter the price in cents (e.g., `2500` for $25.00).
    *   **Stock Quantity:** The initial quantity you have on hand (e.g., `50`).
    *   **Low Stock Threshold:** The quantity at which you want to receive a low stock alert (e.g., `10`).
5.  Click **"Save"**. Your new product is now in the inventory.

### Step 2: Add a Customer

Now, let's add the customer who will be buying the product.

1.  Navigate to the **Customers** tab.
2.  Click the **"Add Customer"** button.
3.  Fill in the customer's details (Name, Email, Phone, etc.).
4.  Click **"Save"**.

### Step 3: Create a Sales Order

With a product and customer in the system, you can now create a sale.

1.  Navigate to the **Sales** tab.
2.  Click the **"Create Sales Order"** button.
3.  In the new window:
    *   Select the customer you just created from the dropdown list.
    *   Click **"Add Item"**.
    *   Select the "Wireless Mouse" from the product list and enter the quantity the customer wants to buy (e.g., `2`).
    *   The total amount will be calculated automatically.
4.  Click **"Create Order"**. The stock for "Wireless Mouse" will be automatically reduced by 2.

### Step 4: Create an Invoice

Finally, let's create an invoice from the sales order.

1.  Navigate to the **Invoicing** tab.
2.  You should see the sales order you just created listed.
3.  Click the **"Create Invoice"** button next to the order.
4.  Set a **Due Date** for the payment.
5.  You can set the initial **Status** (e.g., "Sent").
6.  Click **"Save Invoice"**. The invoice is now created and linked to the sale. You can track its status (e.g., mark it as "Paid" later).

---

## 4. Core Features Overview

### User Roles
-   **Admin:** Full access to all features, including user management.
-   **Accountant:** Access to accounting, purchasing, and reporting. Cannot manage users.
-   **Sales:** Access to sales, customer, and inventory modules.

### Modules
-   **Dashboard:** An overview of your business with key metrics and notifications.
-   **Customers & Suppliers:** Manage your business contacts and view their transaction history.
-   **Products:** Manage your inventory, set stock levels, and define low-stock alerts.
-   **Sales & Purchases:** Create and manage sales and purchase orders.
-   **Accounting:** Includes the Chart of Accounts for managing accounts and a Journal Entry system for double-entry bookkeeping.
-   **Reporting:** Generate key financial reports like the Profit & Loss statement and Balance Sheet. You can **Export** reports to PDF and Excel.
-   **Notifications:** Displays alerts for low stock, overdue invoices, etc.

### Security
-   **Audit Trail:** The application logs all important user actions (e.g., creating an order, logging in) for security and accountability. This feature is accessible to Admins.