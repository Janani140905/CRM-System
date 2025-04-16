import streamlit as st
import pandas as pd
import time
import io
import base64
from db_utils import (
    get_product_by_id, get_user_by_id, get_order_by_id, get_complaint_by_id, 
    respond_to_complaint, get_all_users, get_all_products, get_all_orders, 
    get_all_complaints, get_all_ratings, get_user_orders, get_user_complaints,
    update_product
)

def show_admin_dashboard():
    """Display the admin dashboard with summary information."""
    st.title("Admin Dashboard")
    
    # Get database information
    users_df = get_all_users()
    products_df = get_all_products()
    orders_df = get_all_orders()
    complaints_df = get_all_complaints()
    ratings_df = get_all_ratings()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Total users (excluding admin)
        total_users = len(users_df[~users_df["is_admin"]])
        st.metric("Total Customers", total_users)
    
    with col2:
        # Total products
        st.metric("Total Products", len(products_df))
    
    with col3:
        # Total orders
        st.metric("Total Orders", len(orders_df))
    
    with col4:
        # Open complaints
        open_complaints = len(complaints_df[complaints_df["status"] == "Pending"])
        st.metric("Open Complaints", open_complaints)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Recent orders
    if not orders_df.empty:
        st.write("**Recent Orders:**")
        
        recent_orders = orders_df.sort_values(by="created_at", ascending=False).head(5)
        
        for _, order in recent_orders.iterrows():
            user = get_user_by_id(order["user_id"])
            product = get_product_by_id(order["product_id"])
            
            if user is not None and product is not None:
                st.write(f"Order #{order['id']} - {user['username']} purchased {order['quantity']} × {product['name']} for ${order['total_price']:.2f} ({order['created_at'].strftime('%Y-%m-%d')})")
        
        st.divider()
    
    # Recent complaints
    if not complaints_df.empty:
        st.write("**Recent Complaints:**")
        
        recent_complaints = complaints_df.sort_values(by="created_at", ascending=False).head(5)
        
        for _, complaint in recent_complaints.iterrows():
            user = get_user_by_id(complaint["user_id"])
            
            if user is not None:
                st.write(f"Complaint #{complaint['id']} - {user['username']} - {complaint['subject']} - Status: {complaint['status']} ({complaint['created_at'].strftime('%Y-%m-%d')})")
        
        st.divider()
    
    # Low stock alerts
    st.subheader("Low Stock Alerts")
    
    low_stock_products = products_df[products_df["stock"] < 10].sort_values(by="stock")
    
    if not low_stock_products.empty:
        for _, product in low_stock_products.iterrows():
            st.write(f"**{product['name']}** - Only {product['stock']} left in stock")
    else:
        st.info("No products with low stock.")
    
    # Export data section
    st.subheader("Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export Users"):
            csv = users_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="users.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    with col2:
        if st.button("Export Products"):
            csv = products_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="products.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    with col3:
        if st.button("Export Orders"):
            csv = orders_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="orders.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)

