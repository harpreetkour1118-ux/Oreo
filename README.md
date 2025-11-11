SOFTWARE REQUIREMENTS & DESIGN DOCUMENT (SRDD)

Prepared by: Manoj Kapri
Devlopers: Shrezal, Sumit, Harpreet, Heneli

1. Introduction
   1.1 Purpose of the System

The OREO Online Shopping System is designed to provide users with a seamless platform for browsing electronic products, adding them to a cart, and completing secure checkout. The system enables both customers and administrators to interact with the platform efficiently through dedicated interfaces.

This documentation outlines the system’s architecture, functional requirements, database schema, UML diagrams, interface behavior, and implementation details.

1.2 Scope

The system supports:

User registration & login

Browsing electronic products

Shopping cart management

Secure checkout and order placement

Admin panel for managing products

Database-driven persistent storage

The software is built using Python (Tkinter) for the GUI and MySQL for backend storage.

1.3 Technologies Used

Python 3.10+

Tkinter (GUI Framework)

MySQL Database

PIL / Pillow (Image handling)

OOP-based structure

2. System Overview
   2.1 System Users

The system has two types of users:

Customers

Register and login

View products

Add to cart

Update cart items

Checkout using payment details

Place orders

Administrator

Add products

Update product information

Delete products

View product list

3. Functional Requirements
   3.1 User Functional Requirements
   Feature Description
   Register User can create an account with name, email, password, address, phone.
   Login Authenticates using username & password.
   Browse Products View all products in scrollable grid.
   Add to Cart Add product with quantity.
   Update Cart Increase quantity or remove items.
   Checkout Process card payment and place order.
   Logout Secure session termination.
   3.2 Admin Functional Requirements
   Feature Description
   Add Product Insert new product with name, price, description, image.
   Update Product Edit product details based on product ID.
   Delete Product Remove product by ID.
   View Product Table See all products in a treeview table.
4. Non-Functional Requirements
   4.1 Performance

GUI loads within 3 seconds.

Product grid supports unlimited products using scrollable canvas.

4.2 Reliability

MySQL ensures ACID-compliant records for order and payment.

4.3 Security

Password input concealed with \* masking.

Payment information validated before processing.

4.4 Usability

GUI uses clean layout, icons, and readable fonts (Arial, 10–14pt).

Admin panel uses simple navigational windows.

5. System Architecture
   5.1 High-Level Architecture Diagram
   +---------------+ +-------------------+
   | GUI Layer | <-----> | Application |
   | (Tkinter UI) | | Logic (Python) |
   +---------------+ +-------------------+
   | |
   v v
   +--------------------------+
   | MySQL Database |
   +--------------------------+

5.2 Major System Modules

login.py → Handles registration & login

oreo.py / Dashboard → Displays products and cart access

cart.py → Manages cart operations

checkout.py → Handles final payment and order storing

admin.py → Add/update/delete products

database.py → Creates tables and schema

6.  UML Diagrams
    6.1 USE CASE DIAGRAM
    +----------------------+
    | Admin |
    +----------------------+
    / | \
     / | \
     Add Product Update Product Delete Product
    \ | /
    \ | /
    View Product Table

                        +----------------------+
                        |        User          |
                        +----------------------+
                              |        |
              +---------------+        +-----------------+
              |                                    |

    Register ---> Login ---> View Products ---> Add to Cart
    |
    Manage Cart
    |
    Checkout
    |
    Process Payment
    |
    Place Order

    6.2 CLASS DIAGRAM
    +----------------------+
    | User |
    +----------------------+
    | user_id |
    | username |
    | email |
    | password |
    | phone |
    | address |
    +----------------------+
    | +login() |
    | +register() |
    +----------------------+

+----------------------+
| Product |
+----------------------+
| product_id |
| name |
| description |
| price |
| stock |
| category_id |
| image_url |
+----------------------+
| +addProduct() |
| +updateProduct() |
| +deleteProduct() |
+----------------------+

+----------------------+
| Cart |
+----------------------+
| cart_id |
| user_id |
| product_id |
| quantity |
+----------------------+
| +load_cart() |
| +add_quantity() |
| +remove_item() |
+----------------------+

+----------------------+
| Order |
+----------------------+
| order_id |
| user_id |
| total_amount |
| date |
| status |
+----------------------+

+----------------------+
| OrderItem |
+----------------------+
| item_id |
| order_id |
| product_id |
| quantity |
| price |
+----------------------+

+---------------------------+
| Dashboard (GUI) |
+---------------------------+
| user_id |
| username |
+---------------------------+
| +load_products() |
| +add_to_cart() |
| +open_cart() |
+---------------------------+

+---------------------------+
| CartWindow (GUI) |
+---------------------------+
| +load_cart() |
| +checkout() |
+---------------------------+

+---------------------------+
| CheckoutWindow (GUI) |
+---------------------------+
| +load_cart() |
| +process_checkout() |
+---------------------------+

7. Database Design

Your actual database schema (from database.py):

7.1 Database Tables
users
Field Type
user_id INT PK
username VARCHAR
email VARCHAR
password VARCHAR
phone VARCHAR
address TEXT
category
Field Type
category_id INT PK
name VARCHAR
description TEXT
product
Field Type
product_id INT PK
name VARCHAR
description TEXT
price DECIMAL
stock INT
category_id FK
details VARCHAR
image_url VARCHAR
cart
Field Type
cart_id INT PK
user_id FK
product_id FK
quantity INT
orders
Field Type
order_id INT PK
user_id FK
total_amount DECIMAL
order_date TIMESTAMP
status ENUM
order_items
Field Type
item_id INT PK
order_id FK
product_id FK
quantity INT
price DECIMAL
payment
Field Type
payment_id INT PK
order_id FK
payment_method ENUM
amount DECIMAL
payment_date TIMESTAMP
status ENUM 8. Detailed Module Documentation
8.1 login.py
Features:

Login user

Registration

Validation

Switch between login and register frames

Key Functions:

login_user() → verifies username & password

register_user() → inserts new user into database

8.2 oreo.py (Dashboard)
Features:

Displays products

Scrollable grid

Add to cart

Access cart window

Key Methods:

load_products()

add_to_cart()

open_cart()
8.3 cart.py
Features:

View cart items

Increase quantity

Remove item

Summary on the right

Go to checkout

Key Methods:

load_cart()

add_quantity()

remove_item()

checkout()

8.4 checkout.py
Features:

Displays receipt

Enter payment info

Insert into order + order_items

Clear cart

Key Methods:

load_cart()

process_checkout()

8.5 admin.py
Features:

Add, update, delete product

View product list

Auto-load category IDs

Key Windows:

Add Product

Update Product

Delete Product

9. User Interface Layout

(Screenshots can be added if you upload them.)

10. System Flow
    10.1 Customer Flow
    Register → Login → Dashboard → Add to Cart → View Cart → Checkout → Order Created

10.2 Admin Flow
Admin Panel → Add/Update/Delete Product → View Product Table

11. Future Enhancements

Add admin authentication

Add search bar for products

Add product categories on dashboard

Implement password hashing

Add online payment integration

Order tracking status UI

12. Conclusion

The OREO Online Shopping System provides a complete, functional e-commerce solution for electronic products. It demonstrates strong software engineering principles including layered architecture, GUI-based interaction, database persistence, and structured modular development.
