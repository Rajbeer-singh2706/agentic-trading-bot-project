"""
Streamlit UI for Agentic Trading Bot
Professional frontend connecting to FastAPI backend
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8000/api/v1"
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# Page configuration
st.set_page_config(
    page_title="Agentic Trading Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Utility Functions
# ============================================================================

def get_api_url(endpoint: str) -> str:
    """Build API URL"""
    return f"{API_BASE_URL}{endpoint}"


def check_api_health() -> bool:
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(get_api_url("/health"), timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


@st.cache_data(ttl=3600)
def get_health_status() -> Dict[str, Any]:
    """Get API health status (cached)"""
    try:
        response = requests.get(get_api_url("/health"), timeout=2)
        return response.json()
    except Exception as e:
        return {"status": "offline", "error": str(e)}


def create_session() -> Optional[str]:
    """Create a new session"""
    try:
        response = requests.post(get_api_url("/session"), timeout=5)
        if response.status_code == 200:
            return response.json().get("session_id")
        else:
            st.error(f"Failed to create session: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error creating session: {str(e)}")
        return None


def send_query(question: str, session_id: str) -> Optional[Dict[str, Any]]:
    """Send query to backend"""
    try:
        payload = {
            "question": question,
            "session_id": session_id
        }
        response = requests.post(
            get_api_url("/query"),
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Query failed: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.Timeout:
        st.error("Query timeout - backend is taking too long to respond")
        return None
    except Exception as e:
        st.error(f"Error sending query: {str(e)}")
        return None


def upload_documents(files: list, session_id: str) -> Optional[Dict[str, Any]]:
    """Upload documents to backend"""
    try:
        # Prepare file tuples for multipart upload
        file_list = []
        for uploaded_file in files:
            file_list.append(
                ("files", (uploaded_file.name, uploaded_file.getbuffer(), uploaded_file.type))
            )
        
        data = {"session_id": session_id}
        response = requests.post(
            get_api_url("/upload"),
            files=file_list,
            data=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error uploading documents: {str(e)}")
        return None


# ============================================================================
# Session State Management
# ============================================================================

def init_session_state():
    """Initialize session state"""
    if "session_id" not in st.session_state:
        session_id = create_session()
        st.session_state.session_id = session_id
        st.session_state.session_created_at = datetime.now()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "uploaded_docs" not in st.session_state:
        st.session_state.uploaded_docs = []


def is_session_valid() -> bool:
    """Check if session is still valid"""
    if "session_created_at" not in st.session_state:
        return False
    
    elapsed = (datetime.now() - st.session_state.session_created_at).total_seconds()
    return elapsed < SESSION_TIMEOUT


# ============================================================================
# UI Components
# ============================================================================

def render_header():
    """Render page header"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.image("🤖", width=50)
    
    with col2:
        st.title("Agentic Trading Bot")
        st.markdown("*Intelligent AI-powered trading assistant*")
    
    with col3:
        health = get_health_status()
        if health.get("status") == "healthy":
            st.success("🟢 API Connected")
        else:
            st.error("🔴 API Offline")


