import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate, make_msgid
import streamlit as st

def send_email(to_email, subject, html_body):
    # Check if secrets are available
    if "email" not in st.secrets:
        st.error("Email secrets not configured. Please add SMTP details to .streamlit/secrets.toml")
        return False
        
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = st.secrets["email"]["user"]
    smtp_password = st.secrets["email"]["password"]
    sender_email = st.secrets.get("email", {}).get("sender", smtp_user)

    # Build multipart/alternative so Outlook sees a plain-text version too
    msg = MIMEMultipart("alternative")
    msg['From'] = formataddr(("MiniFabLab ECC", sender_email))
    msg['To'] = to_email
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid(domain="gmail.com")
    msg['Reply-To'] = sender_email

    # Plain-text fallback (strip HTML tags)
    plain_text = re.sub(r'<[^>]+>', '', html_body)
    plain_text = re.sub(r'\s+', ' ', plain_text).strip()

    msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

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
    subject = "Lien de connexion - MiniFabLab ECC"
    body = f"""\
<html>
  <body>
    <h3>MiniFabLab ECC - Connexion</h3>
    <p>Bonjour,</p>
    <p>Cliquez sur le lien ci-dessous pour vous connecter :</p>
    <p><a href="{link}">{link}</a></p>
    <p>Ce lien expirera dans 1 heure.</p>
    <br>
    <p>MiniFabLab ECC</p>
  </body>
</html>"""
    return send_email(to_email, subject, body)

def send_reservation_confirmation(to_email, group_name, date, slot):
    subject = f"Confirmation de réservation - {group_name}"
    body = f"""\
<html>
  <body>
    <h3>Réservation Confirmée</h3>
    <p>Bonjour,</p>
    <p>Votre réservation pour <b>{group_name}</b> a été effectuée avec succès.</p>
    <p><b>Date :</b> {date}</p>
    <p><b>Créneau :</b> {slot}</p>
    <br>
    <p>MiniFabLab ECC</p>
  </body>
</html>"""
    return send_email(to_email, subject, body)
