import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
import psycopg2
import psycopg2.extras
# Config
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_ADDRESS = 'amitpandeyblogs@gmail.com'
EMAIL_PASSWORD = 'qsat tohx ajcq jwaj'
DATABASE_URL = os.getenv('DATABASE_URL', 'dbname=notif user=postgres password=0326 host=localhost')
TIMEZONE = pytz.timezone('Asia/Kolkata')
CHECK_INTERVAL = 30  # minutes

# DB Connection
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="notif",
        user="postgres",
        password="0326"
    )

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notif.deadlines (
                    id SERIAL PRIMARY KEY,
                    text_message TEXT NOT NULL,
                    deadline_date TIMESTAMP NOT NULL,
                    reminder_sent BOOLEAN DEFAULT FALSE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notif.recipients (
                    id SERIAL PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE
                );
            """)
        conn.commit()

# Send email
def send_reminder_email(email, subject, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = subject

        body = f"""
        REMINDER: Upcoming Deadline!

        {message}

        This is an automated reminder. Please do not reply.
        """
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        st.error(f"Error sending email to {email}: {str(e)}")
        return False

# Reminder check
def check_and_send_reminders():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                now_utc = datetime.utcnow()
                reminder_time = now_utc + timedelta(hours=24)

                cur.execute("""
                    SELECT * FROM notif.deadlines
                    WHERE deadline_date <= %s AND reminder_sent = FALSE;
                """, (reminder_time,))
                deadlines = cur.fetchall()

                cur.execute("SELECT email FROM recipients;")
                recipients = [r['email'] for r in cur.fetchall()]

                sent_count = 0
                for deadline in deadlines:
                    for email in recipients:
                        subject = f"Deadline Reminder: {deadline['deadline_date'].strftime('%b %d')}"
                        if send_reminder_email(email, subject, deadline['text_message']):
                            sent_count += 1

                    # Mark deadline as sent
                    cur.execute("UPDATE notif.deadlines SET reminder_sent = TRUE WHERE id = %s;", (deadline['id'],))
                conn.commit()
                return sent_count
    except Exception as e:
        st.error(f"Error in reminder check: {str(e)}")
        return 0

# APScheduler
def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send_reminders, 'interval', minutes=CHECK_INTERVAL, next_run_time=datetime.now())
    scheduler.start()
    return scheduler

# Streamlit App

def deadline_reminder_scheduler():
    st.title("📅 Deadline Reminder System")
    init_db()

    if 'scheduler' not in st.session_state:
        st.session_state.scheduler = init_scheduler()

    with st.expander("📤 Upload Files", expanded=True):
        deadline_file = st.file_uploader("Deadlines Excel", type=['xlsx'])
        recipient_file = st.file_uploader("Recipients Excel", type=['xlsx'])

        if st.button("Process Files"):
            if deadline_file and recipient_file:
                try:
                    deadlines_df = pd.read_excel(deadline_file)
                    if 'text_message' not in deadlines_df or 'deadline_date' not in deadlines_df:
                        st.error("Deadlines file must contain 'text_message' and 'deadline_date'")
                        return

                    recipients_df = pd.read_excel(recipient_file)
                    if 'Email' not in recipients_df:
                        st.error("Recipients file must contain 'Email' column")
                        return

                    with get_connection() as conn:
                        with conn.cursor() as cur:
                            for _, row in deadlines_df.iterrows():
                                cur.execute("""
                                    INSERT INTO notif.deadlines (text_message, deadline_date)
                                    VALUES (%s, %s)
                                    ON CONFLICT DO NOTHING;
                                """, (row['text_message'], pd.to_datetime(row['deadline_date'])))

                            for email in recipients_df['Email']:
                                cur.execute("""
                                    INSERT INTO recipients (email)
                                    VALUES (%s)
                                    ON CONFLICT (email) DO NOTHING;
                                """, (email,))
                        conn.commit()

                    st.success("Files processed successfully!")
                    st.dataframe(deadlines_df)
                    st.dataframe(recipients_df)

                except Exception as e:
                    st.error(f"Error processing files: {str(e)}")
            else:
                st.warning("Please upload both files.")

    with st.expander("🗃️ Database Status"):
        try:
            with get_connection() as conn:
                deadlines_df = pd.read_sql("SELECT * FROM notif.deadlines", conn)
                recipients_df = pd.read_sql("SELECT * FROM notif.recipients", conn)

            st.write("**Deadlines:**")
            st.dataframe(deadlines_df if not deadlines_df.empty else pd.DataFrame(["No data found"]))

            st.write("**Recipients:**")
            st.dataframe(recipients_df if not recipients_df.empty else pd.DataFrame(["No data found"]))
        except Exception as e:
            st.error(f"Unable to load database: {str(e)}")

    with st.expander("⚙️ System Controls"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Run Reminder Check Now"):
                with st.spinner("Checking for reminders..."):
                    count = check_and_send_reminders()
                    if count > 0:
                        st.success(f"Sent {count} reminders!")
                    else:
                        st.info("No reminders to send.")

        with col2:
            if st.button("Reset Database"):
                init_db()
                st.success("Database structure ensured (tables rechecked).")

    st.write("## 🔄 Scheduler Status")
    st.info(f"Automatic reminder checks running every {CHECK_INTERVAL} minutes")
    next_run = datetime.now() + timedelta(minutes=CHECK_INTERVAL)
    st.caption(f"Next check: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    deadline_reminder_scheduler()
