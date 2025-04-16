# CRM System

A Python-powered CRM system built with Streamlit, featuring comprehensive business management tools including user authentication, product management, order tracking, and admin functionalities.

## Features

- User authentication (login/registration)
- Product management (search, add, edit, delete)
- Order tracking
- Customer complaint handling
- Product ratings and reviews
- Admin dashboard with analytics
- SQLite database for persistent data storage

## Setup Instructions

1. Install the required packages:
   ```
   pip install -r package_requirements.txt
   ```

2. Run the application:
   ```
   streamlit run app.py
   ```

3. Access the application in your web browser at:
   ```
   http://localhost:5000
   ```

## Admin Access

- Username: admin
- Password: admin

## Regular User Access

You can register a new user account from the login page.

## File Structure

- `app.py` - Main application entry point
- `authentication.py` - Handles user login and registration
- `db_utils.py` - SQLite database implementation with CRUD operations
- `user_views.py` - User interface components
- `admin_views.py` - Admin interface components
- `utils.py` - Utility functions
- `.streamlit/config.toml` - Streamlit configuration
- `crm_database.db` - SQLite database file