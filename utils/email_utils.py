import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def send_email(to_email, subject, body):
    # Check if secrets are available
    if "email" not in st.secrets:
        st.error("Email secrets not configured. Please add SMTP details to .streamlit/secrets.toml")
        return False
        
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = st.secrets["email"]["user"] # minifablabecc@outlook.com
    smtp_password = st.secrets["email"]["password"]

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

def send_login_link(to_email, link):
    subject = "MiniFabLab Login Link"
    body = f"""
    <html>
        <body>
            <h3>MiniFabLab Reservation System</h3>
            <p>Click the link below to login to the reservation system:</p>
            <p><a href="{link}">{link}</a></p>
            <p>This link will expire in 1 hour.</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, body)

def send_reservation_confirmation(to_email, group_name, date, slot):
    subject = f"Reservation Confirmation - {group_name}"
    body = f"""
    <html>
        <body>
            <h3>Reservation Confirmed</h3>
            <p>Your reservation for <b>{group_name}</b> has been successfully made.</p>
            <p><b>Date:</b> {date}</p>
            <p><b>Slot:</b> {slot}</p>
            <p>Thank you!</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, body)
