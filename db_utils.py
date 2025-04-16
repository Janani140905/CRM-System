import sqlite3
import os
import pandas as pd
import hashlib
import time
import random
from datetime import datetime, timedelta

# Database file path
DB_FILE = 'crm_database.db'

def initialize_database():
    """Initialize the SQLite database if it doesn't exist."""
    # Check if database file exists
    db_exists = os.path.exists(DB_FILE)
    
    # Connect to database (will create it if it doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if not db_exists:
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
        ''')
        
        # Create products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            stock INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
        ''')
        
        # Create orders table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Create complaints table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            admin_response TEXT,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
        ''')
        
        # Create ratings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            review TEXT,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Insert admin user
        admin_password = hashlib.sha256('admin'.encode()).hexdigest()
        cursor.execute('''
        INSERT INTO users (username, email, password, is_admin, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@example.com', admin_password, True, datetime.now()))
        
        # Insert sample products
        sample_products = [
            (1, "Laptop Pro", "Electronics", 1299.99, "High-performance laptop for professionals", 15, datetime.now()),
            (2, "Smartphone X", "Electronics", 999.99, "Latest smartphone with advanced features", 25, datetime.now()),
            (3, "Tablet Air", "Electronics", 499.99, "Lightweight tablet for entertainment and productivity", 20, datetime.now()),
            (4, "Wireless Headphones", "Audio", 249.99, "Noise-cancelling wireless headphones", 30, datetime.now()),
            (5, "Smart Watch", "Wearables", 349.99, "Smart watch with health monitoring features", 18, datetime.now()),
            (6, "4K Monitor", "Computer Accessories", 399.99, "Ultra HD 4K monitor for crisp visuals", 10, datetime.now()),
            (7, "Gaming Mouse", "Computer Accessories", 79.99, "High-precision gaming mouse", 45, datetime.now()),
            (8, "Mechanical Keyboard", "Computer Accessories", 129.99, "RGB mechanical keyboard with custom switches", 25, datetime.now()),
            (9, "Bluetooth Speaker", "Audio", 149.99, "Portable Bluetooth speaker with deep bass", 30, datetime.now()),
            (10, "External SSD", "Storage", 199.99, "1TB External SSD with high-speed transfer", 20, datetime.now()),
            (11, "Wireless Charger", "Accessories", 59.99, "Fast wireless charger compatible with all devices", 35, datetime.now()),
            (12, "USB Hub", "Computer Accessories", 49.99, "Multi-port USB hub with pass-through charging", 40, datetime.now()),
            (13, "Power Bank", "Accessories", 89.99, "20,000mAh power bank for multiple charges", 50, datetime.now()),
            (14, "Camera DSLR", "Photography", 799.99, "Professional DSLR camera with 24MP sensor", 12, datetime.now()),
            (15, "Fitness Tracker", "Wearables", 129.99, "Water-resistant fitness tracker with heart rate monitor", 25, datetime.now()),
            (16, "Smart Home Hub", "Smart Home", 199.99, "Central hub for all smart home devices", 15, datetime.now()),
            (17, "Wireless Router", "Networking", 149.99, "High-speed wireless router with wide coverage", 20, datetime.now()),
            (18, "Portable Printer", "Office", 179.99, "Compact portable printer for documents and photos", 18, datetime.now()),
            (19, "VR Headset", "Entertainment", 399.99, "Immersive virtual reality headset", 10, datetime.now()),
            (20, "Drone Pro", "Gadgets", 799.99, "4K camera drone with 30-minute flight time", 8, datetime.now())
        ]
        
        cursor.executemany('''
        INSERT INTO products (id, name, category, price, description, stock, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_products)
        
        # Commit the changes
        conn.commit()
    
    # Close the connection
    conn.close()

def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def get_all_users():
    """Get all users from the database."""
    conn = get_db_connection()
    users = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return users

def get_all_products():
    """Get all products from the database."""
    conn = get_db_connection()
    products = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    return products

def get_all_orders():
    """Get all orders from the database."""
    conn = get_db_connection()
    orders = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    return orders

def get_all_complaints():
    """Get all complaints from the database."""
    conn = get_db_connection()
    complaints = pd.read_sql_query("SELECT * FROM complaints", conn)
    conn.close()
    return complaints

def get_all_ratings():
    """Get all ratings from the database."""
    conn = get_db_connection()
    ratings = pd.read_sql_query("SELECT * FROM ratings", conn)
    conn.close()
    return ratings

def get_user_by_username(username):
    """Get a user by username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Get a user by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_product_by_id(product_id):
    """Get a product by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return dict(product) if product else None

def get_order_by_id(order_id):
    """Get an order by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    return dict(order) if order else None

def get_complaint_by_id(complaint_id):
    """Get a complaint by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    complaint = cursor.fetchone()
    conn.close()
    return dict(complaint) if complaint else None

def get_user_orders(user_id):
    """Get all orders for a user."""
    conn = get_db_connection()
    orders = pd.read_sql_query("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", 
                               conn, params=(user_id,))
    conn.close()
    return orders

def get_user_complaints(user_id):
    """Get all complaints for a user."""
    conn = get_db_connection()
    complaints = pd.read_sql_query("SELECT * FROM complaints WHERE user_id = ? ORDER BY created_at DESC", 
                                 conn, params=(user_id,))
    conn.close()
    return complaints

def get_user_ratings(user_id):
    """Get all ratings for a user."""
    conn = get_db_connection()
    ratings = pd.read_sql_query("SELECT * FROM ratings WHERE user_id = ? ORDER BY created_at DESC", 
                              conn, params=(user_id,))
    conn.close()
    return ratings

def create_user(username, email, password, is_admin=False):
    """Create a new user in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if username or email already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists"
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return False, "Email already exists"
    
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Insert the new user
    try:
        cursor.execute('''
        INSERT INTO users (username, email, password, is_admin, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, email, hashed_password, is_admin, datetime.now()))
        
        # Get the ID of the newly created user
        user_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return True, user_id
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def authenticate_user(username, password):
    """Authenticate a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the user
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user:
        # Hash the password and compare
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user['password'] == hashed_password:
            conn.close()
            return True, dict(user)
    
    conn.close()
    return False, None

def add_order(user_id, product_id, quantity):
    """Add a new order to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get product information
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    
    if not product:
        conn.close()
        return False, "Product not found"
    
    # Check if we have enough stock
    if product['stock'] < quantity:
        conn.close()
        return False, f"Not enough stock. Available: {product['stock']}"
    
    # Calculate total price
    total_price = product['price'] * quantity
    
    # Create new order
    try:
        cursor.execute('''
        INSERT INTO orders (user_id, product_id, quantity, total_price, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, product_id, quantity, total_price, "Processing", datetime.now()))
        
        # Get the ID of the newly created order
        order_id = cursor.lastrowid
        
        # Update product stock
        cursor.execute('''
        UPDATE products SET stock = stock - ? WHERE id = ?
        ''', (quantity, product_id))
        
        conn.commit()
        conn.close()
        return True, order_id
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def add_complaint(user_id, order_id, subject, description):
    """Add a new complaint to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if order exists and belongs to the user
    cursor.execute("SELECT * FROM orders WHERE id = ? AND user_id = ?", (order_id, user_id))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        return False, "Order not found or does not belong to this user"
    
    # Create new complaint
    try:
        now = datetime.now()
        cursor.execute('''
        INSERT INTO complaints (user_id, order_id, subject, description, status, admin_response, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, order_id, subject, description, "Pending", None, now, now))
        
        # Get the ID of the newly created complaint
        complaint_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return True, complaint_id
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def add_rating(user_id, product_id, rating, review):
    """Add a new product rating to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product exists
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    if not cursor.fetchone():
        conn.close()
        return False, "Product not found"
    
    # Check if user has already rated this product
    cursor.execute("SELECT * FROM ratings WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    existing_rating = cursor.fetchone()
    
    try:
        if existing_rating:
            # Update existing rating
            cursor.execute('''
            UPDATE ratings SET rating = ?, review = ?, created_at = ?
            WHERE user_id = ? AND product_id = ?
            ''', (rating, review, datetime.now(), user_id, product_id))
            
            conn.commit()
            conn.close()
            return True, "Rating updated"
        else:
            # Create new rating
            cursor.execute('''
            INSERT INTO ratings (user_id, product_id, rating, review, created_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, product_id, rating, review, datetime.now()))
            
            # Get the ID of the newly created rating
            rating_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            return True, rating_id
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def respond_to_complaint(complaint_id, response):
    """Update a complaint with admin response."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if complaint exists
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    if not cursor.fetchone():
        conn.close()
        return False, "Complaint not found"
    
    # Update complaint
    try:
        cursor.execute('''
        UPDATE complaints SET status = ?, admin_response = ?, updated_at = ?
        WHERE id = ?
        ''', ("Resolved", response, datetime.now(), complaint_id))
        
        conn.commit()
        conn.close()
        return True, "Complaint updated"
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def search_products(query, category=None, min_price=None, max_price=None):
    """Search for products based on query and filters."""
    conn = get_db_connection()
    
    # Build the query dynamically
    sql_query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    # Apply search query if provided
    if query:
        sql_query += " AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ?)"
        query_param = f"%{query.lower()}%"
        params.extend([query_param, query_param])
    
    # Apply category filter if provided
    if category and category != "All Categories":
        sql_query += " AND category = ?"
        params.append(category)
    
    # Apply price filters if provided
    if min_price is not None:
        sql_query += " AND price >= ?"
        params.append(min_price)
    
    if max_price is not None:
        sql_query += " AND price <= ?"
        params.append(max_price)
    
    # Execute the query
    products = pd.read_sql_query(sql_query, conn, params=params)
    
    conn.close()
    return products

def generate_sample_orders():
    """Generate sample orders for testing (only if no orders exist)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if any orders exist
    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]
    
    # Check if there are non-admin users
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
    user_count = cursor.fetchone()[0]
    
    if order_count == 0 and user_count > 0:
        # Get non-admin users
        cursor.execute("SELECT id FROM users WHERE is_admin = 0")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        # Get all products
        cursor.execute("SELECT id, price FROM products")
        products = cursor.fetchall()
        
        # Get the current date
        now = datetime.now()
        
        # For each user, create 1-3 random orders
        order_id = 1
        
        for user_id in user_ids:
            num_orders = random.randint(1, 3)
            
            for _ in range(num_orders):
                # Random product
                product = random.choice(products)
                product_id = product[0]
                product_price = product[1]
                
                # Random quantity between 1 and 3
                quantity = random.randint(1, 3)
                
                # Calculate total price
                total_price = product_price * quantity
                
                # Random date in the last 90 days
                days_ago = random.randint(0, 90)
                order_date = now - timedelta(days=days_ago)
                
                # Random status
                status = random.choice(["Delivered", "Processing", "Shipped"])
                
                # Insert order
                cursor.execute('''
                INSERT INTO orders (id, user_id, product_id, quantity, total_price, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (order_id, user_id, product_id, quantity, total_price, status, order_date))
                
                order_id += 1
        
        conn.commit()
    
    conn.close()


def update_product(product_id, name, category, price, stock, description):
    """Update a product in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product exists
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    if not cursor.fetchone():
        conn.close()
        return False, "Product not found"
    
    # Update product
    try:
        cursor.execute('''
        UPDATE products SET name = ?, category = ?, price = ?, stock = ?, description = ?
        WHERE id = ?
        ''', (name, category, price, stock, description, product_id))
        
        conn.commit()
        conn.close()
        return True, "Product updated successfully"
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)