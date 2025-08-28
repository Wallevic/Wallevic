import streamlit as st
from PIL import Image
import requests
import json
import time

# --- CONFIGURE THESE ---
AAUA_LOGO_PATH = "aaua_logo.png"  # Place your logo file in the same directory
BACKEND_API_URL = "http://127.0.0.1:5000/chat"  # Flask backend endpoint

# --- SIDEBAR NAVIGATION ---
sidebar_options = [
    ("Dashboard", "house"),
    ("Playground", "grid"),
    ("API Keys", "key"),
    ("Plans", "database"),
    ("Login/Signup", "person"),
    ("Agents", "robot"),
    ("AI Starter Kits", "lightbulb"),
    ("Community", "people"),
    ("Documentation", "book"),
    ("Connect with us", "link-45deg"),
]

# --- PROMPT SUGGESTIONS/CARDS ---
prompt_cards = [
    {"icon": "📝", "text": "What are the admission requirements for Computer Science?"},
    {"icon": "🏠", "text": "Tell me about hostel accommodation options"},
    {"icon": "📅", "text": "What is the current academic calendar?"},
    {"icon": "💸", "text": "How much are the tuition fees for Law program?"},
    {"icon": "🎓", "text": "What programs are available in Faculty of Science?"},
    {"icon": "📚", "text": "How do I apply for admission to AAUA?"},
]

st.set_page_config(
    page_title="AAUA AI Assistant", 
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .block-container {padding-top: 1rem;}
    .stButton>button {
        border-radius: 24px;
        background: linear-gradient(90deg, #400075 0%, #6a0dad 100%);
        color: white;
        border: none;
        padding: 8px 24px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #6a0dad 0%, #400075 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(106, 13, 173, 0.3);
    }
    .prompt-card {
        display: inline-block;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8eaff 100%);
        border: 1px solid #e0e6ff;
        border-radius: 18px;
        padding: 22px 26px;
        margin: 12px;
        min-width: 240px;
        box-shadow: 0 2px 8px rgba(64, 0, 117, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .prompt-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(64, 0, 117, 0.15);
        border-color: #400075;
    }
    .prompt-icon {
        font-size: 30px;
        margin-bottom: 12px;
        display: block;
    }
    .chat-message {
        padding: 16px 20px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        word-wrap: break-word;
    }
    .user-message {
        background: linear-gradient(135deg, #400075 0%, #6a0dad 100%);
        color: white;
        margin-left: auto;
        text-align: right;
    }
    .bot-message {
        background: #f8f9ff;
        border: 1px solid #e0e6ff;
        color: #333;
    }
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 16px 20px;
        background: #f8f9ff;
        border-radius: 18px;
        max-width: 80%;
    }
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #400075;
        animation: typing 1.4s infinite ease-in-out;
    }
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
    .sidebar-header {
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid #e0e6ff;
        margin-bottom: 20px;
    }
    .sidebar-nav-item {
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 12px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .sidebar-nav-item:hover {
        background: linear-gradient(135deg, #400075 0%, #6a0dad 100%);
        color: white;
    }
    .main-header {
        background: linear-gradient(135deg, #400075 0%, #6a0dad 100%);
        color: white;
        padding: 24px 32px;
        border-radius: 16px;
        margin-bottom: 24px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class="sidebar-header">
            <h2>🎓 AAUA AI Assistant</h2>
            <p style="color: #666; font-size: 14px;">Your intelligent guide to AAUA</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    for name, icon in sidebar_options:
        st.markdown(
            f'<div class="sidebar-nav-item"><span style="font-size:18px;margin-right:10px;">{icon}</span>{name}</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Connection status
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")

# --- MAIN AREA ---
st.markdown("""
    <div class="main-header">
        <h1>🤖 AAUA AI Assistant</h1>
        <p>Ask me anything about Adekunle Ajasin University Akungba!</p>
    </div>
""", unsafe_allow_html=True)

# --- PROMPT CARDS ---
st.markdown("### 💡 Quick Questions")
st.markdown("Click on any card below to ask a common question:")

# Create columns for prompt cards
cols = st.columns(3)
for i, card in enumerate(prompt_cards):
    with cols[i % 3]:
        if st.button(
            f"{card['icon']} {card['text']}", 
            key=f"card_{i}",
            help="Click to ask this question"
        ):
            st.session_state.quick_question = card['text']

# --- SESSION STATE FOR CHAT HISTORY ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "processing" not in st.session_state:
    st.session_state.processing = False

# Handle quick questions
if "quick_question" in st.session_state and not st.session_state.processing:
    question = st.session_state.quick_question
    del st.session_state.quick_question
    st.session_state.chat_history.append(("user", question))
    st.session_state.processing = True
    st.rerun()  # Rerun to display the user message immediately

# If processing a quick question or previous input
if st.session_state.processing:
    # Display typing indicator
    st.markdown("""
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Get the last user message to process
    last_message = next((msg for sender, msg in reversed(st.session_state.chat_history) if sender == "user"), None)
    
    if last_message:
        try:
            with st.spinner("🤖 AI is thinking..."):
                response = requests.post(
                    BACKEND_API_URL,
                    json={"message": last_message},
                    timeout=30
                )
                
                if response.status_code == 200:
                    bot_response = response.json().get("response", "Sorry, I didn't understand that.")
                else:
                    bot_response = f"Backend error (Status: {response.status_code}). Please try again."
                
                st.session_state.chat_history.append(("bot", bot_response))
                
        except requests.exceptions.Timeout:
            st.session_state.chat_history.append(("bot", "Request timed out. Please try again."))
        except requests.exceptions.ConnectionError:
            st.session_state.chat_history.append(("bot", "Cannot connect to backend. Please ensure the Flask server is running."))
        except Exception as e:
            st.session_state.chat_history.append(("bot", f"Error: {str(e)}"))
    
    st.session_state.processing = False
    st.rerun()

# --- CHAT DISPLAY ---
st.markdown("### 💬 Chat History")

# Display chat messages
for sender, message in st.session_state.chat_history:
    if sender == "user":
        st.markdown(
            f'<div class="chat-message user-message">{message}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="chat-message bot-message">{message}</div>',
            unsafe_allow_html=True
        )

# --- CHAT INPUT AREA ---
st.markdown("---")
st.markdown("### 💭 Ask a Question")

with st.form(key="chat_form"):
    col1, col2 = st.columns([4, 1])
    with col1:
        chat_input = st.text_input(
            "Type your question here...",
            key="chat_input",
            label_visibility="collapsed",
            placeholder="e.g., What are the admission requirements for Computer Science?"
        )

    with col2:
        send_btn = st.form_submit_button("Send", use_container_width=True)


# Handle form submit
if send_btn and chat_input.strip() and not st.session_state.processing:
    st.session_state.chat_history.append(("user", chat_input.strip()))
    st.session_state.processing = True
    st.rerun()
    

# --- FOOTER ---
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>🎓 AAUA AI Assistant | Powered by SambaNova LLM & LlamaIndex</p>
        <p>Final Year Project - Adekunle Ajasin University Akungba</p>
    </div>
""", unsafe_allow_html=True)