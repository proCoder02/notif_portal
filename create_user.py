import streamlit as st
from db_connections import create_user, get_connection
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)
# def signup():
#     st.title("Create New Account")
#     new_username = st.text_input("Choose a Username")
#     new_password = st.text_input("Choose a Password", type="password")
#     role = st.selectbox("Role", ["student", "admin"])

#     if st.button("Register"):
#         if not new_username or not new_password:
#             st.error("Username and Password cannot be empty.")
#         else:
#             try:
#                 success = create_user(new_username, new_password, role)
#                 if success:
#                     st.success("Account created! Please log in.")
#                     st.session_state.show_signup = False
#                     st.rerun()
#                 else:
#                     st.error("Username already exists.")
#             except Exception as e:
#                 st.error(f"Error: {e}")
def signup():
    st.title("Sign Up")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    role = st.selectbox("Select Role", ["admin", "student"])
    conn=get_connection()
    cur = conn.cursor()

    if role == "admin":
        room_code = st.text_input("Create a Room Code")
        if st.button("Sign Up"):
            cur.execute("SELECT * FROM notif.rooms WHERE room_code = %s", (room_code,))
            if cur.fetchone():
                st.error("Room code already exists.")
            else:
                cur.execute("INSERT INTO notif.users (username, password, role, room_code) VALUES (%s, %s, %s, %s)",
                            (username, password, role, room_code))
                cur.execute("INSERT INTO notif.rooms (room_code, created_by) VALUES (%s, %s)", (room_code, username))
                conn.commit()
                st.success("Admin account created! Please go to login.")
    else:
        room_code = st.text_input("Enter Room Code to Join")
        if st.button("Sign Up"):
            cur.execute("SELECT * FROM notif.rooms WHERE room_code = %s", (room_code,))
            if not cur.fetchone():
                st.error("Invalid room code.")
            else:
                cur.execute("INSERT INTO notif.users (username, password, role, room_code) VALUES (%s, %s, %s, %s)",
                            (username, password, role, room_code))
                conn.commit()
                st.success("Student account created! Please go to login.")

    cur.close()
    conn.close()