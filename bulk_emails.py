import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import streamlit as st

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)


# Sender email credentials
SENDER_EMAIL = 'amitpandeyblogs@gmail.com'
SENDER_PASSWORD = 'qsat tohx ajcq jwaj'

# Load recipient list
def load_recipients(filename):
    recipients = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            recipients.append({'name': row['name'], 'email': row['email']})
    return recipients

# Load message content
def load_message(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            attention = row['attention']
            subject = row['subject']
            message = row['message']
            return attention, subject, message
    return "", "", ""

# Send email
def send_bulk_email(recipients, attention, subject, message_template):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        for recipient in recipients:
            msg = MIMEMultipart()
            # msg['From'] = SENDER_EMAIL
            msg['From'] = formataddr(("IIM Indore Notification", SENDER_EMAIL))
            msg['To'] = recipient['email']
            msg['Subject'] = f"{attention} {subject}"

            # Format message with recipient's name
            personalized_message = message_template.replace('\\n', '\n').format(name=recipient['name'])
            msg.attach(MIMEText(personalized_message, 'plain'))

            server.send_message(msg)
            print(f"Email sent to {recipient['email']}")

        server.quit()
        print("All emails sent successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    recipients = load_recipients('recipients.csv')
    attention, subject, message_template = load_message('message.csv')
    send_bulk_email(recipients, attention, subject, message_template)
