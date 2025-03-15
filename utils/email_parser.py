import re
import base64
from datetime import datetime
import config.settings as settings

def is_important_email(email_data):
    """Determine if an email is important based on subject, sender, and body content."""
    subject = email_data.get('subject', '').lower()
    sender = email_data.get('sender', '').lower()
    body = email_data.get('body', '').lower()

    # Check if sender is in the list of important senders
    if any(re.search(pattern, sender) for pattern in settings.IMPORTANT_EMAIL_CRITERIA['important_senders']):
        return True

    # Check if subject or body contains any important keywords
    for keyword in settings.IMPORTANT_EMAIL_CRITERIA['important_subjects']:
        if re.search(r'\b' + re.escape(keyword) + r'\b', subject):
            return True

    for keyword in settings.IMPORTANT_EMAIL_CRITERIA['important_keywords']:
        if re.search(r'\b' + re.escape(keyword) + r'\b', body):
            return True

    return False

def extract_email_data(message):
    """Extract relevant data from an email message."""
    headers = message['payload']['headers']
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    sender = next(header['value'] for header in headers if header['name'] == 'From')
    body = ''
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = part['body']['data']
                break
    return {
        'subject': subject,
        'sender': sender,
        'body': body
    }
