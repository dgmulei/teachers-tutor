"""
Document service for the AI Teaching Assistant Platform.
Handles document processing and file management.
"""

import os
import logging
import tempfile
from typing import Dict, Any, Optional, BinaryIO
import magic
import PyPDF2
from docx import Document as DocxDocument

from config.settings import ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from services.openai_service import openai_service
from services.database_service import db_service


class DocumentService:
    """Service class for handling document processing and file management."""

    def __init__(self):
        """Initialize the document service."""
        self.mime = magic.Magic(mime=True)

    def get_file_type(self, file: BinaryIO) -> str:
        """
        Get the MIME type of a file.

        Args:
            file: File object to check

        Returns:
            MIME type of the file
        """
        # Read the first 2048 bytes for MIME detection
        header = file.read(2048)
        file.seek(0)  # Reset file pointer
        return self.mime.from_buffer(header)

    def validate_file(self, file: BinaryIO, filename: str) -> Optional[str]:
        """
        Validate a file for upload.

        Args:
            file: File object to validate
            filename: Name of the file

        Returns:
            Error message if validation fails, None if file is valid
        """
        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        if size > MAX_FILE_SIZE:
            return f"File size exceeds maximum limit of {MAX_FILE_SIZE / (1024 * 1024)}MB"

        # Check file extension
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return f"File type {ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"

        # Check MIME type
        mime_type = self.get_file_type(file)
        allowed_mimes = {
            "application/pdf": ".pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/msword": ".doc",
            "text/plain": ".txt",
            "text/markdown": ".md"
        }

        if mime_type not in allowed_mimes:
            return f"Invalid file type: {mime_type}"

        if allowed_mimes[mime_type] != ext:
            return f"File extension does not match content type"

        return None

    def extract_text(self, file: BinaryIO, file_type: str) -> Optional[str]:
        """
        Extract text from a document file.

        Args:
            file: File object to extract text from
            file_type: Type of the file

        Returns:
            Extracted text or None if extraction failed
        """
        try:
            if file_type == "application/pdf":
                # Extract text from PDF
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text

            elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                # Extract text from Word document
                doc = DocxDocument(file)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text

            elif file_type in ["text/plain", "text/markdown"]:
                # Read text file directly
                return file.read().decode('utf-8')

            else:
                logging.error(f"Unsupported file type for text extraction: {file_type}")
                return None

        except Exception as e:
            logging.error(f"Failed to extract text from file: {e}")
            return None

    def process_file(self, file: BinaryIO, filename: str, user_id: str, assistant_id: str) -> Optional[Dict[str, Any]]:
        """
        Process an uploaded file.

        Args:
            file: File object to process
            filename: Name of the file
            user_id: ID of the user uploading the file
            assistant_id: ID of the assistant this file belongs to

        Returns:
            Processed document data or None if processing failed
        """
        try:
            # Validate the file
            error = self.validate_file(file, filename)
            if error:
                logging.error(f"File validation failed: {error}")
                return None

            # Get file type
            file_type = self.get_file_type(file)

            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                # Write the uploaded file to the temporary file
                file.seek(0)
                temp_file.write(file.read())
                temp_file.flush()

                # Upload file to Supabase Storage
                storage_path = f"documents/{assistant_id}/{filename}"
                with open(temp_file.name, 'rb') as f:
                    response = db_service.client.storage.from_('documents').upload(
                        path=storage_path,
                        file=f,
                        file_options={"content-type": file_type}
                    )
                
                if not response:
                    logging.error("Failed to upload file to Supabase Storage")
                    return None
                
                # Get the public URL for the file
                file_url = db_service.client.storage.from_('documents').get_public_url(storage_path)
                
                # Create document in database
                document = db_service.create_document(
                    user_id=user_id,
                    assistant_id=assistant_id,
                    filename=filename,
                    file_type=file_type,
                    file_size=os.path.getsize(temp_file.name),
                    openai_file_id="manual_upload",  # Placeholder for manual upload
                    storage_path=storage_path,
                    file_url=file_url
                )

                # Clean up temporary file
                os.unlink(temp_file.name)

                return document

        except Exception as e:
            logging.error(f"Failed to process file: {e}")
            return None


# Create a singleton instance
document_service = DocumentService()
