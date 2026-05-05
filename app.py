import streamlit as st
import requests

BASE_URL = "http://localhost:8000" # backend endpoint 

st.set_page_config(
    page_title="📈 Stock Market Agentic Chatbot",
    page_icon = "📈",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("Stock Market Agentic Chatbot")



###