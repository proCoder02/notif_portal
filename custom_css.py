import streamlit as st
def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background-color: #f8f9fa;
        }

        .css-1d391kg {  /* Main title class */
            color: #1a1a1a;
        }

        .stSidebar {
            background-color: #2c3e50;
            color: white;
        }

        .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4 {
            color: #ecf0f1;
        }

        .stButton>button {
            background-color: #3498db;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1em;
        }

        .stTextInput>div>div>input {
            border-radius: 6px;
            padding: 8px;
        }

        .stTextArea textarea {
            border-radius: 6px;
            padding: 8px;
        }

        .stRadio, .stFileUploader, .stTextInput, .stTextArea {
            padding-bottom: 1rem;
        }

        .stSuccess {
            background-color: #d1f0d7;
        }

        .stError {
            background-color: #f8d7da;
        }

        .stInfo {
            background-color: #d9edf7;
        }

        .stSubheader, .stTitle {
            color: #2c3e50;
        }

        .block-container {
            padding: 2rem 2rem 2rem 2rem;
        }

        </style>
    """, unsafe_allow_html=True)

