# import smtplib
# import csv
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# # Sender email credentials
# SENDER_EMAIL = 'amitpandeyblogs@gmail.com'
# SENDER_PASSWORD = 'qsat tohx ajcq jwaj'

# # Load recipient list
# def load_recipients(filename):
#     recipients = []
#     with open(filename, newline='') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             recipients.append({'name': row['name'], 'email': row['email']})
#     return recipients

# # Load message content
# def load_message(filename):
#     with open(filename, newline='') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             attention = row['attention']
#             subject = row['subject']
#             message = row['message']
#             return attention, subject, message
#     return "", "", ""

# # Send email
# def send_bulk_email(recipients, attention, subject, message_template):
#     try:
#         server = smtplib.SMTP('smtp.gmail.com', 587)
#         server.starttls()
#         server.login(SENDER_EMAIL, SENDER_PASSWORD)

#         for recipient in recipients:
#             msg = MIMEMultipart()
#             msg['From'] = SENDER_EMAIL
#             msg['To'] = recipient['email']
#             msg['Subject'] = f"{attention} {subject}"

#             # Format message with recipient's name
#             personalized_message = message_template.replace('\\n', '\n').format(name=recipient['name'])
#             msg.attach(MIMEText(personalized_message, 'plain'))

#             server.send_message(msg)
#             print(f"Email sent to {recipient['email']}")

#         server.quit()
#         print("All emails sent successfully.")

#     except Exception as e:
#         print(f"An error occurred: {e}")

# if __name__ == "__main__":
#     recipients = load_recipients('recipients.csv')
#     attention, subject, message_template = load_message('message.csv')
#     send_bulk_email(recipients, attention, subject, message_template)

import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tempfile
import pandas as pd

# Email credentials (Move to secure vault/env for production)
SENDER_EMAIL = 'amitpandeyblogs@gmail.com'
SENDER_PASSWORD = 'qsat tohx ajcq jwaj'

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

# --- IN ADMIN DASHBOARD FUNCTION ---

elif tab == "Send Bulk Email":
    st.subheader("Send Bulk Email")
    recipients_file = st.file_uploader("Upload Recipients CSV", type="csv", key="recipients")
    message_file = st.file_uploader("Upload Message CSV", type="csv", key="message")

    if st.button("Send Emails"):
        if recipients_file and message_file:
            try:
                recipients_df = pd.read_csv(recipients_file)
                message_df = pd.read_csv(message_file)

                recipients = recipients_df.to_dict('records')
                attention = message_df['attention'][0]
                subject = message_df['subject'][0]
                message_template = message_df['message'][0]

                success, result = send_bulk_email(recipients, attention, subject, message_template)
                if success:
                    st.success(result)
                else:
                    st.error(f"Failed: {result}")

            except Exception as e:
                st.error(f"Error reading CSVs: {e}")
        else:
            st.warning("Please upload both recipient and message files.")