def show_user_management():
    """Display the user management page."""
    st.title("User Management")
    
    # Get user data
    users_df = get_all_users()
    
    # Filter out admin users for display
    regular_users = users_df[~users_df["is_admin"]]
    
    # Search/filter options
    search_query = st.text_input("Search by Username or Email")
    
    if search_query:
        query_lower = search_query.lower()
        filtered_users = regular_users[
            regular_users["username"].str.lower().str.contains(query_lower) | 
            regular_users["email"].str.lower().str.contains(query_lower)
        ]
    else:
        filtered_users = regular_users
    
    # Display user list
    st.subheader(f"Users ({len(filtered_users)})")
    
    if filtered_users.empty:
        st.info("No users found.")
    else:
        # Sort users by creation date
        filtered_users = filtered_users.sort_values(by="created_at", ascending=False)
        
        # Display users in a table
        st.dataframe(
            filtered_users[["id", "username", "email", "created_at"]],
            column_config={
                "id": "ID",
                "username": "Username",
                "email": "Email",
                "created_at": st.column_config.DatetimeColumn("Created At", format="YYYY-MM-DD HH:mm")
            },
            hide_index=True
        )
    
    # User details section
    st.subheader("User Details")
    
    selected_user_id = st.selectbox(
        "Select User",
        options=regular_users["id"].tolist(),
        format_func=lambda x: f"{get_user_by_id(x)['username']} (ID: {x})"
    )
    
    if selected_user_id:
        user = get_user_by_id(selected_user_id)
        
        if user is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Username:** {user['username']}")
                st.write(f"**Email:** {user['email']}")
                st.write(f"**Created:** {user['created_at'].strftime('%Y-%m-%d %H:%M')}")
            
            # Get user orders
            user_orders = get_user_orders(selected_user_id)
            
            with col2:
                st.write(f"**Total Orders:** {len(user_orders)}")
                
                if not user_orders.empty:
                    total_spent = user_orders["total_price"].sum()
                    st.write(f"**Total Spent:** ${total_spent:.2f}")
                else:
                    st.write("**Total Spent:** $0.00")
                
                # Get user complaints
                user_complaints = get_user_complaints(selected_user_id)
                st.write(f"**Complaints:** {len(user_complaints)}")
            
            # User activity tabs
            tab1, tab2 = st.tabs(["Orders", "Complaints"])
            
            with tab1:
                if user_orders.empty:
                    st.info("This user has no orders.")
                else:
                    # Sort orders by date
                    user_orders = user_orders.sort_values(by="created_at", ascending=False)
                    
                    for _, order in user_orders.iterrows():
                        product = get_product_by_id(order["product_id"])
                        
                        if product is not None:
                            st.write(f"**Order #{order['id']}** - {order['created_at'].strftime('%Y-%m-%d')}")
                            st.write(f"Product: {product['name']} × {order['quantity']}")
                            st.write(f"Total: ${order['total_price']:.2f} | Status: {order['status']}")
                            st.divider()
            
            with tab2:
                if user_complaints.empty:
                    st.info("This user has no complaints.")
                else:
                    # Sort complaints by date
                    user_complaints = user_complaints.sort_values(by="created_at", ascending=False)
                    
                    for _, complaint in user_complaints.iterrows():
                        st.write(f"**Complaint #{complaint['id']}** - {complaint['created_at'].strftime('%Y-%m-%d')}")
                        st.write(f"Subject: {complaint['subject']}")
                        st.write(f"Status: {complaint['status']}")
                        
                        with st.expander("View Details"):
                            st.write(f"Description: {complaint['description']}")
                            
                            if complaint["admin_response"]:
                                st.write(f"Admin Response: {complaint['admin_response']}")
                            else:
                                st.write("No response yet.")
                                response = st.text_area(f"Respond to Complaint #{complaint['id']}", key=f"response_{complaint['id']}")
                                
                                if st.button(f"Submit Response", key=f"submit_{complaint['id']}"):
                                    if response:
                                        success, message = respond_to_complaint(complaint["id"], response)
                                        
                                        if success:
                                            st.success("Response submitted successfully!")
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error(message)
                                    else:
                                        st.error("Please enter a response.")
                        
                        st.divider()

def show_complaint_management():
    """Display the complaint management page."""
    st.title("Complaint Management")
    
    # Get complaints data
    complaints_df = get_all_complaints()
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "Pending", "Resolved"]
        )
    
    with col2:
        search_query = st.text_input("Search by Subject")
    
    # Apply filters
    filtered_complaints = complaints_df.copy()
    
    if status_filter != "All":
        filtered_complaints = filtered_complaints[filtered_complaints["status"] == status_filter]
    
    if search_query:
        query_lower = search_query.lower()
        filtered_complaints = filtered_complaints[
            filtered_complaints["subject"].str.lower().str.contains(query_lower)
        ]
    
    # Display complaints
    st.subheader(f"Complaints ({len(filtered_complaints)})")
    
    if filtered_complaints.empty:
        st.info("No complaints found.")
    else:
        # Sort complaints by date (most recent first)
        filtered_complaints = filtered_complaints.sort_values(by="created_at", ascending=False)
        
        # Create tabs for pending and resolved
        pending_complaints = filtered_complaints[filtered_complaints["status"] == "Pending"]
        resolved_complaints = filtered_complaints[filtered_complaints["status"] == "Resolved"]
        
        tab1, tab2 = st.tabs([f"Pending ({len(pending_complaints)})", f"Resolved ({len(resolved_complaints)})"])
        
        with tab1:
            if pending_complaints.empty:
                st.info("No pending complaints.")
            else:
                for _, complaint in pending_complaints.iterrows():
                    user = get_user_by_id(complaint["user_id"])
                    order = get_order_by_id(complaint["order_id"])
                    
                    if user is not None and order is not None:
                        product = get_product_by_id(order["product_id"])
                        
                        if product is not None:
                            st.write(f"**Complaint #{complaint['id']}** - {complaint['created_at'].strftime('%Y-%m-%d')}")
                            st.write(f"User: {user['username']} | Order: #{order['id']} | Product: {product['name']}")
                            st.write(f"Subject: {complaint['subject']}")
                            
                            with st.expander("View Details & Respond"):
                                st.write(f"**Description:**")
                                st.write(complaint['description'])
                                
                                st.divider()
                                
                                response = st.text_area(f"Response to Complaint #{complaint['id']}", key=f"response_{complaint['id']}")
                                
                                if st.button(f"Submit Response", key=f"submit_{complaint['id']}"):
                                    if response:
                                        success, message = respond_to_complaint(complaint["id"], response)
                                        
                                        if success:
                                            st.success("Response submitted successfully!")
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error(message)
                                    else:
                                        st.error("Please enter a response.")
                            
                            st.divider()
        
        with tab2:
            if resolved_complaints.empty:
                st.info("No resolved complaints.")
            else:
                for _, complaint in resolved_complaints.iterrows():
                    user = get_user_by_id(complaint["user_id"])
                    order = get_order_by_id(complaint["order_id"])
                    
                    if user is not None and order is not None:
                        product = get_product_by_id(order["product_id"])
                        
                        if product is not None:
                            st.write(f"**Complaint #{complaint['id']}** - {complaint['created_at'].strftime('%Y-%m-%d')}")
                            st.write(f"User: {user['username']} | Order: #{order['id']} | Product: {product['name']}")
                            st.write(f"Subject: {complaint['subject']}")
                            
                            with st.expander("View Details"):
                                st.write(f"**Description:**")
                                st.write(complaint['description'])
                                
                                st.divider()
                                
                                st.write(f"**Admin Response:**")
                                st.write(complaint['admin_response'])
                                st.write(f"Responded on: {complaint['updated_at'].strftime('%Y-%m-%d %H:%M')}")
                            
                            st.divider()

