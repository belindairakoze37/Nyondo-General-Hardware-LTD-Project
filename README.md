# Nyondo General Hardware Management System

## Project Overview

Nyondo General Hardware Management System is a Django-based business management application developed to help manage stock, sales, customers, and financial transactions in a hardware business environment.

The system simplifies daily operations by providing tools for inventory tracking, sales processing, customer management, reporting, and payment handling.

---

# Objectives

The main objectives of the system are:

* To improve stock management efficiency.
* To reduce manual record keeping.
* To simplify sales processing.
* To generate accurate business reports.
* To help monitor customer transactions and balances.

---

# Features

## Authentication and User Management

* Secure login and logout system.
* Role-based access control.
* User account management.

## Stock Management

* Add new stock items.
* Update stock quantities.
* Track available inventory.
* Monitor low stock items.

## Sales Management

* Record customer sales.
* Automatic total calculations.
* Generate sales receipts.
* Track completed transactions.

## Customer Management

* Add and manage customer records.
* Store customer contact information.
* Monitor customer purchase history.

## Payment and Deposit Management

* Record deposits and payments.
* Calculate remaining balances.
* Support multiple payment methods.

## Reporting

* Sales reports.
* Stock reports.
* Financial summaries.
* Printable receipts.

---

# Technologies Used

* Python
* Django
* HTML5
* CSS3
* Bootstrap
* SQLite
* JavaScript

---

# System Requirements

Before running the project, ensure the following are installed:

* Python 3.x
* pip
* Git
* Virtual environment (recommended)

---

# Installation Guide

## 1. Clone the Repository

```bash
git clone https://github.com/belindairakoze37/Nyondo-General-Hardware-LTD-Project.git
```

## 2. Open the Project Folder

```bash
cd nyondo_project
```

## 3. Create a Virtual Environment

```bash
python -m venv venv
```

## 4. Activate the Virtual Environment

### Windows

```bash
 source venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

## 5. Install Dependencies

```bash
pip install -r requirements.txt
```

## 6. Apply Migrations

```bash
python manage.py migrate
```

## 7. Run the Development Server

```bash
python manage.py runserver
```

## 8. Open in Browser

```text
http://127.0.0.1:8000/
```

---

# Project Structure

```text
NYONDOHARDWARE/              
│
├── nyondo_project/         
│   ├── nyondo_project/      
│   ├── static/
│   ├── templates/
│   ├── users/               
│   ├── web/                 
│   ├── .gitignore
│   ├── db.sqlite3
│   ├── manage.py
│   ├── README.md
│   ├── requirements.txt
│   └── venv/
```

---

# Future Improvements

Possible future enhancements include:

* SMS or email notifications.
* Advanced analytics dashboard.
* Barcode scanning integration.
* Online payment integration.
* Cloud deployment.

---

# Challenges Solved During Development

* Managing stock updates after sales.
* Implementing secure authentication.
* Handling balance calculations.
* Designing responsive user interfaces.
* Generating printable receipts and reports.

---

# Author

Developed by Belinda Irakoze.

---

# Conclusion

Nyondo General Hardware Management System was developed to improve business efficiency and simplify hardware shop operations through digital inventory and sales management.

The system demonstrates practical application of Django web development concepts including database management, authentication, business logic implementation, and responsive interface design.
