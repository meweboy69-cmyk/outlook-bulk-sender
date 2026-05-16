{\rtf1\ansi\ansicpg1252\cocoartf2868
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import smtplib\
from email.mime.multipart import MIMEMultipart\
from email.mime.text import MIMEText\
from email.mime.base import MIMEBase\
from email import encoders\
import pandas as pd\
from time import sleep\
\
def get_name_from_email(email):\
    """Automatically picks name from email address"""\
    if not email or '@' not in email:\
        return "Friend"\
    local = email.split('@')[0].strip()\
    # Replace dots, underscores, dashes with space\
    for char in ['.', '_', '-', '+']:\
        local = local.replace(char, ' ')\
    # Capitalize each word\
    name_parts = [part.capitalize() for part in local.split() if part.isalpha() or len(part) > 1]\
    return ' '.join(name_parts) if name_parts else "there"\
\
def send_email(sender_email, password, to_email, subject, body_template, attachments, is_html=False, delay=2):\
    try:\
        msg = MIMEMultipart()\
        msg['From'] = sender_email\
        msg['To'] = to_email\
        msg['Subject'] = subject\
        \
        # Replace \{name\} with actual name\
        name = get_name_from_email(to_email)\
        body = body_template.replace("\{name\}", name)\
        \
        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))\
        \
        # Add all attachments\
        for filename, filebytes in attachments:\
            part = MIMEBase('application', "octet-stream")\
            part.set_payload(filebytes)\
            encoders.encode_base64(part)\
            part.add_header('Content-Disposition', f'attachment; filename="\{filename\}"')\
            msg.attach(part)\
        \
        # Connect to Outlook SMTP\
        server = smtplib.SMTP('smtp.office365.com', 587)\
        server.starttls()\
        server.login(sender_email, password)\
        server.sendmail(sender_email, to_email, msg.as_string())\
        server.quit()\
        return True, f"\uc0\u9989  Sent to \{to_email\} (\{name\})"\
    except Exception as e:\
        return False, f"\uc0\u10060  Failed \{to_email\}: \{str(e)\}"\
\
# \uc0\u9472 \u9472  App UI \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \
st.set_page_config(page_title="Outlook Bulk Sender", layout="wide")\
st.title("\uc0\u55357 \u56551  Outlook Bulk Email Sender")\
st.caption("Send personalized emails with attachments using your Outlook account")\
\
# Sidebar - Credentials\
with st.sidebar:\
    st.header("\uc0\u55357 \u56593  Your Outlook Credentials")\
    sender_email = st.text_input("Your Outlook Email", placeholder="you@outlook.com")\
    password = st.text_input("App Password", type="password", \
                             help="Use an App Password (not your normal password) if you have 2FA enabled")\
    st.info("\uc0\u55357 \u56481  How to create App Password: Go to Microsoft account \u8594  Security \u8594  Advanced security options \u8594  App passwords")\
\
# Main form\
col1, col2 = st.columns([2, 1])\
\
with col1:\
    st.subheader("\uc0\u9993 \u65039  Email Content")\
    subject = st.text_input("Subject", placeholder="Meeting reminder - \{name\}")\
    body_template = st.text_area("Email Body (use \{name\} for personalized greeting)", \
                                 height=300,\
                                 value="Hi \{name\},\\n\\nHope you're doing great!\\n\\nBest regards,\\nYour Name",\
                                 placeholder="Hi \{name\}, ...")\
    is_html = st.checkbox("Enable HTML formatting in email", value=True)\
\
with col2:\
    st.subheader("\uc0\u55357 \u56523  Recipients")\
    method = st.radio("How to add recipients?", ["Paste emails (one per line)", "Upload CSV file"])\
    \
    if method == "Paste emails (one per line)":\
        emails_text = st.text_area("Paste emails here", height=200)\
        email_list = [e.strip() for e in emails_text.splitlines() if e.strip()]\
    else:\
        csv_file = st.file_uploader("Upload CSV", type=["csv"])\
        email_list = []\
        if csv_file:\
            df = pd.read_csv(csv_file)\
            # Try to find email column automatically\
            email_col = next((col for col in df.columns if 'email' in col.lower()), None)\
            if email_col:\
                email_list = df[email_col].astype(str).dropna().tolist()\
                st.success(f"\uc0\u9989  Loaded \{len(email_list)\} emails")\
            else:\
                st.error("CSV must contain a column with 'email' in the name")\
\
st.subheader("\uc0\u55357 \u56526  Attachments (same file(s) attached to every email)")\
uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True, help="These will be attached to ALL emails")\
attachments = [(f.name, f.getvalue()) for f in uploaded_files] if uploaded_files else []\
\
if attachments:\
    st.success(f"\uc0\u9989  \{len(attachments)\} file(s) will be attached to every email")\
\
delay = st.slider("Delay between emails (seconds) - helps avoid blocks", 1, 10, 3)\
\
# SEND BUTTON\
if st.button("\uc0\u55357 \u56960  SEND ALL EMAILS", type="primary", use_container_width=True):\
    if not sender_email or not password or not subject or not body_template:\
        st.error("\uc0\u10060  Please fill in email, password, subject and body")\
    elif len(email_list) == 0:\
        st.error("\uc0\u10060  No recipients found")\
    else:\
        st.info(f"\uc0\u55357 \u56548  Starting to send **\{len(email_list)\}** personalized emails...")\
        \
        progress_bar = st.progress(0)\
        status_text = st.empty()\
        log = st.expander("\uc0\u55357 \u56540  Live Sending Log", expanded=True)\
        \
        success_count = 0\
        failed_count = 0\
        \
        for i, email in enumerate(email_list):\
            status_text.text(f"Sending \{i+1\}/\{len(email_list)\} \uc0\u8594  \{email\}")\
            \
            ok, message = send_email(\
                sender_email=sender_email,\
                password=password,\
                to_email=email,\
                subject=subject,\
                body_template=body_template,\
                attachments=attachments,\
                is_html=is_html,\
                delay=delay\
            )\
            \
            with log:\
                st.write(message)\
            \
            if ok:\
                success_count += 1\
            else:\
                failed_count += 1\
                \
            progress_bar.progress((i + 1) / len(email_list))\
            sleep(delay)\
        \
        st.success(f"\uc0\u55356 \u57225  Finished! \u9989  Success: \{success_count\} | \u10060  Failed: \{failed_count\}")\
        st.balloons()\
\
st.caption("Made with \uc0\u10084 \u65039  for you \'95 Safe & runs only on your computer")}