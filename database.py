import streamlit as st
import pandas as pd
import random
import string
import time
from datetime import datetime, timedelta

def initialize_database():
    """Initialize the in-memory database if it hasn't been initialized yet."""
    if "db" not in st.session_state:
        st.session_state.db = {}
        
        # Create users table with admin user
        users_df = pd.DataFrame({
            "id": [1],
            "username": ["admin"],
            "email": ["admin@example.com"],
            "password": ["8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"],  # admin
            "is_admin": [True],
            "created_at": [pd.Timestamp.now()]
        })
        
        # Create products table
        products_df = pd.DataFrame({
            "id": list(range(1, 21)),
            "name": [
                "Laptop Pro", "Smartphone X", "Tablet Air", "Wireless Headphones", 
                "Smart Watch", "4K Monitor", "Gaming Mouse", "Mechanical Keyboard",
                "Bluetooth Speaker", "External SSD", "Wireless Charger", "USB Hub",
                "Power Bank", "Camera DSLR", "Fitness Tracker", "Smart Home Hub",
                "Wireless Router", "Portable Printer", "VR Headset", "Drone Pro"
            ],
            "category": [
                "Electronics", "Electronics", "Electronics", "Audio",
                "Wearables", "Computer Accessories", "Computer Accessories", "Computer Accessories",
                "Audio", "Storage", "Accessories", "Computer Accessories",
                "Accessories", "Photography", "Wearables", "Smart Home",
                "Networking", "Office", "Entertainment", "Gadgets"
            ],
            "price": [
                1299.99, 999.99, 499.99, 249.99,
                349.99, 399.99, 79.99, 129.99,
                149.99, 199.99, 59.99, 49.99,
                89.99, 799.99, 129.99, 199.99,
                149.99, 179.99, 399.99, 799.99
            ],
            "description": [
                "High-performance laptop for professionals", "Latest smartphone with advanced features",
                "Lightweight tablet for entertainment and productivity", "Noise-cancelling wireless headphones",
                "Smart watch with health monitoring features", "Ultra HD 4K monitor for crisp visuals",
                "High-precision gaming mouse", "RGB mechanical keyboard with custom switches",
                "Portable Bluetooth speaker with deep bass", "1TB External SSD with high-speed transfer",
                "Fast wireless charger compatible with all devices", "Multi-port USB hub with pass-through charging",
                "20,000mAh power bank for multiple charges", "Professional DSLR camera with 24MP sensor",
                "Water-resistant fitness tracker with heart rate monitor", "Central hub for all smart home devices",
                "High-speed wireless router with wide coverage", "Compact portable printer for documents and photos",
                "Immersive virtual reality headset", "4K camera drone with 30-minute flight time"
            ],
            "stock": [15, 25, 20, 30, 18, 10, 45, 25, 30, 20, 35, 40, 50, 12, 25, 15, 20, 18, 10, 8],
            "created_at": [pd.Timestamp.now()] * 20
        })
        
        # Create empty orders table
        orders_df = pd.DataFrame({
            "id": [],
            "user_id": [],
            "product_id": [],
            "quantity": [],
            "total_price": [],
            "status": [],
            "created_at": []
        })
        
        # Create empty complaints table
        complaints_df = pd.DataFrame({
            "id": [],
            "user_id": [],
            "order_id": [],
            "subject": [],
            "description": [],
            "status": [],
            "admin_response": [],
            "created_at": [],
            "updated_at": []
        })
        
        # Create empty ratings table
        ratings_df = pd.DataFrame({
            "id": [],
            "user_id": [],
            "product_id": [],
            "rating": [],
            "review": [],
            "created_at": []
        })
        
        # Store DataFrames in session state
        st.session_state.db["users"] = users_df
        st.session_state.db["products"] = products_df
        st.session_state.db["orders"] = orders_df
        st.session_state.db["complaints"] = complaints_df
        st.session_state.db["ratings"] = ratings_df

