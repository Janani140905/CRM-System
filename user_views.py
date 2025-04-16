import streamlit as st
import pandas as pd
import time
from db_utils import (
    get_product_by_id, get_user_orders, get_user_complaints, get_user_ratings,
    search_products, add_order, add_complaint, add_rating, generate_sample_orders
)

def show_dashboard():
    """Display the user dashboard with summary information."""
    st.title(f"Welcome, {st.session_state.username}!")
    
    # Generate sample orders if needed (for demo purposes)
    generate_sample_orders()
    
    col1, col2 = st.columns(2)
    
    # Get user data
    user_id = st.session_state.user_id
    orders = get_user_orders(user_id)
    complaints = get_user_complaints(user_id)
    ratings = get_user_ratings(user_id)
    
    with col1:
        st.subheader("Your Activity")
        
        # Order statistics
        st.metric("Total Orders", len(orders))
        
        # Calculate total spent
        if not orders.empty:
            total_spent = orders["total_price"].sum()
            st.metric("Total Spent", f"${total_spent:.2f}")
        else:
            st.metric("Total Spent", "$0.00")
        
        # Complaint statistics
        st.metric("Open Complaints", len(complaints[complaints["status"] == "Pending"]))
        
        # Rating statistics
        st.metric("Products Rated", len(ratings))
    
    with col2:
        st.subheader("Recent Orders")
        
        if not orders.empty:
            recent_orders = orders.head(3)
            
            for _, order in recent_orders.iterrows():
                product = get_product_by_id(order["product_id"])
                
                if product is not None:
                    st.write(f"**{product['name']}** - ${order['total_price']:.2f}")
                    st.write(f"Status: {order['status']} | Date: {order['created_at'].strftime('%Y-%m-%d')}")
                    st.divider()
        else:
            st.info("You haven't placed any orders yet.")
    
    # Featured products section
    st.subheader("Featured Products")
    
    products_df = get_all_products()
    featured_products = products_df.sample(min(3, len(products_df)))
    
    cols = st.columns(3)
    
    for i, (_, product) in enumerate(featured_products.iterrows()):
        with cols[i]:
            st.write(f"**{product['name']}**")
            st.write(f"${product['price']:.2f}")
            st.write(f"{product['description'][:100]}...")
            
            if st.button(f"View Details #{product['id']}", key=f"view_{product['id']}"):
                st.session_state.selected_product = product["id"]
                st.session_state.last_page = "dashboard"
                st.rerun()

def show_product_search():
    """Display the product search page with filters and results."""
    st.title("Product Search")
    
    # Search and filter section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("Search Products", value="")
    
    with col2:
        # Get all unique categories
        products_df = get_all_products()
        categories = products_df["category"].unique().tolist()
        categories = ["All Categories"] + categories
        selected_category = st.selectbox("Category", categories)
    
    with col3:
        # Price range slider
        min_price = float(products_df["price"].min())
        max_price = float(products_df["price"].max())
        
        price_range = st.slider(
            "Price Range",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=10.0
        )
    
    # Search button
    if st.button("Search"):
        selected_category_filter = None if selected_category == "All Categories" else selected_category
        search_results = search_products(
            search_query, 
            category=selected_category_filter,
            min_price=price_range[0],
            max_price=price_range[1]
        )
        
        st.session_state.search_results = search_results
    
    # Display search results
    if "search_results" in st.session_state:
        results = st.session_state.search_results
        
        if results.empty:
            st.info("No products found matching your criteria.")
        else:
            st.subheader(f"Found {len(results)} products")
            
            # Display results in a grid
            num_cols = 3
            rows = (len(results) + num_cols - 1) // num_cols  # Ceiling division
            
            for row in range(rows):
                cols = st.columns(num_cols)
                
                for col in range(num_cols):
                    idx = row * num_cols + col
                    
                    if idx < len(results):
                        product = results.iloc[idx]
                        
                        with cols[col]:
                            st.write(f"**{product['name']}**")
                            st.write(f"Category: {product['category']}")
                            st.write(f"Price: ${product['price']:.2f}")
                            st.write(f"In Stock: {product['stock']}")
                            
                            # Product actions
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button(f"View", key=f"view_{product['id']}"):
                                    st.session_state.selected_product = product["id"]
                                    st.session_state.last_page = "search"
                                    
                            with col2:
                                if st.button(f"Buy", key=f"buy_{product['id']}"):
                                    show_purchase_form(product["id"])
    
    # Display selected product details
    if "selected_product" in st.session_state:
        product_id = st.session_state.selected_product
        product = get_product_by_id(product_id)
        
        if product is not None:
            st.divider()
            st.subheader(f"Product Details: {product['name']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Category:** {product['category']}")
                st.write(f"**Price:** ${product['price']:.2f}")
                st.write(f"**In Stock:** {product['stock']}")
            
            with col2:
                st.write(f"**Description:**")
                st.write(product['description'])
            
            # Purchase form
            st.subheader("Purchase")
            quantity = st.number_input("Quantity", min_value=1, max_value=int(product['stock']), value=1)
            
            if st.button("Add to Order"):
                success, message = add_order(st.session_state.user_id, product_id, quantity)
                
                if success:
                    st.success(f"Order placed successfully! Order #{message}")
                    time.sleep(1)
                    st.session_state.pop("selected_product", None)
                    st.rerun()
                else:
                    st.error(message)
            
            # Go back button
            if st.button("Back to Results"):
                st.session_state.pop("selected_product", None)
                st.rerun()

