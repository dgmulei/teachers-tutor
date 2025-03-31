"""
OpenAI service for the AI Teaching Assistant Platform.
Handles interactions with the OpenAI API.
"""

import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from openai.types.beta import Assistant, Thread
from openai.types.beta.threads import Run

from config.settings import OPENAI_API_KEY, ASSISTANT_MODEL


class OpenAIService:
    """Service class for handling OpenAI API operations."""

    def __init__(self):
        """Initialize the OpenAI client."""
        try:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def create_assistant(self, name: str, description: str, instructions: str) -> Optional[Assistant]:
        """
        Create a new assistant in OpenAI.

        Args:
            name: Name of the assistant
            description: Description of the assistant
            instructions: Instructions for the assistant

        Returns:
            Created assistant or None if creation failed
        """
        try:
            assistant = self.client.beta.assistants.create(
                name=name,
                description=description,
                instructions=instructions,
                model=ASSISTANT_MODEL,
                tools=[{"type": "file_search"}]  # Enable file search capability
            )
            return assistant

        except Exception as e:
            logging.error(f"Failed to create OpenAI assistant: {e}")
            return None

    def get_assistant(self, assistant_id: str) -> Optional[Assistant]:
        """
        Get an assistant by ID.

        Args:
            assistant_id: ID of the assistant

        Returns:
            Assistant object or None if not found
        """
        try:
            return self.client.beta.assistants.retrieve(assistant_id)

        except Exception as e:
            logging.error(f"Failed to get OpenAI assistant: {e}")
            return None

    def update_assistant(self, assistant_id: str, data: Dict[str, Any]) -> Optional[Assistant]:
        """
        Update an assistant.

        Args:
            assistant_id: ID of the assistant to update
            data: Data to update

        Returns:
            Updated assistant or None if update failed
        """
        try:
            return self.client.beta.assistants.update(
                assistant_id=assistant_id,
                **data
            )

        except Exception as e:
            logging.error(f"Failed to update OpenAI assistant: {e}")
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
            response = self.client.beta.assistants.delete(assistant_id)
            return response.deleted

        except Exception as e:
            logging.error(f"Failed to delete OpenAI assistant: {e}")
            return False

    def upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Upload a file to OpenAI.

        Args:
            file_path: Path to the file to upload

        Returns:
            Uploaded file data or None if upload failed
        """
        try:
            with open(file_path, "rb") as file:
                response = self.client.files.create(
                    file=file,
                    purpose="assistants"
                )
            return response

        except Exception as e:
            logging.error(f"Failed to upload file to OpenAI: {e}")
            return None

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from OpenAI.

        Args:
            file_id: ID of the file to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            response = self.client.files.delete(file_id)
            return response.deleted

        except Exception as e:
            logging.error(f"Failed to delete OpenAI file: {e}")
            return False

    def create_thread(self) -> Optional[Thread]:
        """
        Create a new thread in OpenAI.

        Returns:
            Created thread or None if creation failed
        """
        try:
            return self.client.beta.threads.create()

        except Exception as e:
            logging.error(f"Failed to create OpenAI thread: {e}")
            return None

    def create_message(self, thread_id: str, content: str) -> Optional[Dict[str, Any]]:
        """
        Create a new message in a thread.

        Args:
            thread_id: ID of the thread
            content: Content of the message

        Returns:
            Created message data or None if creation failed
        """
        try:
            return self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=content
            )

        except Exception as e:
            logging.error(f"Failed to create OpenAI message: {e}")
            return None

    def run_assistant(self, thread_id: str, assistant_id: str) -> Optional[Dict[str, Any]]:
        """
        Run an assistant on a thread.

        Args:
            thread_id: ID of the thread
            assistant_id: ID of the assistant

        Returns:
            Run result data or None if run failed
        """
        try:
            # Create a run
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )

            # Wait for the run to complete
            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

                if run_status.status == "completed":
                    # Get the messages from the thread
                    messages = self.client.beta.threads.messages.list(thread_id=thread_id)
                    return {
                        "run": run_status,
                        "messages": messages.data
                    }
                elif run_status.status in ["failed", "cancelled", "expired"]:
                    logging.error(f"Run failed with status: {run_status.status}")
                    return None

        except Exception as e:
            logging.error(f"Failed to run OpenAI assistant: {e}")
            return None

    def delete_thread(self, thread_id: str) -> bool:
        """
        Delete a thread.

        Args:
            thread_id: ID of the thread to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            response = self.client.beta.threads.delete(thread_id)
            return response.deleted

        except Exception as e:
            logging.error(f"Failed to delete OpenAI thread: {e}")
            return False


# Create a singleton instance
openai_service = OpenAIService()
