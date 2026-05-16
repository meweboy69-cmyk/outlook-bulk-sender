import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from time import sleep

def get_name_from_email(email):
    if not email or '@' not in email:
        return "Friend"
    local = email.split('@')[0].strip()
    for char in ['.', '_', '-', '+']:
        local = local.replace(char, ' ')
    name_parts = [part.capitalize() for part in local.split() if part.isalpha() or len(part) > 1]
    return ' '.join(name_parts) if name_parts else "there"

def send_email(sender_email, password, to_email, subject, body_template, attachments, is_html=False, delay=2):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        name = get_name_from_email(to_email)
        body = body_template.replace("{name}", name)
        
        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
        
        for filename, filebytes in attachments:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(filebytes)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
        
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True, f"✅ Sent to {to_email} ({name})"
    except Exception as e:
        return False, f"❌ Failed {to_email}: {str(e)}"

st.set_page_config(page_title="Outlook Bulk Sender", layout="wide")
st.title("📧 Outlook Bulk Email Sender")
st.caption("Send personalized emails with attachments using your Outlook account")

with st.sidebar:
    st.header("🔑 Your Outlook Credentials")
    sender_email = st.text_input("Your Outlook Email", placeholder="you@outlook.com")
    password = st.text_input("App Password", type="password", help="Use an App Password (not your normal password)")
    st.info("💡 How to create App Password: Microsoft account → Security → Advanced security options → App passwords")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("✉️ Email Content")
    subject = st.text_input("Subject", placeholder="Meeting reminder - {name}")
    body_template = st.text_area("Email Body (use {name} for personalized greeting)", 
                                 height=300,
                                 value="Hi {name},\n\nHope you're doing great!\n\nBest regards,\nYour Name")
    is_html = st.checkbox("Enable HTML formatting in email", value=True)

with col2:
    st.subheader("📋 Recipients")
    method = st.radio("How to add recipients?", ["Paste emails (one per line)", "Upload CSV file"])
    
    if method == "Paste emails (one per line)":
        emails_text = st.text_area("Paste emails here", height=200)
        email_list = [e.strip() for e in emails_text.splitlines() if e.strip()]
    else:
        csv_file = st.file_uploader("Upload CSV", type=["csv"])
        email_list = []
        if csv_file:
            df = pd.read_csv(csv_file)
            email_col = next((col for col in df.columns if 'email' in col.lower()), None)
            if email_col:
                email_list = df[email_col].astype(str).dropna().tolist()
                st.success(f"✅ Loaded {len(email_list)} emails")
            else:
                st.error("CSV must contain a column with 'email' in the name")

st.subheader("📎 Attachments (same file(s) attached to every email)")
uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
attachments = [(f.name, f.getvalue()) for f in uploaded_files] if uploaded_files else []

delay = st.slider("Delay between emails (seconds)", 1, 10, 3)

if st.button("🚀 SEND ALL EMAILS", type="primary", use_container_width=True):
    if not sender_email or not password or not subject or not body_template:
        st.error("❌ Please fill in email, password, subject and body")
    elif len(email_list) == 0:
        st.error("❌ No recipients found")
    else:
        st.info(f"📤 Starting to send **{len(email_list)}** emails...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        log = st.expander("📜 Live Sending Log", expanded=True)
        
        success_count = failed_count = 0
        
        for i, email in enumerate(email_list):
            status_text.text(f"Sending {i+1}/{len(email_list)} → {email}")
            ok, message = send_email(sender_email, password, email, subject, body_template, attachments, is_html, delay)
            with log:
                st.write(message)
            if ok:
                success_count += 1
            else:
                failed_count += 1
            progress_bar.progress((i + 1) / len(email_list))
            sleep(delay)
        
        st.success(f"🎉 Finished! ✅ Success: {success_count} | ❌ Failed: {failed_count}")
        st.balloons()

st.caption("Made for you • Runs securely on your browser")