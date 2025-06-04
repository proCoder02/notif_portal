
import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from icalendar import Calendar, Event, vCalAddress, vText
import re
from datetime import datetime
import pytz
def sent():
    def parse_time_range(time_str):
        """Parse time range string into start and end times"""
        time_str = time_str.replace('<br>', ' ').strip()
        match = re.search(r'(\d+:\d+\s*[AP]M)\s*-\s*(\d+:\d+\s*[AP]M)', time_str)
        if match:
            start_str = match.group(1).replace(' ', '')
            end_str = match.group(2).replace(' ', '')
            return start_str, end_str
        return None, None

    def create_ics_event(event_name, event_date, start_time_str, end_time_str, sender_email, recipient_email, location="Virtual"):
        """Create ICS calendar event"""
        cal = Calendar()
        cal.add('prodid', '-//Exam Calendar//')
        cal.add('version', '2.0')
        cal.add('method', 'REQUEST')

        event = Event()
        event.add('summary', event_name)
        event.add('location', location)

        organizer = vCalAddress(f'mailto:{sender_email}')
        organizer.params['cn'] = vText('Exam Scheduler')
        event['organizer'] = organizer

        attendee = vCalAddress(f'mailto:{recipient_email}')
        attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
        attendee.params['CN'] = vText(recipient_email)
        event.add('attendee', attendee, encode=0)

        start_dt = datetime.strptime(f"{event_date} {start_time_str}", "%Y-%m-%d %I:%M%p")
        end_dt = datetime.strptime(f"{event_date} {end_time_str}", "%Y-%m-%d %I:%M%p")
        tz = pytz.timezone('Asia/Kolkata')
        event.add('dtstart', tz.localize(start_dt))
        event.add('dtend', tz.localize(end_dt))
        event.add('dtstamp', datetime.now(tz))
        event['uid'] = f"{event_name}-{event_date}-{recipient_email}@examscheduler.com"

        cal.add_component(event)
        return cal.to_ical()

    def send_email(sender, password, receiver, subject, body, ics_data):
        """Send email with ICS attachment"""
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        part = MIMEBase('text', 'calendar')
        part.set_payload(ics_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="exam_invite.ics"')
        part.add_header('Content-Class', 'urn:content-classes:calendarmessage')
        msg.attach(part)

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            st.error(f"Error sending email: {str(e)}")
            return False

    # Streamlit UI
    st.title("📅 Exam Schedule Invite Sender")

    uploaded_file = st.file_uploader("Upload Exam Schedule (Excel)", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        time_ranges = {}
        for col in df.columns[5:10]:
            if 'Session' in col:
                start, end = parse_time_range(col)
                if start and end:
                    time_ranges[col] = (start, end)

        events = []
        for _, row in df.iterrows():
            if pd.isna(row['Date']):
                continue
            date_str = str(row['Date']).split()[0]
            for i, col in enumerate(df.columns[5:10]):
                event_name = row[col]
                if pd.notna(event_name) and event_name != "" and col in time_ranges:
                    start_time, end_time = time_ranges[col]
                    events.append({
                        'date': date_str,
                        'session': f"Session {i+1}",
                        'name': event_name,
                        'start': start_time,
                        'end': end_time
                    })

        if events:
            st.success(f"Found {len(events)} exam events in schedule")

            st.subheader("Email Configuration")
            sender_email = st.text_input("Sender Email")
            sender_password = st.text_input("Sender Password", type="password")
            email_subject = st.text_input("Email Subject", "Exam Schedule Invitation")

            st.subheader("Recipient Configuration")
            recipient_mode = st.radio("Select Mode", ['Single Email', 'Upload Recipient Excel'])
            recipient_emails = []

            if recipient_mode == 'Upload Recipient Excel':
                uploaded_recipients = st.file_uploader("Upload Recipient Email List (Excel with column 'Email')", type=["xlsx"], key="recipients")
                if uploaded_recipients:
                    recipient_df = pd.read_excel(uploaded_recipients)
                    if 'Email' in recipient_df.columns:
                        recipient_emails = recipient_df['Email'].dropna().tolist()
                    else:
                        st.error("Excel must contain a column named 'Email'")
            else:
                single_email = st.text_input("Recipient Email")
                if single_email:
                    recipient_emails = [single_email]

            if st.button("Send Calendar Invites"):
                if not sender_email or not sender_password or not recipient_emails:
                    st.warning("Please fill all required fields")
                else:
                    progress_bar = st.progress(0)
                    total_tasks = len(events) * len(recipient_emails)
                    task_count = 0
                    sent_count = 0

                    for recipient in recipient_emails:
                        for event in events:
                            ics_data = create_ics_event(
                                event['name'],
                                event['date'],
                                event['start'],
                                event['end'],
                                sender_email,
                                recipient
                            )

                            body = f"""
                            You have an upcoming exam:

                            Exam: {event['name']}
                            Date: {event['date']}
                            Time: {event['start']} to {event['end']}
                            Session: {event['session']}

                            This invite has been added to your calendar.
                            """

                            if send_email(
                                sender_email,
                                sender_password,
                                recipient,
                                email_subject,
                                body,
                                ics_data
                            ):
                                sent_count += 1

                            task_count += 1
                            progress_bar.progress(task_count / total_tasks)

                    st.success(f"Sent {sent_count}/{total_tasks} invites successfully!")
        else:
            st.warning("No exam events found in the schedule")

