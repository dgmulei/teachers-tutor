"""
Authentication UI components for the AI Teaching Assistant Platform.
Provides UI elements for user authentication.
"""

import streamlit as st
from typing import Dict, Any, Tuple, Optional

from services.auth_service import auth_service


def login_ui() -> Optional[Dict[str, Any]]:
    """
    Display the login UI.

    Returns:
        User data if login is successful, None otherwise
    """
    st.title("Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password.")
                return None
            
            success, result = auth_service.sign_in(email, password)
            
            if success:
                st.success("Login successful!")
                
                # Extract user ID from the user object
                user_id = None
                user_email = None
                
                if "user" in result and result["user"] is not None:
                    # Try to access the ID attribute directly
                    try:
                        user_id = result["user"].id
                        user_email = result["user"].email
                    except AttributeError:
                        # If that fails, try to access as a dictionary
                        if hasattr(result["user"], "model_dump"):
                            user_dict = result["user"].model_dump()
                            user_id = user_dict.get("id")
                            user_email = user_dict.get("email")
                
                # Create a simple dictionary structure that we can easily access
                user_data = {
                    "user": {
                        "id": user_id,
                        "email": user_email
                    },
                    "session": result.get("session")
                }
                
                return user_data
            else:
                error_msg = "Unknown error"
                if isinstance(result, dict) and "error" in result:
                    error_msg = result["error"]
                st.error(f"Login failed: {error_msg}")
                return None
    
    return None


def signup_ui() -> Optional[Dict[str, Any]]:
    """
    Display the signup UI.

    Returns:
        User data if signup is successful, None otherwise
    """
    st.title("Sign Up")
    
    with st.form("signup_form"):
        email = st.text_input("Email", key="signup_email")
        full_name = st.text_input("Full Name", key="signup_full_name")
        password = st.text_input("Password", type="password", key="signup_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not email or not full_name or not password:
                st.error("Please fill in all required fields.")
                return None
            
            if password != password_confirm:
                st.error("Passwords do not match.")
                return None
            
            success, result = auth_service.sign_up(email, password, full_name)
            
            if success:
                st.success("Sign up successful! Please log in.")
                return result
            else:
                st.error(f"Sign up failed: {result.get('error', 'Unknown error')}")
                return None
    
    return None


def auth_page() -> Optional[Dict[str, Any]]:
    """
    Display the authentication page with login and signup tabs.

    Returns:
        User data if authentication is successful, None otherwise
    """
    # Check if user is already logged in
    if "user" in st.session_state:
        return st.session_state["user"]
    
    # Display login/signup tabs
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        user_data = login_ui()
        if user_data:
            st.session_state["user"] = user_data
            return user_data
    
    with tab2:
        user_data = signup_ui()
        if user_data:
            # Don't automatically log in after signup
            # Just show a success message (handled in signup_ui)
            pass
    
    return None


def logout_ui() -> None:
    """
    Display the logout button and handle logout.
    """
    if st.sidebar.button("Logout"):
        # Get the access token if available
        access_token = st.session_state.get("user", {}).get("session", {}).get("access_token", "")
        
        # Call the sign_out method
        auth_service.sign_out(access_token)
        
        # Clear the session state
        if "user" in st.session_state:
            del st.session_state["user"]
        
        # Rerun the app to show the login page
        st.rerun()


def profile_ui() -> None:
    """
    Display the user profile UI.
    """
    if "user" not in st.session_state:
        return
    
    user_data = st.session_state["user"]
    user = user_data.get("user", {})
    
    st.sidebar.write(f"Logged in as: {user.get('email', 'Unknown')}")
    
    # Add logout button
    logout_ui()


def require_auth() -> Optional[Dict[str, Any]]:
    """
    Require authentication to access the page.
    If the user is not logged in, display the auth page.

    Returns:
        User data if authenticated, None otherwise
    """
    # Check if user is already logged in
    if "user" in st.session_state:
        # Display profile in sidebar
        profile_ui()
        return st.session_state["user"]
    
    # If not logged in, show auth page
    return auth_page()
