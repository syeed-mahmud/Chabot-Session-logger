import streamlit as st
import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8001"

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def create_new_session():
    """Create a new chat session"""
    try:
        response = requests.post(f"{API_BASE_URL}/new-session")
        if response.status_code == 200:
            data = response.json()
            st.session_state.session_id = data['session_id']
            st.session_state.chat_history = []
            return True, data['message']
        else:
            return False, f"Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"

def send_message(question):
    """Send a message to the chatbot"""
    if not st.session_state.session_id:
        return False, "No active session. Please create a new session first."
    
    try:
        payload = {
            "session_id": st.session_state.session_id,
            "question": question
        }
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"

def get_chat_history():
    """Get chat history for current session"""
    if not st.session_state.session_id:
        return False, "No active session"
    
    try:
        response = requests.get(f"{API_BASE_URL}/session/{st.session_state.session_id}/history")
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"

def check_api_status():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        return response.status_code == 200
    except:
        return False

# Streamlit UI
st.set_page_config(
    page_title="Odoo XML-RPC Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Odoo XML-RPC Code Generator Chatbot")
st.markdown("Ask questions and get Python code for Odoo XML-RPC queries!")

# Sidebar for session management
with st.sidebar:
    st.header("Session Management")
    
    # API Status
    api_status = check_api_status()
    if api_status:
        st.success("✅ API is running")
    else:
        st.error("❌ API is not responding")
        st.stop()
    
    # Current session info
    if st.session_state.session_id:
        st.info(f"📝 Session ID: {st.session_state.session_id[:8]}...")
    else:
        st.warning("No active session")
    
    # New session button
    if st.button("🆕 Start New Session"):
        success, message = create_new_session()
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)
    
    # Refresh history button
    if st.button("🔄 Refresh History") and st.session_state.session_id:
        success, data = get_chat_history()
        if success:
            st.session_state.chat_history = data.get('history', [])
            st.success("History refreshed!")
        else:
            st.error(f"Failed to refresh: {data}")

# Main chat interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat Interface")
    
    # Question input
    with st.form("chat_form"):
        question = st.text_area(
            "Ask a question about Odoo data:",
            placeholder="e.g., Show me all partners from USA",
            help="Ask questions about Odoo data and get XML-RPC Python code"
        )
        submitted = st.form_submit_button("Send Message", type="primary")
        
        if submitted and question:
            if not st.session_state.session_id:
                st.error("Please create a new session first!")
            else:
                with st.spinner("Generating code..."):
                    success, response = send_message(question)
                    if success:
                        # Add to local history
                        st.session_state.chat_history.append({
                            'question': question,
                            'answer': response['answer'],
                            'created_at': datetime.now().isoformat()
                        })
                        st.success("Message sent!")
                        st.rerun()
                    else:
                        st.error(f"Failed to send message: {response}")

with col2:
    st.header("📊 Quick Actions")
    
    # Example questions
    st.subheader("💡 Example Questions")
    example_questions = [
        "Show me all partners",
        "Get sales orders from this month",
        "Find all products with price > 100",
        "Show me recent invoices",
        "Get purchase orders by partner"
    ]
    
    for example in example_questions:
        if st.button(f"📝 {example}", key=f"example_{example}"):
            if st.session_state.session_id:
                with st.spinner("Processing..."):
                    success, response = send_message(example)
                    if success:
                        st.session_state.chat_history.append({
                            'question': example,
                            'answer': response['answer'],
                            'created_at': datetime.now().isoformat()
                        })
                        st.rerun()
            else:
                st.error("Please create a session first!")

# Chat History Display
st.header("📜 Chat History")

if st.session_state.chat_history:
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        with st.container():
            st.markdown(f"**Q{len(st.session_state.chat_history)-i}:** {chat['question']}")
            
            # Parse and display the formatted response
            answer = chat['answer']
            if "📝 Generated Code:" in answer and "🔍 Execution Results:" in answer:
                # Split into sections
                parts = answer.split("🔍 Execution Results:")
                if len(parts) >= 2:
                    code_section = parts[0].replace("📝 Generated Code:", "").strip()
                    results_section = parts[1].split("📊 Data Summary:")[0].strip()
                    
                    # Clean code section (remove ```python and ```)
                    if code_section.startswith("```python"):
                        code_section = code_section[9:].strip()
                    if code_section.endswith("```"):
                        code_section = code_section[:-3].strip()
                    
                    # Display sections
                    st.subheader("📝 Generated Code")
                    st.code(code_section, language='python')
                    
                    st.subheader("🔍 Execution Results")
                    if results_section.strip():
                        st.text(results_section)
                    else:
                        st.info("Code executed successfully (no output)")
                    
                    # Show data summary if available
                    if "📊 Data Summary:" in answer:
                        data_summary = answer.split("📊 Data Summary:")[1].split("\n")[0].strip()
                        st.info(f"📊 {data_summary}")
                    
                    # Show warnings if any
                    if "⚠️ Warning:" in answer:
                        warning = answer.split("⚠️ Warning:")[1].strip()
                        st.warning(f"⚠️ {warning}")
                else:
                    # Fallback: display as markdown
                    st.markdown(answer)
            else:
                # Legacy format or error - display as code
                if "❌ Error:" in answer:
                    st.error("❌ Execution Error")
                st.code(answer, language='python')
            
            # Timestamp
            if 'created_at' in chat:
                try:
                    timestamp = datetime.fromisoformat(chat['created_at'].replace('Z', '+00:00'))
                    st.caption(f"Generated at: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    st.caption(f"Generated at: {chat['created_at']}")
            
            st.divider()
else:
    st.info("No chat history yet. Start by creating a session and asking a question!")

# Footer
st.markdown("---")
st.markdown("🔧 **Status**: Ready to generate Odoo XML-RPC Python code based on your questions!") 