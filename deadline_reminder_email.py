
import streamlit as st
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import hashlib
from email.utils import formataddr
def deadline_reminders():
    # Email Config
    SENDER_EMAIL = 'amitpandeyblogs@gmail.com'
    SENDER_PASSWORD = 'qsat tohx ajcq jwaj'

    # APScheduler
    scheduler = BackgroundScheduler()
    scheduler.start()

    # To track and avoid duplicate jobs
    scheduled_jobs = {}

    # Email sending function
    def send_email(subject, body, recipients):
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            # msg['From'] = SENDER_EMAIL
            msg['From'] = formataddr(("IIM Indore Notification", SENDER_EMAIL))
            msg['To'] = ', '.join(recipients)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, recipients, msg.as_string())

            print(f"Email sent: {subject}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    # Schedule reminders
    def schedule_reminders(row, recipients):
        message = row['text_message']
        deadline = row['deadline_date']
        deadline = pd.to_datetime(deadline)
        key = hashlib.md5((message + str(deadline)).encode()).hexdigest()

        # Cancel old jobs
        if key in scheduled_jobs:
            for job in scheduled_jobs[key]:
                scheduler.remove_job(job.id)

        # 24-hour reminder
        time_24h = deadline - timedelta(hours=24)
        if time_24h > datetime.now():
            job_24h = scheduler.add_job(
                send_email,
                'date',
                run_date=time_24h,
                args=[
                    f"Reminder: {message}",
                    f"Your event is scheduled at {deadline.strftime('%Y-%m-%d %H:%M:%S')}",
                    recipients
                ]
            )
        else:
            job_24h = None

        # 15-minute reminder
        time_15m = deadline - timedelta(minutes=15)
        if time_15m > datetime.now():
            job_15m = scheduler.add_job(
                send_email,
                'date',
                run_date=time_15m,
                args=[
                    f"Urgent Reminder: {message}",
                    f"Your event is coming up at {deadline.strftime('%Y-%m-%d %H:%M:%S')}",
                    recipients
                ]
            )
        else:
            job_15m = None

        scheduled_jobs[key] = [job for job in [job_24h, job_15m] if job is not None]

    # Streamlit UI
    st.title("📧 Excel-Based Multi-User Reminder System")

    msg_file = st.file_uploader("Upload Excel with Messages (text_message, deadline_date)", type=['xlsx'])
    email_file = st.file_uploader("Upload Excel with Recipients (email column)", type=['xlsx'])

    if msg_file and email_file:
        try:
            msg_df = pd.read_excel(msg_file)
            msg_df.columns = msg_df.columns.str.strip().str.lower()  # 👈 Normalize
            email_df = pd.read_excel(email_file)
            email_df.columns = email_df.columns.str.strip().str.lower()  # 👈 Normalize
            
            # Parse and clean
            msg_df['deadline_date'] = pd.to_datetime(msg_df['deadline_date'])
            email_df['email'] = email_df['email'].astype(str)
            recipients = email_df['email'].dropna().tolist()

            st.subheader("📄 Messages:")
            st.dataframe(msg_df)

            st.subheader("📧 Recipients:")
            st.dataframe(email_df)

            if st.button("✅ Schedule Reminders"):
                for _, row in msg_df.iterrows():
                    schedule_reminders(row, recipients)
                st.success("All reminders scheduled!")

        except Exception as e:
            st.error(f"Error: {e}")
