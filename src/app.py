import streamlit as st
import requests, sys  
from utils.exceptions import TradingBotException

BASE_URL = "http://localhost:8000" # backend endpoint 

st.set_page_config(
    page_title="📈 Stock Market Agentic Chatbot",
    page_icon = "📈",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("Stock Market Agentic Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: Upload documents
with st.sidebar:
    st.header("📄 Upload Documents")
    st.markdown("Upload **stock market PDFs or DOCX** to create knowledge base.")
    uploaded_files = st.file_uploader("choose files", type=["pdf","docx"], accept_multiple_files=True)

    if st.button("Upload and Ingest"):
        if uploaded_files:
            print("--")
            files = []

            for f in uploaded_files:
                file_data = f.read()
                if not file_data:
                    continue
                files.append(("files", (getattr(f, "name", "file.pdf"), file_data, f.type)))
            
            if files:
                try:
                    with st.spinner("Uploading and processing files..."):
                        response = requests.post(f"{BASE_URL}/upload", files=files)
                        if response.status_code == 200:
                            st.success("✅ Files uploaded and processed successfully!")
                        else:
                            st.error("❌ Upload failed: "+ response.text) 
                except Exception as e:
                    raise TradingBotException(e, sys)
            else:
                st.warning("Some files were emoty or unreadable.")




# streamlit run src/app.py