def show_purchase_form(product_id):
    """Show the purchase form for a product."""
    product = get_product_by_id(product_id)
    
    if product is not None:
        st.session_state.selected_product = product_id
        st.rerun()

def show_order_history():
    """Display the user's order history."""
    st.title("Order History")
    
    # Get user orders
    user_id = st.session_state.user_id
    orders = get_user_orders(user_id)
    
    if orders.empty:
        st.info("You haven't placed any orders yet.")
    else:
        # Sort orders by date (most recent first)
        orders = orders.sort_values(by="created_at", ascending=False)
        
        # Display orders
        for _, order in orders.iterrows():
            product = get_product_by_id(order["product_id"])
            
            if product is not None:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{product['name']}**")
                    st.write(f"{order['quantity']} × ${product['price']:.2f}")
                
                with col2:
                    st.write(f"**Total:** ${order['total_price']:.2f}")
                    st.write(f"**Status:** {order['status']}")
                
                with col3:
                    st.write(f"**Date:** {order['created_at'].strftime('%Y-%m-%d')}")
                    
                    # Add complaint button
                    if st.button(f"Submit Complaint", key=f"complaint_{order['id']}"):
                        st.session_state.selected_order_for_complaint = order["id"]
                        st.rerun()
                
                st.divider()
        
        # Display complaint form if an order is selected
        if "selected_order_for_complaint" in st.session_state:
            order_id = st.session_state.selected_order_for_complaint
            order = orders[orders["id"] == order_id].iloc[0]
            product = get_product_by_id(order["product_id"])
            
            st.subheader(f"Submit Complaint for Order #{order_id}")
            st.write(f"Product: {product['name']}")
            st.write(f"Date: {order['created_at'].strftime('%Y-%m-%d')}")
            
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Submit"):
                    if subject and description:
                        success, message = add_complaint(user_id, order_id, subject, description)
                        
                        if success:
                            st.success(f"Complaint submitted successfully! Complaint #{message}")
                            time.sleep(1)
                            st.session_state.pop("selected_order_for_complaint", None)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill out all fields.")
            
            with col2:
                if st.button("Cancel"):
                    st.session_state.pop("selected_order_for_complaint", None)
                    st.rerun()

