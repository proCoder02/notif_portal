import streamlit as st
import smtplib
import pandas as pd
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from admin_insights import show_admin_insights
from create_user import signup
from custom_css import inject_custom_css
from db_connections import fetch_user
from deadline_reminder_email import deadline_reminders
from bulk_calendar_inivite_email import sent  

# --- Credentials (for demo only, use env vars or st.secrets in production)
SENDER_EMAIL = 'amitpandeyblogs@gmail.com'
SENDER_PASSWORD = 'qsat tohx ajcq jwaj'


# --- Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.polls = []
    st.session_state.notifications = []
    st.session_state.responses = {}



def login():
    st.title("Classroom Portal Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = fetch_user(username)
        if user and user[1] == password:
            st.session_state.logged_in = True
            st.session_state.username = user[0]
            st.session_state.role = user[2]
            st.success(f"Welcome, {user[0]}!")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.markdown("Don't have an account?")
    if st.button("Create New Account"):
        st.session_state.show_signup = True
        st.rerun()

# --- Email Sender
def send_bulk_email(recipients, attention, subject, message_template):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        for recipient in recipients:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient['email']
            msg['Subject'] = f"{attention} {subject}"
            personalized_message = message_template.replace('\\n', '\n').format(name=recipient['name'])
            msg.attach(MIMEText(personalized_message, 'plain'))
            server.send_message(msg)

        server.quit()
        return True, "All emails sent successfully."
    except Exception as e:
        return False, str(e)

# --- Admin Dashboard
def admin_dashboard():
    st.sidebar.title("Admin Dashboard")
    tab = st.sidebar.radio("Select Action", [
        "Post Notification",
        "Post Poll",
        "Send Bulk Email",
        "Email Bulk Invites",
        "Deadline Reminders",
        "View Insights"
    ])

    st.title(f"Admin Panel – {st.session_state.username}")

    if tab == "Post Notification":
        st.text('Post Notifications')
    elif tab == "Post Poll":
        st.text('Post Poll')
    elif tab == "Send Bulk Email":
        st.text('Send Emails')
    elif tab == "Email Bulk Invites":
        st.text('Email Bulk Invites')
    elif tab == ("Deadline Reminders"):
        st.text("Deadline Reminders")
    elif tab == "View Insights":
        show_admin_insights()


    if tab == "Post Notification":
        notif = st.text_area("Enter Notification")
        if st.button("Post Notification"):
            st.session_state.notifications.append({
                "text": notif,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.success("Notification posted.")

    elif tab == "Post Poll":
        question = st.text_input("Poll Question")
        options = st.text_area("Poll Options (comma separated)").split(",")
        if st.button("Post Poll"):
            poll_id = len(st.session_state.polls)
            st.session_state.polls.append({
                "id": poll_id,
                "question": question,
                "options": options,
                "votes": {opt.strip(): 0 for opt in options}
            })
            st.success("Poll created.")

    elif tab == "Send Bulk Email":
        st.subheader("Upload CSV Files")
        recipients_file = st.file_uploader("Recipients CSV", type="csv")
        message_file = st.file_uploader("Message CSV", type="csv")

        if st.button("Send Emails"):
            if recipients_file and message_file:
                try:
                    recipients_df = pd.read_csv(recipients_file)
                    message_df = pd.read_csv(message_file)

                    recipients = recipients_df.to_dict('records')
                    attention = message_df['attention'][0]
                    subject = message_df['subject'][0]
                    message_template = message_df['message'][0]

                    success, msg = send_bulk_email(recipients, attention, subject, message_template)
                    if success:
                        st.success(msg)
                    else:
                        st.error(f"Failed: {msg}")
                except Exception as e:
                    st.error(f"Error processing CSVs: {e}")
            else:
                st.warning("Please upload both CSV files.")
    elif tab=="Email Bulk Invites":
        sent()
    elif tab=="Deadline Reminders":
        deadline_reminders()



# --- Student Dashboard

def student_dashboard():
    if "notif_views" not in st.session_state:
        st.session_state.notif_views = {}  # {notif_id: set(usernames)}
    st.sidebar.title("Student Dashboard")
    st.title(f"Welcome {st.session_state.username}")

    st.subheader("📢 Notifications")
 
    for idx, notif in enumerate(reversed(st.session_state.notifications)):
        st.info(f"{notif['timestamp']} - {notif['text']}")
        notif_id = len(st.session_state.notifications) - 1 - idx
        views = st.session_state.notif_views.setdefault(notif_id, set())
        views.add(st.session_state.username)


    st.subheader("🗳️ Active Polls")
    for poll in st.session_state.polls:
        if poll["id"] not in st.session_state.responses.get(st.session_state.username, []):
            st.write(f"**{poll['question']}**")
            choice = st.radio("Select an option", poll["options"], key=f"poll_{poll['id']}")
            if st.button("Vote", key=f"vote_{poll['id']}"):
                choice = choice.strip()
                poll["votes"][choice] = poll["votes"].get(choice, 0) + 1
                st.session_state.responses.setdefault(st.session_state.username, []).append(poll["id"])
                st.success("Your vote has been submitted.")
                st.rerun()
        else:
            st.write(f"✅ You already voted: {poll['question']}")

    st.subheader("📊 Poll Results")
    for poll in st.session_state.polls:
        st.write(f"**{poll['question']}**")
        total = sum(poll["votes"].values())
        for opt, count in poll["votes"].items():
            percent = (count / total * 100) if total else 0
            st.write(f"{opt}: {count} vote(s) – {percent:.2f}%")

# --- Logout
def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()


def main():
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False

    if not st.session_state.logged_in:
        if st.session_state.show_signup:
            signup()
        else:
            login()
    elif st.session_state.role == "admin":
        admin_dashboard()
    elif st.session_state.role == "student":
        student_dashboard()

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        logout()
if __name__ == "__main__":
    main()