def render_sidebar():
    """Render sidebar with options"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Session info
        st.subheader("Session")
        if st.session_state.get("session_id"):
            st.code(st.session_state.session_id[:8] + "...", language="text")
            st.caption(f"Created: {st.session_state.session_created_at.strftime('%H:%M:%S')}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 New Session"):
                    st.session_state.session_id = create_session()
                    st.session_state.session_created_at = datetime.now()
                    st.session_state.messages = []
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.messages = []
                    st.rerun()
        
        st.divider()
        
        # Document management
        st.subheader("📄 Documents")
        if st.session_state.get("uploaded_docs"):
            st.write(f"Uploaded: {len(st.session_state.uploaded_docs)} documents")
            for doc in st.session_state.uploaded_docs:
                st.caption(f"✓ {doc['name']}")
        else:
            st.caption("No documents uploaded yet")
        
        st.divider()
        
        # API Settings
        st.subheader("🔌 API Config")
        api_url = st.text_input(
            "Backend URL",
            value=API_BASE_URL,
            help="FastAPI backend URL"
        )
        if api_url != API_BASE_URL:
            globals()["API_BASE_URL"] = api_url
        
        st.divider()
        
        # About
        st.subheader("ℹ️ About")
        st.markdown("""
        **Version**: 1.0.0  
        **Framework**: Streamlit + FastAPI  
        **Status**: Production Ready
        """)


def render_chat_interface():
    """Render chat interface"""
    st.subheader("💬 Chat")
    
    # Display message history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message["content"])
                    
                    # Display sources if available
                    if message.get("sources"):
                        with st.expander("📚 Sources"):
                            for i, source in enumerate(message["sources"], 1):
                                st.caption(f"**Source {i}**: {source.get('title', 'Unknown')}")
                                if source.get("content"):
                                    st.text(source["content"][:200] + "...")
                    
                    # Display metadata if available
                    if message.get("metadata"):
                        with st.expander("📊 Metadata"):
                            st.json(message["metadata"])
    
    st.divider()
    
    # Input area
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask a question...",
            placeholder="Type your question here",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    # Process input
    if send_button and user_input:
        if not st.session_state.session_id:
            st.error("No active session. Please refresh the page.")
            return
        
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Show loading state
        with st.spinner("🤔 Thinking..."):
            response = send_query(user_input, st.session_state.session_id)
        
        if response:
            # Add assistant response to history
            assistant_message = {
                "role": "assistant",
                "content": response.get("answer", "No response"),
                "sources": response.get("sources", []),
                "metadata": {
                    "confidence": response.get("confidence", 0),
                    "response_time": response.get("response_time", 0),
                    "model": response.get("model", "Unknown")
                }
            }
            st.session_state.messages.append(assistant_message)
            st.rerun()


def render_document_upload():
    """Render document upload section"""
    st.subheader("📤 Upload Documents")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            help="Supported formats: PDF, DOCX, TXT"
        )
    
    with col2:
        if uploaded_files:
            if st.button("📤 Upload", use_container_width=True):
                if not st.session_state.session_id:
                    st.error("No active session. Please refresh the page.")
                    return
                
                with st.spinner(f"Uploading {len(uploaded_files)} file(s)..."):
                    result = upload_documents(uploaded_files, st.session_state.session_id)
                
                if result:
                    st.success(f"✅ Uploaded {result.get('successful_uploads', 0)} file(s)")
                    
                    # Update uploaded docs list
                    for file in uploaded_files:
                        st.session_state.uploaded_docs.append({
                            "name": file.name,
                            "size": len(file.getbuffer()),
                            "uploaded_at": datetime.now().isoformat()
                        })
                    
                    st.rerun()
    
    # Display upload info
    if uploaded_files:
        st.info(f"📋 Selected {len(uploaded_files)} file(s) for upload")
        for file in uploaded_files:
            st.caption(f"• {file.name} ({file.size / 1024:.1f} KB)")


def render_analytics():
    """Render analytics dashboard"""
    st.subheader("📊 Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Session ID",
            st.session_state.session_id[:8] + "..." if st.session_state.session_id else "N/A"
        )
    
    with col2:
        st.metric(
            "Messages",
            len(st.session_state.messages)
        )
    
    with col3:
        st.metric(
            "Documents",
            len(st.session_state.uploaded_docs)
        )
    
    with col4:
        if st.session_state.session_id:
            elapsed = (datetime.now() - st.session_state.session_created_at).total_seconds()
            st.metric(
                "Session Time",
                f"{int(elapsed)}s"
            )


def render_help():
    """Render help section"""
    with st.expander("❓ Help & Documentation"):
        st.markdown("""
        ### How to Use
        
        1. **Chat**: Type your question and click Send
        2. **Upload Documents**: Upload PDF, DOCX, or TXT files
        3. **View Sources**: Click "Sources" to see reference materials
        4. **Manage Session**: Use sidebar to create new session or clear chat
        
        ### Features
        
        - 🤖 **AI-Powered**: Leverages advanced language models
        - 📄 **Document Upload**: Support for PDF, DOCX, TXT
        - 🔍 **Source Attribution**: See where answers come from
        - 💾 **Session Management**: Maintain conversation history
        - ⚡ **Real-time**: Instant responses
        
        ### Supported File Types
        
        - **PDF**: `.pdf` files
        - **Word**: `.docx` files
        - **Text**: `.txt` files
        
        ### Keyboard Shortcuts
        
        - `Ctrl + Enter`: Send message (when cursor in input)
        - `Escape`: Clear input
        
        ### API Endpoints
        
        - `GET /api/v1/health` - Health check
        - `POST /api/v1/session` - Create session
        - `POST /api/v1/query` - Send query
        - `POST /api/v1/upload` - Upload documents
        """)


# ============================================================================
# Main App
# ============================================================================

def main():
    """Main application"""
    # Initialize session state
    init_session_state()
    
    # Check API connectivity
    if not check_api_health():
        st.error("""
        ❌ **API Backend is Offline**
        
        Please ensure the FastAPI server is running:
        ```bash
        uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
        ```
        """)
        st.stop()
    
    # Render UI
    render_header()
    render_sidebar()
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📤 Upload", "📊 Analytics"])
    
    with tab1:
        render_chat_interface()
    
    with tab2:
        render_document_upload()
        st.divider()
        render_help()
    
    with tab3:
        render_analytics()
        st.divider()
        
        # Advanced info
        if st.checkbox("Show Advanced Info"):
            st.subheader("🔧 Debug Info")
            debug_info = {
                "session_id": st.session_state.session_id,
                "api_url": API_BASE_URL,
                "session_valid": is_session_valid(),
                "messages_count": len(st.session_state.messages),
                "documents_count": len(st.session_state.uploaded_docs),
            }
            st.json(debug_info)


if __name__ == "__main__":
    main()
