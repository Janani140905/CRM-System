import streamlit as st
import pandas as pd
import hashlib
import time
from db_utils import authenticate_user, create_user

def hash_password(password):
    """Hash a password for storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def login():
    """User login form and authentication logic."""
    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:
                # Authenticate user
                success, user = authenticate_user(username, password)
                
                if success:
                    st.session_state.is_authenticated = True
                    st.session_state.username = user["username"]
                    st.session_state.user_id = user["id"]
                    st.session_state.is_admin = user["is_admin"]
                    
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password!")
            else:
                st.error("Please enter both username and password!")

def register():
    """User registration form and account creation logic."""
    with st.form("register_form"):
        st.subheader("Register")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            if username and email and password and confirm_password:
                if password == confirm_password:
                    # Create a new user
                    success, message = create_user(username, email, password)
                    
                    if success:
                        st.success("Registration successful! Please login.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Passwords do not match!")
            else:
                st.error("Please fill out all fields!")

def logout():
    """Log out the current user."""
    for key in ["is_authenticated", "username", "user_id", "is_admin"]:
        if key in st.session_state:
            st.session_state[key] = False if key == "is_authenticated" or key == "is_admin" else None

def check_authentication():
    """Check if a user is authenticated."""
    return st.session_state.is_authenticated
