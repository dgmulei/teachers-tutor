"""
Authentication service for the AI Teaching Assistant Platform.
Handles user authentication using Supabase.
"""

import logging
from typing import Dict, Any, Tuple
from datetime import datetime
from supabase import create_client, Client

from config.settings import SUPABASE_URL, SUPABASE_KEY


class AuthService:
    """Service class for handling authentication with Supabase."""

    def __init__(self):
        """Initialize the Supabase client."""
        try:
            print(f"\n[DEBUG] Connecting to Supabase URL: {SUPABASE_URL}\n")
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            logging.error(f"Failed to initialize Supabase client: {e}")
            raise

    def sign_up(self, email: str, password: str, full_name: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Sign up a new user.

        Args:
            email: User's email address
            password: User's password
            full_name: User's full name

        Returns:
            Tuple of (success: bool, result: dict)
        """
        try:
            # Create user in Supabase Auth
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name
                    }
                }
            })

            # Check if user was created successfully
            if response.user:
                # Ensure user exists in the users table
                if self.ensure_user_exists(response.user):
                    return True, {
                        "user": response.user,
                        "session": response.session
                    }
                return False, {"error": "Failed to create user record in database"}
            else:
                return False, {"error": "Failed to create user"}

        except Exception as e:
            logging.error(f"Sign up failed: {e}")
            return False, {"error": str(e)}

    def sign_in(self, email: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Sign in an existing user.

        Args:
            email: User's email address
            password: User's password

        Returns:
            Tuple of (success: bool, result: dict)
        """
        try:
            # Sign in user with Supabase Auth
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            # Check if sign in was successful
            if response.user:
                # Ensure user exists in the users table
                if self.ensure_user_exists(response.user):
                    return True, {
                        "user": response.user,
                        "session": response.session
                    }
                return False, {"error": "Failed to create user record in database"}
            else:
                return False, {"error": "Invalid credentials"}

        except Exception as e:
            logging.error(f"Sign in failed: {e}")
            return False, {"error": str(e)}

    def sign_out(self, access_token: str = "") -> bool:
        """
        Sign out the current user.

        Args:
            access_token: Optional access token to invalidate

        Returns:
            bool: True if sign out was successful, False otherwise
        """
        try:
            # Sign out user from Supabase Auth
            self.client.auth.sign_out()
            return True

        except Exception as e:
            logging.error(f"Sign out failed: {e}")
            return False

    def ensure_user_exists(self, user_data) -> bool:
        """
        Ensure the authenticated user exists in the users table.
        
        Args:
            user_data: User data from authentication (Supabase User object)
            
        Returns:
            bool: True if user exists or was created, False otherwise
        """
        try:
            user_id = user_data.id
            
            # Check if user exists in users table
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if not response.data:
                # User doesn't exist, create a new record
                insert_data = {
                    "id": user_id,
                    "email": user_data.email,
                    "full_name": user_data.user_metadata.get("full_name", "") if user_data.user_metadata else "",
                    "created_at": datetime.utcnow().isoformat()
                }
                
                self.client.table("users").insert(insert_data).execute()
                logging.info(f"Created new user record for {user_data.email}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to ensure user exists: {e}")
            return False

    def get_user(self) -> Dict[str, Any]:
        """
        Get the current user's information.

        Returns:
            Dict containing user information or None if no user is signed in
        """
        try:
            # Get current session
            session = self.client.auth.get_session()
            
            if session and session.user:
                return {
                    "id": session.user.id,
                    "email": session.user.email,
                    "full_name": session.user.user_metadata.get("full_name")
                }
            else:
                return {}

        except Exception as e:
            logging.error(f"Failed to get user: {e}")
            return {}


# Create a singleton instance
auth_service = AuthService()