def generate_sample_orders():
    """Generate sample orders for testing (only if no orders exist)."""
    if len(st.session_state.db["orders"]) == 0 and len(st.session_state.db["users"]) > 1:
        orders = []
        order_id = 1
        
        # Get non-admin users
        users = st.session_state.db["users"][~st.session_state.db["users"]["is_admin"]]
        products = st.session_state.db["products"]
        
        # Get the current date
        now = pd.Timestamp.now()
        
        # For each user, create 1-3 random orders
        for user_id in users["id"].values:
            num_orders = random.randint(1, 3)
            
            for _ in range(num_orders):
                # Random product
                product = products.sample(1).iloc[0]
                product_id = product["id"]
                
                # Random quantity between 1 and 3
                quantity = random.randint(1, 3)
                
                # Calculate total price
                total_price = product["price"] * quantity
                
                # Random date in the last 90 days
                days_ago = random.randint(0, 90)
                order_date = now - pd.Timedelta(days=days_ago)
                
                # Random status
                status = random.choice(["Delivered", "Processing", "Shipped"])
                
                orders.append({
                    "id": order_id,
                    "user_id": user_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "total_price": total_price,
                    "status": status,
                    "created_at": order_date
                })
                
                order_id += 1
        
        if orders:
            st.session_state.db["orders"] = pd.DataFrame(orders)

def get_user_by_id(user_id):
    """Get a user by ID."""
    users_df = st.session_state.db["users"]
    user = users_df[users_df["id"] == user_id]
    
    if not user.empty:
        return user.iloc[0]
    return None

def get_product_by_id(product_id):
    """Get a product by ID."""
    products_df = st.session_state.db["products"]
    product = products_df[products_df["id"] == product_id]
    
    if not product.empty:
        return product.iloc[0]
    return None

def get_order_by_id(order_id):
    """Get an order by ID."""
    orders_df = st.session_state.db["orders"]
    order = orders_df[orders_df["id"] == order_id]
    
    if not order.empty:
        return order.iloc[0]
    return None

def get_complaint_by_id(complaint_id):
    """Get a complaint by ID."""
    complaints_df = st.session_state.db["complaints"]
    complaint = complaints_df[complaints_df["id"] == complaint_id]
    
    if not complaint.empty:
        return complaint.iloc[0]
    return None

def get_user_orders(user_id):
    """Get all orders for a user."""
    orders_df = st.session_state.db["orders"]
    return orders_df[orders_df["user_id"] == user_id].sort_values(by="created_at", ascending=False)

def get_user_complaints(user_id):
    """Get all complaints for a user."""
    complaints_df = st.session_state.db["complaints"]
    return complaints_df[complaints_df["user_id"] == user_id].sort_values(by="created_at", ascending=False)

def get_user_ratings(user_id):
    """Get all ratings for a user."""
    ratings_df = st.session_state.db["ratings"]
    return ratings_df[ratings_df["user_id"] == user_id].sort_values(by="created_at", ascending=False)

def add_order(user_id, product_id, quantity):
    """Add a new order to the database."""
    orders_df = st.session_state.db["orders"]
    products_df = st.session_state.db["products"]
    
    # Get product information
    product = products_df[products_df["id"] == product_id]
    
    if product.empty:
        return False, "Product not found"
    
    product = product.iloc[0]
    
    # Check if we have enough stock
    if product["stock"] < quantity:
        return False, f"Not enough stock. Available: {product['stock']}"
    
    # Calculate total price
    total_price = product["price"] * quantity
    
    # Create new order
    new_order_id = 1 if len(orders_df) == 0 else orders_df["id"].max() + 1
    
    new_order = pd.DataFrame({
        "id": [new_order_id],
        "user_id": [user_id],
        "product_id": [product_id],
        "quantity": [quantity],
        "total_price": [total_price],
        "status": ["Processing"],
        "created_at": [pd.Timestamp.now()]
    })
    
    # Add order to database
    st.session_state.db["orders"] = pd.concat([orders_df, new_order], ignore_index=True)
    
    # Update product stock
    products_df.loc[products_df["id"] == product_id, "stock"] -= quantity
    st.session_state.db["products"] = products_df
    
    return True, new_order_id

