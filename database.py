import mysql.connector


def connect_db(_with_db: bool = True):
    if _with_db:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="mkkapri",
            database="oreo",
        )
    # Server-level connection (used during bootstrap before DB exists)
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mkkapri",
    )


def create_database():
    connection = connect_db(_with_db=False)
    cursor = connection.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS oreo;")
    cursor.execute("USE oreo;")

    # USERS Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            address TEXT
        );
        """
    )

    # CATEGORY Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS category (
            category_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT
        );
        """
    )

    # PRODUCTS Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            stock INT DEFAULT 0,
            category_id INT,
            details VARCHAR(255),
            image_url VARCHAR(255),
            FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE SET NULL
        );
        """
    )

    # CART Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cart (
            cart_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            product_id INT,
            quantity INT DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE
        );
        """
    )

    # ORDERS Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            total_amount DECIMAL(10,2) NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status ENUM('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled') DEFAULT 'Pending',
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """
    )

    # PAYMENT Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS payment (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            payment_method ENUM('Card', 'Cash on Delivery', 'UPI', 'Bank Transfer') DEFAULT 'Card',
            amount DECIMAL(10,2) NOT NULL,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status ENUM('Pending', 'Completed', 'Failed') DEFAULT 'Pending',
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
        );
        """
    )

    # ORDER ITEMS Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            item_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            product_id INT,
            quantity INT,
            price DECIMAL(10,2),
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE
        );
        """
    )

    # Add analytics columns to users (robust across MySQL versions)
    def _ensure_user_analytics_columns():
        def _ensure(col, ddl):
            cursor.execute("SHOW COLUMNS FROM users LIKE %s", (col,))
            exists = cursor.fetchone() is not None
            if not exists:
                cursor.execute(ddl)

        _ensure("login_count", "ALTER TABLE users ADD COLUMN login_count INT DEFAULT 0")
        _ensure("total_spent", "ALTER TABLE users ADD COLUMN total_spent DECIMAL(12,2) DEFAULT 0")
        _ensure("last_login", "ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL DEFAULT NULL")

    _ensure_user_analytics_columns()

    # RATINGS Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ratings (
            rating_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uniq_user_product (user_id, product_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE
        );
        """
    )

    connection.commit()
    cursor.close()
    connection.close()
    print("Database and tables created/updated successfully!")


# ---------- Helper functions for analytics ----------
def increment_login_counter(user_id):
    db = connect_db()
    cur = db.cursor()
    try:
        cur.execute(
            "UPDATE users SET login_count = COALESCE(login_count,0) + 1, last_login = NOW() WHERE user_id=%s",
            (user_id,),
        )
        db.commit()
    finally:
        db.close()


def add_user_spend(user_id, amount):
    db = connect_db()
    cur = db.cursor()
    try:
        cur.execute(
            "UPDATE users SET total_spent = COALESCE(total_spent,0) + %s WHERE user_id=%s",
            (amount, user_id),
        )
        db.commit()
    finally:
        db.close()


def record_order_effects(order_id):
    """Adds order.total_amount to the user's total_spent.
    Can be called after creating an order.
    """
    db = connect_db()
    cur = db.cursor()
    try:
        cur.execute("SELECT user_id, total_amount FROM orders WHERE order_id=%s", (order_id,))
        row = cur.fetchone()
        if row:
            user_id, total_amount = row
            cur.execute(
                "UPDATE users SET total_spent = COALESCE(total_spent,0) + %s WHERE user_id=%s",
                (total_amount, user_id),
            )
            db.commit()
    finally:
        db.close()


def add_or_update_rating(user_id, product_id, rating, comment=None):
    if rating < 1 or rating > 5:
        raise ValueError("rating must be between 1 and 5")
    db = connect_db()
    cur = db.cursor()
    try:
        cur.execute(
            """
            INSERT INTO ratings (user_id, product_id, rating, comment)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE rating=VALUES(rating), comment=VALUES(comment), created_at=CURRENT_TIMESTAMP
            """,
            (user_id, product_id, rating, comment),
        )
        db.commit()
    finally:
        db.close()


def get_product_rating(product_id):
    """Returns (average_rating, ratings_count) for a product."""
    db = connect_db()
    cur = db.cursor()
    try:
        cur.execute(
            "SELECT COALESCE(AVG(rating),0), COUNT(*) FROM ratings WHERE product_id=%s",
            (product_id,),
        )
        avg_rating, count = cur.fetchone()
        return float(avg_rating or 0), int(count or 0)
    finally:
        db.close()


def get_user_stats(user_id):
    """Returns dict with total_spent, login_count, last_login."""
    db = connect_db()
    cur = db.cursor()
    try:
        cur.execute(
            "SELECT COALESCE(total_spent,0), COALESCE(login_count,0), last_login FROM users WHERE user_id=%s",
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            return {"total_spent": 0.0, "login_count": 0, "last_login": None}
        total_spent, login_count, last_login = row
        return {"total_spent": float(total_spent or 0), "login_count": int(login_count or 0), "last_login": last_login}
    finally:
        db.close()


def get_most_sold_products(limit=10):
    """Returns list of (product_id, name, total_sold) sorted desc by sold quantity."""
    db = connect_db()
    cur = db.cursor()
    try:
        cur.execute(
            """
            SELECT p.product_id, p.name, COALESCE(SUM(oi.quantity), 0) AS total_sold
            FROM product p
            LEFT JOIN order_items oi ON oi.product_id = p.product_id
            GROUP BY p.product_id, p.name
            ORDER BY total_sold DESC, p.product_id ASC
            LIMIT %s
            """,
            (limit,),
        )
        return cur.fetchall()
    finally:
        db.close()


def get_least_sold_products(limit=10):
    """Returns list of (product_id, name, total_sold) sorted asc by sold quantity (includes zeros)."""
    db = connect_db()
    cur = db.cursor()
    try:
        cur.execute(
            """
            SELECT p.product_id, p.name, COALESCE(SUM(oi.quantity), 0) AS total_sold
            FROM product p
            LEFT JOIN order_items oi ON oi.product_id = p.product_id
            GROUP BY p.product_id, p.name
            ORDER BY total_sold ASC, p.product_id ASC
            LIMIT %s
            """,
            (limit,),
        )
        return cur.fetchall()
    finally:
        db.close()
create_database()
