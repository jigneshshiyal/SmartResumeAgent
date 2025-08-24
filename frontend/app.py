import streamlit as st
import asyncio
import websockets
import json

# Set the title of the Streamlit app
st.title("WebSocket Chat App")

# --- Initial Setup and Session State ---
# Initialize chat history if it doesn't exist in the session state
# This is a key part of the fix: it ensures the list of messages is persistent
# across all user interactions and page refreshes.
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat Messages from History ---
# Loop through the stored messages and display them in the chat UI
# This loop ensures that the entire chat history is always redrawn
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Get User Input ---
# Get input from the user using Streamlit's chat input widget
if prompt := st.chat_input("What is up?"):
    # Add the user's message to the chat history immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display the user's message in the chat UI
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Use st.status to show a loading indicator.
    with st.status("Thinking...", expanded=True) as status:
        # Function to handle the WebSocket communication asynchronously
        async def chat_with_websocket(prompt):
            """
            Connects to the WebSocket, sends the user's prompt, and streams the response.
            """
            # Replace with the correct WebSocket URL for your backend server
            uri = "ws://localhost:8000/ws" 
            
            try:
                # Use an async context manager to connect to the WebSocket
                async with websockets.connect(uri) as websocket:
                    # Send the user's message to the server
                    await websocket.send(prompt)
                    
                    # Create a new, empty message for the assistant in the chat history
                    st.session_state.messages.append({"role": "assistant", "content": ""})
                    
                    # Use a placeholder to update the chat message in real-time
                    with st.chat_message("assistant"):
                        placeholder = st.empty()
                        full_response = ""
                        
                        # Loop to receive streamed chunks from the server
                        async for message in websocket:
                            full_response += message
                            # Update the placeholder with the streamed content
                            placeholder.markdown(full_response + "▌") # Add a blinking cursor effect
                        
                        # Update the final message content in the session state
                        st.session_state.messages[-1]["content"] = full_response
                        # Final update to remove the cursor
                        placeholder.markdown(full_response)
            except Exception as e:
                # Display an error message if the connection fails
                st.error(f"Error connecting to the WebSocket server: {e}")
                st.error("Please make sure your FastAPI server is running.")
        
        # Run the async WebSocket chat function using asyncio
        asyncio.run(chat_with_websocket(prompt))
        
        # Update the status to show completion and remove the spinner
        status.update(label="Response received!", state="complete", expanded=False)
        
    # The `st.rerun()` call has been removed. Streamlit will automatically handle
    # the re-rendering of the app now, which correctly preserves the session state.