def add_complaint(user_id, order_id, subject, description):
    """Add a new complaint to the database."""
    complaints_df = st.session_state.db["complaints"]
    orders_df = st.session_state.db["orders"]
    
    # Check if order exists and belongs to the user
    order = orders_df[(orders_df["id"] == order_id) & (orders_df["user_id"] == user_id)]
    
    if order.empty:
        return False, "Order not found or does not belong to this user"
    
    # Create new complaint
    new_complaint_id = 1 if len(complaints_df) == 0 else complaints_df["id"].max() + 1
    
    new_complaint = pd.DataFrame({
        "id": [new_complaint_id],
        "user_id": [user_id],
        "order_id": [order_id],
        "subject": [subject],
        "description": [description],
        "status": ["Pending"],
        "admin_response": [None],
        "created_at": [pd.Timestamp.now()],
        "updated_at": [pd.Timestamp.now()]
    })
    
    # Add complaint to database
    st.session_state.db["complaints"] = pd.concat([complaints_df, new_complaint], ignore_index=True)
    
    return True, new_complaint_id

def add_rating(user_id, product_id, rating, review):
    """Add a new product rating to the database."""
    ratings_df = st.session_state.db["ratings"]
    products_df = st.session_state.db["products"]
    
    # Check if product exists
    if products_df[products_df["id"] == product_id].empty:
        return False, "Product not found"
    
    # Check if user has already rated this product
    existing_rating = ratings_df[(ratings_df["user_id"] == user_id) & (ratings_df["product_id"] == product_id)]
    
    if not existing_rating.empty:
        # Update existing rating
        ratings_df.loc[(ratings_df["user_id"] == user_id) & (ratings_df["product_id"] == product_id), 
                       ["rating", "review", "created_at"]] = [rating, review, pd.Timestamp.now()]
        
        st.session_state.db["ratings"] = ratings_df
        return True, "Rating updated"
    
    # Create new rating
    new_rating_id = 1 if len(ratings_df) == 0 else ratings_df["id"].max() + 1
    
    new_rating = pd.DataFrame({
        "id": [new_rating_id],
        "user_id": [user_id],
        "product_id": [product_id],
        "rating": [rating],
        "review": [review],
        "created_at": [pd.Timestamp.now()]
    })
    
    # Add rating to database
    st.session_state.db["ratings"] = pd.concat([ratings_df, new_rating], ignore_index=True)
    
    return True, new_rating_id

def respond_to_complaint(complaint_id, response):
    """Update a complaint with admin response."""
    complaints_df = st.session_state.db["complaints"]
    
    # Check if complaint exists
    if complaints_df[complaints_df["id"] == complaint_id].empty:
        return False, "Complaint not found"
    
    # Update complaint
    complaints_df.loc[complaints_df["id"] == complaint_id, 
                     ["status", "admin_response", "updated_at"]] = ["Resolved", response, pd.Timestamp.now()]
    
    st.session_state.db["complaints"] = complaints_df
    
    return True, "Complaint updated"

def search_products(query, category=None, min_price=None, max_price=None):
    """Search for products based on query and filters."""
    products_df = st.session_state.db["products"]
    
    # Start with all products
    results = products_df.copy()
    
    # Apply search query if provided
    if query:
        query_lower = query.lower()
        results = results[
            results["name"].str.lower().str.contains(query_lower) | 
            results["description"].str.lower().str.contains(query_lower)
        ]
    
    # Apply category filter if provided
    if category and category != "All Categories":
        results = results[results["category"] == category]
    
    # Apply price filters if provided
    if min_price is not None:
        results = results[results["price"] >= min_price]
    
    if max_price is not None:
        results = results[results["price"] <= max_price]
    
    return results
