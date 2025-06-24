import streamlit as st
import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8001"

def create_new_session():
    """Create a new chat session"""
    try:
        response = requests.post(f"{API_BASE_URL}/new-session")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error creating session: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def send_message(session_id, question):
    """Send message to chatbot"""
    try:
        payload = {
            "session_id": session_id,
            "question": question
        }
        response = requests.post(f"{API_BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error sending message: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def get_chat_history(session_id):
    """Get chat history for session"""
    try:
        response = requests.get(f"{API_BASE_URL}/session/{session_id}/history")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

# Streamlit App
st.set_page_config(page_title="Simple Chatbot", page_icon="🤖", layout="wide")

st.title("Chatbot")
st.markdown("---")

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for session management
with st.sidebar:
    st.header("Session Management")
    
    if st.button(" Start New Session", type="primary"):
        session_data = create_new_session()
        if session_data:
            st.session_state.session_id = session_data['session_id']
            st.session_state.chat_history = []
            st.success("New session started!")
            st.rerun()
    
    if st.session_state.session_id:
        st.success(f"Current Session: {st.session_state.session_id[:8]}...")
        
        if st.button(" Load Chat History"):
            history_data = get_chat_history(st.session_state.session_id)
            if history_data and history_data['history']:
                st.session_state.chat_history = []
                for msg in history_data['history']:
                    st.session_state.chat_history.append({
                        'question': msg['question'],
                        'answer': msg['answer'],
                        'timestamp': msg['created_at']
                    })
                st.success("Chat history loaded!")
                st.rerun()
    else:
        st.warning("No active session. Please start a new session.")

# Main chat interface
if st.session_state.session_id:
    st.subheader(" Chat Interface")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### Chat History")
        for i, chat in enumerate(st.session_state.chat_history):
            with st.container():
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown(f"**You:** {chat['question']}")
                with col2:
                    st.markdown(f"**Bot:** {chat['answer']}")
                st.markdown("---")
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_question = st.text_input("Ask a question:", placeholder="Type your message here...")
        with col2:
            submit_button = st.form_submit_button("Send 📤", type="primary")
        
        if submit_button and user_question.strip():
            # Send message to API
            response = send_message(st.session_state.session_id, user_question)
            if response:
                # Add to chat history
                st.session_state.chat_history.append({
                    'question': response['question'],
                    'answer': response['answer'],
                    'timestamp': 'Just now'
                })
                st.rerun()

else:
    st.info("👈 Please start a new session from the sidebar to begin chatting!")

# Footer
st.markdown("---")
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("**API Status:**")
with col2:
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            st.success("✅ Connected")
        else:
            st.error(" API Error")
    except:
        st.error(" API Offline") 