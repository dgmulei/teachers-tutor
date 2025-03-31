"""
Chat UI components for the AI Teaching Assistant Platform.
Provides UI elements for the chat interface.
"""

import streamlit as st
import time
from typing import Dict, Any, List, Optional

from services.database_service import db_service
from services.openai_service import openai_service


def format_message(role: str, content: str) -> None:
    """
    Format and display a chat message.

    Args:
        role: Role of the message sender ("user" or "assistant")
        content: Content of the message
    """
    if role == "user":
        st.chat_message("user").write(content)
    else:
        st.chat_message("assistant").write(content)


def display_chat_history(thread_id: str) -> None:
    """
    Display the chat history for a thread.

    Args:
        thread_id: ID of the chat thread
    """
    # Get messages from the database
    messages = db_service.get_thread_messages(thread_id)
    
    # Display messages
    for message in messages:
        format_message(message["role"], message["content"])


def create_thread_ui(assistant_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Create a new chat thread with an initial welcome message.

    Args:
        assistant_id: ID of the assistant
        user_id: ID of the user

    Returns:
        Created thread data or None if failed
    """
    # Create a thread in OpenAI
    openai_thread = openai_service.create_thread()
    
    if not openai_thread:
        st.error("Failed to create chat thread.")
        return None
    
    # Create a thread in the database
    thread = db_service.create_chat_thread(
        assistant_id=assistant_id,
        user_id=user_id,
        openai_thread_id=openai_thread.id
    )
    
    if not thread:
        st.error("Failed to create chat thread in the database.")
        return None
    
    # Add welcome message from assistant
    welcome_message = (
        "Hey there! "
        "I'm here to quiz you one question at a time based on the key topics from your teacher's unit review sheet. "
        "If you get a question right, we'll move forward. If you're unsure or make a mistake, no worries — "
        "I'll guide you with a follow-up or hint to help you lock it in. Ready to start?"
    )
    
    # Create the welcome message in OpenAI
    openai_service.client.beta.threads.messages.create(
        thread_id=openai_thread.id,
        role="assistant",
        content=welcome_message
    )
    
    # Save welcome message to database
    db_service.create_chat_message(
        thread_id=thread["id"],
        role="assistant",
        content=welcome_message
    )
    
    return thread


def chat_ui(assistant_id: str, user_id: str) -> None:
    """
    Display the chat UI for an assistant.

    Args:
        assistant_id: ID of the assistant
        user_id: ID of the user
    """
    # Get the assistant from the database
    assistant = db_service.get_assistant(assistant_id)
    
    if not assistant:
        st.error("Assistant not found.")
        return
    
    # Check if the assistant belongs to the current user
    if assistant["user_id"] != user_id:
        st.error("You don't have permission to chat with this assistant.")
        return
    
    st.title(f"Test Preparation with {assistant['name']}")
    
    # Check if we have a current thread
    current_thread_id = st.session_state.get("current_thread_id")
    
    if not current_thread_id:
        # Create a new thread
        thread = create_thread_ui(assistant_id, user_id)
        
        if thread:
            st.session_state["current_thread_id"] = thread["id"]
            current_thread_id = thread["id"]
        else:
            return
    
    # Get the thread from the database
    thread = db_service.get_chat_thread(current_thread_id)
    
    if not thread:
        st.error("Chat thread not found.")
        return
    
    # Display chat history
    display_chat_history(current_thread_id)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Display user message
        format_message("user", prompt)
        
        # Save user message to database
        db_service.create_chat_message(
            thread_id=current_thread_id,
            role="user",
            content=prompt
        )
        
        # Create a message in the OpenAI thread
        openai_service.create_message(
            thread_id=thread["openai_thread_id"],
            content=prompt
        )
        
        # Run the assistant
        with st.spinner("Thinking..."):
            result = openai_service.run_assistant(
                thread_id=thread["openai_thread_id"],
                assistant_id=assistant["openai_assistant_id"]
            )
            
            if result:
                # Get the latest message (assistant's response)
                messages = result.get("messages", [])
                
                if messages:
                    # Get the last message from the assistant
                    # Note: messages are already in newest-first order from the API
                    for message in messages:
                        if message.role == "assistant":
                            # Display assistant message
                            assistant_response = ""
                            
                            # Process the message content
                            for content_item in message.content:
                                if content_item.type == "text":
                                    assistant_response = content_item.text.value
                            
                            if assistant_response:
                                # Display the message
                                format_message("assistant", assistant_response)
                                
                                # Save assistant message to database
                                db_service.create_chat_message(
                                    thread_id=current_thread_id,
                                    role="assistant",
                                    content=assistant_response
                                )
                            
                            break
            else:
                st.error("Failed to get a response from the assistant.")


def chat_history_ui(user_id: str) -> None:
    """
    Display the chat history UI.

    Args:
        user_id: ID of the current user
    """
    st.title("Tutor Session History")
    
    # Get the user's chat threads
    threads = db_service.get_user_chat_threads(user_id)
    
    if not threads:
        st.info("You don't have any chat history yet.")
        return
    
    # Display threads in a list
    for thread in threads:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                # Get the assistant name
                assistant_name = thread.get("assistants", {}).get("name", "Unknown Assistant")
                st.write(f"**{assistant_name}**")
                
                # Show thread name or creation date
                if thread.get("name"):
                    st.write(thread["name"])
                else:
                    created_at = thread.get("created_at", "")
                    if created_at:
                        st.write(f"Created: {created_at[:10]}")
            
            with col2:
                # Show last message time
                last_message_at = thread.get("last_message_at", "")
                if last_message_at:
                    st.write(f"Last message: {last_message_at[:10]}")
            
            with col3:
                # Continue chat button
                if st.button("Continue", key=f"continue_{thread['id']}"):
                    # Set the current thread and assistant in session state and navigate to chat
                    st.session_state["current_assistant_id"] = thread["assistant_id"]
                    st.session_state["current_thread_id"] = thread["id"]
                    st.session_state["current_page"] = "chat"
                    st.rerun()
                
                # Delete thread button
                if st.button("Delete", key=f"delete_{thread['id']}"):
                    if db_service.delete_chat_thread(thread["id"]):
                        # Also delete the OpenAI thread
                        openai_service.delete_thread(thread["openai_thread_id"])
                        st.success("Chat thread deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete chat thread.")


def chat_page(user_id: str) -> None:
    """
    Display the chat page.

    Args:
        user_id: ID of the current user
    """
    # Check if we have a current assistant
    current_assistant_id = st.session_state.get("current_assistant_id")
    
    if current_assistant_id:
        # Add a back button
        if st.button("← Back to Assistants"):
            st.session_state["current_assistant_id"] = None
            st.session_state["current_thread_id"] = None
            st.session_state["current_page"] = "assistants"
            st.rerun()
        
        # Display the chat UI
        chat_ui(current_assistant_id, user_id)
    else:
        # Display the chat history UI
        chat_history_ui(user_id)
