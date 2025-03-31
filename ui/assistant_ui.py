"""
Assistant management UI components for the AI Teaching Assistant Platform.
Provides UI elements for creating and managing assistants.
"""

import streamlit as st
from typing import Dict, Any, List, Optional

from services.database_service import db_service
from services.openai_service import openai_service


def create_assistant_ui(user_id: str) -> None:
    """
    Display the UI for creating a new assistant.

    Args:
        user_id: ID of the current user
    """
    st.header("Create New Assistant")
    
    with st.form("create_assistant_form"):
        name = st.text_input("Assistant Name", placeholder="e.g., AP Biology Helper")
        description = st.text_area("Description", placeholder="Describe what this assistant will help with...")
        instructions = st.text_area(
            "Instructions", 
            placeholder="Provide detailed instructions for the assistant...",
            help="These instructions will guide how the assistant responds to questions."
        )
        
        submit = st.form_submit_button("Create Assistant")
        
        if submit:
            if not name:
                st.error("Please provide a name for the assistant.")
                return
            
            with st.spinner("Creating assistant..."):
                # Create the assistant in OpenAI
                assistant = openai_service.create_assistant(
                    name=name,
                    description=description or "",
                    instructions=instructions or f"You are a helpful teaching assistant for {name}."
                )
                
                if assistant:
                    # Create the assistant in the database
                    db_assistant = db_service.create_assistant(
                        user_id=user_id,
                        name=name,
                        description=description or "",
                        openai_assistant_id=assistant.id
                    )
                    
                    if db_assistant:
                        st.success(f"Assistant '{name}' created successfully!")
                        # Refresh the page to show the new assistant
                        st.rerun()
                    else:
                        st.error("Failed to create assistant in the database.")
                else:
                    st.error("Failed to create assistant with OpenAI.")


def list_assistants_ui(user_id: str) -> None:
    """
    Display the UI for listing user's assistants.

    Args:
        user_id: ID of the current user
    """
    st.header("Your Assistants")
    
    # Get the user's assistants
    assistants = db_service.get_user_assistants(user_id)
    
    if not assistants:
        st.info("You haven't created any assistants yet.")
        return
    
    # Display assistants in a grid
    cols = st.columns(3)
    
    for i, assistant in enumerate(assistants):
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(assistant["name"])
                if assistant.get("description"):
                    st.write(assistant["description"])
                
                # Show buttons for actions
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Student View", key=f"chat_{assistant['id']}"):
                        # Set the current assistant in session state and navigate to chat
                        st.session_state["current_assistant_id"] = assistant["id"]
                        st.session_state["current_page"] = "chat"
                        st.rerun()
                
                with col2:
                    if st.button("Manage", key=f"manage_{assistant['id']}"):
                        # Set the current assistant in session state and navigate to manage
                        st.session_state["current_assistant_id"] = assistant["id"]
                        st.session_state["current_page"] = "manage_assistant"
                        st.rerun()


