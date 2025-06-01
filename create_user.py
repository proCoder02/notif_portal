import streamlit as st
from db_connections import create_user
def signup():
    st.title("Create New Account")
    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type="password")
    role = st.selectbox("Role", ["student", "admin"])

    if st.button("Register"):
        if not new_username or not new_password:
            st.error("Username and Password cannot be empty.")
        else:
            try:
                success = create_user(new_username, new_password, role)
                if success:
                    st.success("Account created! Please log in.")
                    st.session_state.show_signup = False
                    st.rerun()
                else:
                    st.error("Username already exists.")
            except Exception as e:
                st.error(f"Error: {e}")
