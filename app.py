import streamlit as st
import pandas as pd
import time

from authentication import login, register, logout, check_authentication
from db_utils import initialize_database
from user_views import show_dashboard, show_product_search, show_order_history, show_complaint_form, show_ratings
from admin_views import show_admin_dashboard, show_user_management, show_complaint_management, show_product_management
from utils import initialize_session_state

def main():
    # Initialize the session state
    initialize_session_state()
    
    # Initialize the database if not already done
    initialize_database()
    
    # Set page config
    st.set_page_config(
        page_title="CRM System",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Display the sidebar for navigation
    with st.sidebar:
        st.title("CRM System")
        
        if not st.session_state.is_authenticated:
            auth_option = st.radio("", ["Login", "Register"])
            
            if auth_option == "Login":
                login()
            else:
                register()
        else:
            st.success(f"Logged in as: {st.session_state.username}")
            
            if st.session_state.is_admin:
                # Admin navigation
                st.subheader("Admin Navigation")
                admin_choice = st.radio(
                    "Select Option",
                    ["Dashboard", "User Management", "Complaint Management", "Product Management"]
                )
                
                if st.button("Logout"):
                    logout()
                    st.rerun()
            else:
                # User navigation
                st.subheader("Navigation")
                user_choice = st.radio(
                    "Select Option",
                    ["Dashboard", "Product Search", "Order History", "Submit Complaint/Feedback", "Rate Products"]
                )
                
                if st.button("Logout"):
                    logout()
                    st.rerun()
    
    # Main content based on authentication status and selection
    if not st.session_state.is_authenticated:
        st.title("Welcome to the CRM System")
        st.write("Please login or register to access the system.")
    else:
        if st.session_state.is_admin:
            # Admin views
            if admin_choice == "Dashboard":
                show_admin_dashboard()
            elif admin_choice == "User Management":
                show_user_management()
            elif admin_choice == "Complaint Management":
                show_complaint_management()
            elif admin_choice == "Product Management":
                show_product_management()
        else:
            # User views
            if user_choice == "Dashboard":
                show_dashboard()
            elif user_choice == "Product Search":
                show_product_search()
            elif user_choice == "Order History":
                show_order_history()
            elif user_choice == "Submit Complaint/Feedback":
                show_complaint_form()
            elif user_choice == "Rate Products":
                show_ratings()

if __name__ == "__main__":
    main()