def manage_assistant_ui(assistant_id: str, user_id: str) -> None:
    """
    Display the UI for managing an assistant.

    Args:
        assistant_id: ID of the assistant to manage
        user_id: ID of the current user
    """
    # Get the assistant from the database
    assistant = db_service.get_assistant(assistant_id)
    
    if not assistant:
        st.error("Assistant not found.")
        return
    
    # Check if the assistant belongs to the current user
    if assistant["user_id"] != user_id:
        st.error("You don't have permission to manage this assistant.")
        return
    
    st.header(f"Manage Assistant: {assistant['name']}")
    
    # Create tabs for different management sections
    tab1, tab2, tab3 = st.tabs(["Details", "Documents", "Settings"])
    
    with tab1:
        # Assistant details
        with st.form("update_assistant_form"):
            name = st.text_input("Assistant Name", value=assistant["name"])
            description = st.text_area("Description", value=assistant.get("description", ""))
            
            # Get the OpenAI assistant to get the instructions
            openai_assistant = openai_service.get_assistant(assistant["openai_assistant_id"])
            instructions = ""
            if openai_assistant:
                instructions = openai_assistant.instructions or ""
            
            instructions = st.text_area("Instructions", value=instructions)
            
            submit = st.form_submit_button("Update Assistant")
            
            if submit:
                if not name:
                    st.error("Please provide a name for the assistant.")
                    return
                
                with st.spinner("Updating assistant..."):
                    # Update the assistant in OpenAI
                    updated_openai = openai_service.update_assistant(
                        assistant_id=assistant["openai_assistant_id"],
                        data={
                            "name": name,
                            "description": description,
                            "instructions": instructions
                        }
                    )
                    
                    if updated_openai:
                        # Update the assistant in the database
                        updated_db = db_service.update_assistant(
                            assistant_id=assistant_id,
                            data={
                                "name": name,
                                "description": description
                            }
                        )
                        
                        if updated_db:
                            st.success("Assistant updated successfully!")
                        else:
                            st.error("Failed to update assistant in the database.")
                    else:
                        st.error("Failed to update assistant with OpenAI.")
    
    with tab2:
        # Document management
        st.subheader("Documents")
        
        # Get the assistant's documents
        documents = db_service.get_assistant_documents(assistant_id)
        
        # Upload new document
        st.write("Upload a new document:")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "docx", "doc", "txt", "md"],
            key=f"upload_{assistant_id}"
        )
        
        if uploaded_file:
            from services.document_service import document_service
            
            with st.spinner("Processing document..."):
                # Process the uploaded file
                document = document_service.process_file(
                    file=uploaded_file,
                    filename=uploaded_file.name,
                    user_id=user_id,
                    assistant_id=assistant_id
                )
                
                if document:
                    st.success(f"Document '{uploaded_file.name}' uploaded successfully!")
                    # Refresh the documents list
                    documents = db_service.get_assistant_documents(assistant_id)
                else:
                    st.error(f"Failed to upload document '{uploaded_file.name}'.")
        
        # Display existing documents
        if documents:
            st.write("Existing documents:")
            
            for doc in documents:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(doc["filename"])
                
                with col2:
                    st.write(f"Status: {doc['status']}")
                
                with col3:
                    if st.button("Delete", key=f"delete_{doc['id']}"):
                        with st.spinner("Deleting document..."):
                            # Delete the document from the database only
                            if db_service.delete_document(doc["id"]):
                                st.success(f"Document '{doc['filename']}' deleted successfully!")
                                # Refresh the documents list
                                st.rerun()
                            else:
                                st.error("Failed to delete document from the database.")
        else:
            st.info("No documents uploaded yet.")
    
    with tab3:
        # Settings
        st.subheader("Settings")
        
        # Delete assistant
        st.write("Danger Zone:")
        
        if st.button("Delete Assistant", type="primary", use_container_width=True):
            confirm = st.text_input(
                "Type the assistant name to confirm deletion",
                placeholder=assistant["name"]
            )
            
            if confirm == assistant["name"]:
                with st.spinner("Deleting assistant..."):
                    # Delete the assistant from OpenAI
                    if openai_service.delete_assistant(assistant["openai_assistant_id"]):
                        # Delete the assistant from the database
                        if db_service.delete_assistant(assistant_id):
                            st.success("Assistant deleted successfully!")
                            
                            # Navigate back to the assistants list
                            st.session_state["current_assistant_id"] = None
                            st.session_state["current_page"] = "assistants"
                            st.rerun()
                        else:
                            st.error("Failed to delete assistant from the database.")
                    else:
                        st.error("Failed to delete assistant from OpenAI.")


def assistant_page(user_id: str) -> None:
    """
    Display the assistant management page.

    Args:
        user_id: ID of the current user
    """
    st.title("AI Teaching Assistants")
    
    # Check if we're managing a specific assistant
    if st.session_state.get("current_page") == "manage_assistant" and st.session_state.get("current_assistant_id"):
        # Add a back button
        if st.button("← Back to Assistants"):
            st.session_state["current_assistant_id"] = None
            st.session_state["current_page"] = "assistants"
            st.rerun()
        
        # Display the manage assistant UI
        manage_assistant_ui(st.session_state["current_assistant_id"], user_id)
    else:
        # Display the create and list assistants UI
        create_assistant_ui(user_id)
        st.divider()
        list_assistants_ui(user_id)