def show_product_management():
    """Display the product management page."""
    st.title("Product Management")
    
    # Get products data
    products_df = get_all_products()
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            options=["All Categories"] + list(products_df["category"].unique())
        )
    
    with col2:
        search_query = st.text_input("Search by Product Name")
    
    # Apply filters
    filtered_products = products_df.copy()
    
    if category_filter != "All Categories":
        filtered_products = filtered_products[filtered_products["category"] == category_filter]
    
    if search_query:
        query_lower = search_query.lower()
        filtered_products = filtered_products[
            filtered_products["name"].str.lower().str.contains(query_lower)
        ]
    
    # Display products
    st.subheader(f"Products ({len(filtered_products)})")
    
    if filtered_products.empty:
        st.info("No products found.")
    else:
        # Sort products by name
        filtered_products = filtered_products.sort_values(by="name")
        
        # Display products in a table
        st.dataframe(
            filtered_products[["id", "name", "category", "price", "stock"]],
            column_config={
                "id": "ID",
                "name": "Product Name",
                "category": "Category",
                "price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "stock": "Stock"
            },
            hide_index=True
        )
    
    # Product details section
    st.subheader("Product Details")
    
    selected_product_id = st.selectbox(
        "Select Product",
        options=products_df["id"].tolist(),
        format_func=lambda x: f"{get_product_by_id(x)['name']} (ID: {x})"
    )
    
    if selected_product_id:
        product = get_product_by_id(selected_product_id)
        
        if product is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {product['name']}")
                st.write(f"**Category:** {product['category']}")
                st.write(f"**Price:** ${product['price']:.2f}")
                st.write(f"**Stock:** {product['stock']}")
            
            with col2:
                st.write(f"**Description:**")
                st.write(product['description'])
            
            # Product sales and ratings
            orders_df = get_all_orders()
            product_orders = orders_df[orders_df["product_id"] == selected_product_id]
            
            ratings_df = get_all_ratings()
            product_ratings = ratings_df[ratings_df["product_id"] == selected_product_id]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Sales Statistics")
                
                if product_orders.empty:
                    st.info("No sales for this product.")
                else:
                    total_sales = product_orders["quantity"].sum()
                    total_revenue = product_orders["total_price"].sum()
                    
                    st.metric("Total Units Sold", total_sales)
                    st.metric("Total Revenue", f"${total_revenue:.2f}")
            
            with col2:
                st.subheader("Ratings")
                
                if product_ratings.empty:
                    st.info("No ratings for this product.")
                else:
                    avg_rating = product_ratings["rating"].mean()
                    num_ratings = len(product_ratings)
                    
                    st.metric("Average Rating", f"{avg_rating:.1f}/5.0")
                    st.metric("Number of Ratings", num_ratings)
            
            # Display ratings
            if not product_ratings.empty:
                st.subheader("Customer Reviews")
                
                # Sort ratings by date
                product_ratings = product_ratings.sort_values(by="created_at", ascending=False)
                
                for _, rating in product_ratings.iterrows():
                    user = get_user_by_id(rating["user_id"])
                    
                    if user is not None:
                        st.write(f"**{user['username']}** - {'⭐' * int(rating['rating'])} ({rating['created_at'].strftime('%Y-%m-%d')})")
                        st.write(rating['review'])
                        st.divider()
            
            # Product edit form
            st.subheader("Edit Product")
            
            with st.form("edit_product_form"):
                name = st.text_input("Name", value=product["name"])
                category = st.text_input("Category", value=product["category"])
                price = st.number_input("Price", value=float(product["price"]), min_value=0.01, step=0.01)
                stock = st.number_input("Stock", value=int(product["stock"]), min_value=0, step=1)
                description = st.text_area("Description", value=product["description"])
                
                submitted = st.form_submit_button("Update Product")
                
                if submitted:
                    # Update product in database
                    success, message = update_product(
                        product_id=selected_product_id,
                        name=name,
                        category=category,
                        price=price,
                        stock=stock,
                        description=description
                    )
                    
                    if success:
                        st.success("Product updated successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error updating product: {message}")
