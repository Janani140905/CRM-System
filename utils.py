import streamlit as st

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    
    if "username" not in st.session_state:
        st.session_state.username = None
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

def format_price(price):
    """Format a price value as a string with $ symbol."""
    return f"${price:.2f}"

def format_date(date):
    """Format a datetime as a readable date string."""
    return date.strftime("%Y-%m-%d")

def format_datetime(datetime):
    """Format a datetime as a readable datetime string."""
    return datetime.strftime("%Y-%m-%d %H:%M:%S")
