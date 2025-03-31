"""
Database service for the AI Teaching Assistant Platform.
Handles database operations using Supabase.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID

from services.auth_service import auth_service


class DatabaseService:
    """Service class for handling database operations with Supabase."""

    def __init__(self):
        """Initialize the database service using the auth service's Supabase client."""
        self.client = auth_service.client

    # Assistant operations

    def create_assistant(self, user_id: str, name: str, description: str, openai_assistant_id: str) -> Optional[Dict[str, Any]]:
        """
        Create a new assistant in the database.

        Args:
            user_id: ID of the user creating the assistant
            name: Name of the assistant
            description: Description of the assistant
            openai_assistant_id: ID of the assistant in OpenAI

        Returns:
            Created assistant data or None if creation failed
        """
        try:
            response = self.client.table("assistants").insert({
                "user_id": user_id,
                "name": name,
                "description": description,
                "openai_assistant_id": openai_assistant_id,
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            logging.error(f"Failed to create assistant: {e}")
            return None

    def get_assistant(self, assistant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an assistant by ID.

        Args:
            assistant_id: ID of the assistant

        Returns:
            Assistant data or None if not found
        """
        try:
            response = self.client.table("assistants").select("*").eq("id", assistant_id).execute()
            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            logging.error(f"Failed to get assistant: {e}")
            return None

    def get_user_assistants(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all assistants for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of assistant data
        """
        try:
            response = self.client.table("assistants").select("*").eq("user_id", user_id).execute()
            return response.data or []

        except Exception as e:
            logging.error(f"Failed to get user assistants: {e}")
            return []

    def update_assistant(self, assistant_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an assistant.

        Args:
            assistant_id: ID of the assistant to update
            data: Data to update

        Returns:
            Updated assistant data or None if update failed
        """
        try:
            response = self.client.table("assistants").update(data).eq("id", assistant_id).execute()
            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            logging.error(f"Failed to update assistant: {e}")
            return None

    def delete_assistant(self, assistant_id: str) -> bool:
        """
        Delete an assistant.

        Args:
            assistant_id: ID of the assistant to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            response = self.client.table("assistants").delete().eq("id", assistant_id).execute()
            return bool(response.data)

        except Exception as e:
            logging.error(f"Failed to delete assistant: {e}")
            return False

    # Document operations

    def create_document(self, user_id: str, assistant_id: str, filename: str, file_type: str,
                       file_size: int, openai_file_id: str, storage_path: str, file_url: str) -> Optional[Dict[str, Any]]:
        """
        Create a new document in the database.

        Args:
            user_id: ID of the user uploading the document
            assistant_id: ID of the assistant this document belongs to
            filename: Name of the file
            file_type: Type of the file
            file_size: Size of the file in bytes
            openai_file_id: ID of the file in OpenAI

        Returns:
            Created document data or None if creation failed
        """
        try:
            response = self.client.table("documents").insert({
                "user_id": user_id,
                "assistant_id": assistant_id,
                "filename": filename,
                "file_type": file_type,
                "file_size": file_size,
                "openai_file_id": openai_file_id,
                "storage_path": storage_path,
                "file_url": file_url,
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            logging.error(f"Failed to create document: {e}")
            return None

    def get_assistant_documents(self, assistant_id: str) -> List[Dict[str, Any]]:
        """
        Get all documents for an assistant.

        Args:
            assistant_id: ID of the assistant

        Returns:
            List of document data
        """
        try:
            response = self.client.table("documents").select("*").eq("assistant_id", assistant_id).execute()
            return response.data or []

        except Exception as e:
            logging.error(f"Failed to get assistant documents: {e}")
            return []

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document.

        Args:
            document_id: ID of the document to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            response = self.client.table("documents").delete().eq("id", document_id).execute()
            return bool(response.data)

        except Exception as e:
            logging.error(f"Failed to delete document: {e}")
            return False

    # Chat operations

    def create_chat_thread(self, assistant_id: str, user_id: str, openai_thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Create a new chat thread.

        Args:
            assistant_id: ID of the assistant
            user_id: ID of the user
            openai_thread_id: ID of the thread in OpenAI

        Returns:
            Created thread data or None if creation failed
        """
        try:
            response = self.client.table("chat_threads").insert({
                "assistant_id": assistant_id,
                "user_id": user_id,
                "openai_thread_id": openai_thread_id,
                "created_at": datetime.utcnow().isoformat(),
                "last_message_at": datetime.utcnow().isoformat()
            }).execute()

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            logging.error(f"Failed to create chat thread: {e}")
            return None

    def get_chat_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a chat thread by ID.

        Args:
            thread_id: ID of the thread

        Returns:
            Thread data or None if not found
        """
        try:
            response = self.client.table("chat_threads").select("*").eq("id", thread_id).execute()
            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            logging.error(f"Failed to get chat thread: {e}")
            return None

    def get_user_chat_threads(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all chat threads for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of thread data
        """
        try:
            response = self.client.table("chat_threads").select("*").eq("user_id", user_id).execute()
            return response.data or []

        except Exception as e:
            logging.error(f"Failed to get user chat threads: {e}")
            return []

    def create_chat_message(self, thread_id: str, role: str, content: str) -> Optional[Dict[str, Any]]:
        """
        Create a new chat message.

        Args:
            thread_id: ID of the thread
            role: Role of the message sender ("user" or "assistant")
            content: Content of the message

        Returns:
            Created message data or None if creation failed
        """
        try:
            # Update the thread's last_message_at timestamp
            self.client.table("chat_threads").update({
                "last_message_at": datetime.utcnow().isoformat()
            }).eq("id", thread_id).execute()

            # Create the message
            response = self.client.table("chat_messages").insert({
                "thread_id": thread_id,
                "role": role,
                "content": content,
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            logging.error(f"Failed to create chat message: {e}")
            return None

    def get_thread_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for a thread.

        Args:
            thread_id: ID of the thread

        Returns:
            List of message data
        """
        try:
            response = self.client.table("chat_messages").select("*").eq("thread_id", thread_id).order("created_at").execute()
            return response.data or []

        except Exception as e:
            logging.error(f"Failed to get thread messages: {e}")
            return []

    def delete_chat_thread(self, thread_id: str) -> bool:
        """
        Delete a chat thread and all its messages.

        Args:
            thread_id: ID of the thread to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Delete all messages in the thread
            self.client.table("chat_messages").delete().eq("thread_id", thread_id).execute()
            
            # Delete the thread
            response = self.client.table("chat_threads").delete().eq("id", thread_id).execute()
            return bool(response.data)

        except Exception as e:
            logging.error(f"Failed to delete chat thread: {e}")
            return False


# Create a singleton instance
db_service = DatabaseService()