def show_complaint_form():
    """Display the complaint submission form and history."""
    st.title("Complaints & Feedback")
    
    # Tabs for submission and history
    tab1, tab2 = st.tabs(["Submit New Complaint", "Complaint History"])
    
    with tab1:
        st.subheader("Submit a New Complaint")
        
        # Get user orders for selection
        user_id = st.session_state.user_id
        orders = get_user_orders(user_id)
        
        if orders.empty:
            st.info("You haven't placed any orders yet. Orders are required to submit a complaint.")
        else:
            # Create order options
            order_options = []
            
            for _, order in orders.iterrows():
                product = get_product_by_id(order["product_id"])
                
                if product is not None:
                    option_text = f"Order #{order['id']} - {product['name']} - ${order['total_price']:.2f} ({order['created_at'].strftime('%Y-%m-%d')})"
                    order_options.append((option_text, order["id"]))
            
            # Display order selection
            selected_option = st.selectbox(
                "Select Order",
                options=range(len(order_options)),
                format_func=lambda i: order_options[i][0]
            )
            
            selected_order_id = order_options[selected_option][1]
            
            # Complaint form
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            
            if st.button("Submit Complaint"):
                if subject and description:
                    success, message = add_complaint(user_id, selected_order_id, subject, description)
                    
                    if success:
                        st.success(f"Complaint submitted successfully! Complaint #{message}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill out all fields.")
    
    with tab2:
        st.subheader("Your Complaint History")
        
        # Get user complaints
        complaints = get_user_complaints(user_id)
        
        if complaints.empty:
            st.info("You haven't submitted any complaints yet.")
        else:
            # Sort complaints by date (most recent first)
            complaints = complaints.sort_values(by="created_at", ascending=False)
            
            # Display complaints
            for _, complaint in complaints.iterrows():
                order = get_user_orders(user_id)
                order = order[order["id"] == complaint["order_id"]]
                
                if not order.empty:
                    order = order.iloc[0]
                    product = get_product_by_id(order["product_id"])
                    
                    if product is not None:
                        st.write(f"**Subject:** {complaint['subject']}")
                        st.write(f"**Order:** #{complaint['order_id']} - {product['name']}")
                        st.write(f"**Status:** {complaint['status']}")
                        st.write(f"**Date:** {complaint['created_at'].strftime('%Y-%m-%d')}")
                        st.write(f"**Description:** {complaint['description']}")
                        
                        if complaint["admin_response"]:
                            st.write(f"**Admin Response:** {complaint['admin_response']}")
                        
                        st.divider()

def show_ratings():
    """Display the product rating page."""
    st.title("Rate Products")
    
    # Get user information
    user_id = st.session_state.user_id
    
    # Get products the user has ordered
    orders = get_user_orders(user_id)
    
    if orders.empty:
        st.info("You haven't ordered any products yet. Please place an order to provide ratings.")
    else:
        # Get unique products from orders
        ordered_product_ids = orders["product_id"].unique()
        
        # Get user's existing ratings
        ratings = get_user_ratings(user_id)
        rated_product_ids = [] if ratings.empty else ratings["product_id"].unique()
        
        # Tabs for rating and history
        tab1, tab2 = st.tabs(["Rate a Product", "Your Ratings"])
        
        with tab1:
            st.subheader("Rate a Product")
            
            # Create product options from orders
            product_options = []
            
            for product_id in ordered_product_ids:
                product = get_product_by_id(product_id)
                
                if product is not None:
                    option_text = f"{product['name']} - ${product['price']:.2f}"
                    rating_status = " (Already Rated)" if product_id in rated_product_ids else ""
                    product_options.append((option_text + rating_status, product_id))
            
            # Display product selection
            selected_option = st.selectbox(
                "Select Product",
                options=range(len(product_options)),
                format_func=lambda i: product_options[i][0]
            )
            
            selected_product_id = product_options[selected_option][1]
            selected_product = get_product_by_id(selected_product_id)
            
            # Get existing rating if available
            existing_rating = None
            existing_review = ""
            
            if not ratings.empty:
                product_rating = ratings[ratings["product_id"] == selected_product_id]
                
                if not product_rating.empty:
                    existing_rating = product_rating.iloc[0]["rating"]
                    existing_review = product_rating.iloc[0]["review"]
            
            # Rating form
            st.write(f"**Product:** {selected_product['name']}")
            
            rating = st.slider(
                "Rating (1-5)",
                min_value=1,
                max_value=5,
                value=int(existing_rating) if existing_rating else 3,
                step=1
            )
            
            review = st.text_area("Review", value=existing_review)
            
            button_text = "Update Rating" if existing_rating else "Submit Rating"
            
            if st.button(button_text):
                if review:
                    success, message = add_rating(user_id, selected_product_id, rating, review)
                    
                    if success:
                        st.success(f"Rating {'updated' if existing_rating else 'submitted'} successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please write a review.")
        
        with tab2:
            st.subheader("Your Ratings")
            
            if ratings.empty:
                st.info("You haven't rated any products yet.")
            else:
                # Sort ratings by date (most recent first)
                ratings = ratings.sort_values(by="created_at", ascending=False)
                
                # Display ratings
                for _, user_rating in ratings.iterrows():
                    product = get_product_by_id(user_rating["product_id"])
                    
                    if product is not None:
                        st.write(f"**{product['name']}**")
                        st.write(f"**Rating:** {'⭐' * int(user_rating['rating'])}")
                        st.write(f"**Date:** {user_rating['created_at'].strftime('%Y-%m-%d')}")
                        st.write(f"**Review:** {user_rating['review']}")
                        st.divider()
