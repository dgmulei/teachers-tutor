"""
AI Teaching Assistant Platform

A Streamlit-based web application that allows teachers to create custom AI assistants
using their own curriculum materials. The application leverages the OpenAI Assistants API
and uses Supabase for authentication and data storage.
"""

import streamlit as st
import os
import logging

from utils.logging_utils import setup_logging, configure_streamlit_logging
from config.settings import APP_NAME, DEBUG
from ui.auth_ui import require_auth
from ui.assistant_ui import assistant_page
from ui.chat_ui import chat_page


# Set up logging
if DEBUG:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

logger = setup_logging(log_level=log_level)
configure_streamlit_logging()

# Configure Streamlit page
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main application entry point."""
    # Display app title in sidebar
    st.sidebar.title(APP_NAME)
    
    # Initialize session state for navigation
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "assistants"
    
    # Require authentication
    user_data = require_auth()
    
    if not user_data:
        # User is not authenticated, auth page is displayed by require_auth
        return
    
    # Get user ID
    if isinstance(user_data, dict) and "user" in user_data and isinstance(user_data["user"], dict):
        user_id = user_data["user"].get("id")
    else:
        st.error("User data format is incorrect. Please log out and log in again.")
        return
    
    if not user_id:
        st.error("User ID not found. Please log out and log in again.")
        return
    
    # Navigation in sidebar
    st.sidebar.title("Navigation")
    
    if st.sidebar.button("Assistants", use_container_width=True, 
                         type="primary" if st.session_state["current_page"] == "assistants" else "secondary"):
        st.session_state["current_page"] = "assistants"
        st.session_state["current_assistant_id"] = None
        st.session_state["current_thread_id"] = None
        st.rerun()
    
    if st.sidebar.button("Tutor Session History", use_container_width=True,
                         type="primary" if st.session_state["current_page"] == "chat_history" else "secondary"):
        st.session_state["current_page"] = "chat_history"
        st.session_state["current_assistant_id"] = None
        st.session_state["current_thread_id"] = None
        st.rerun()
    
    # Display the appropriate page based on current_page
    if st.session_state["current_page"] == "assistants" or st.session_state["current_page"] == "manage_assistant":
        assistant_page(user_id)
    elif st.session_state["current_page"] == "chat":
        chat_page(user_id)
    elif st.session_state["current_page"] == "chat_history":
        chat_page(user_id)  # Chat page handles both chat and chat history
    else:
        st.error(f"Unknown page: {st.session_state['current_page']}")


if __name__ == "__main__":
    main()
