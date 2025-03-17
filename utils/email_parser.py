import re
import config.settings as settings
import logging
from datetime import datetime
from config.settings import IMPORTANCE_KEYWORDS
from transformers import pipeline

logger = logging.getLogger(__name__)

# Initialize the text classification pipeline
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

def extract_email_data(message_data):
    """Extract relevant data from Gmail message"""
    headers = message_data.get('payload', {}).get('headers', [])
    
    # Extract headers
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
    date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), None)
    
    # Extract body content
    body = extract_body_from_payload(message_data.get('payload', {}))
    
    return {
        'subject': subject,
        'sender': sender,
        'date': date_str,
        'body': body
    }

def extract_job_details(text, pattern):
    """Extract details using regex pattern"""
    if not text or not pattern:
        return None
        
    # Properly escape the pattern for regex
    pattern = re.escape(pattern)
    
    # Fix: Separate the search and the if statement
    match = re.search(fr'{pattern}\s*([^\n]*)', text, re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    return None

def extract_job_title(text):
    """Extract job title from email text"""
    patterns = ['job title:', 'position:', 'role:']
    
    for pattern in patterns:
        result = extract_job_details(text, pattern)
        if result:
            return result
    
    return None

def extract_company(text):
    """Extract company name from email text"""
    patterns = ['company:', 'organization:', 'employer:']
    
    for pattern in patterns:
        result = extract_job_details(text, pattern)
        if result:
            return result
            
    return None

def extract_location(text):
    """Extract job location from email text"""
    patterns = ['location:', 'city:', 'place:']
    
    for pattern in patterns:
        result = extract_job_details(text, pattern)
        if result:
            return result
            
    return None

def extract_salary(text):
    """Extract salary information from email text"""
    patterns = ['salary:', 'compensation:', 'pay:']
    
    for pattern in patterns:
        result = extract_job_details(text, pattern)
        if result:
            return result
            
    return None

def extract_body_from_payload(payload):
    """Recursively extract text from message parts"""
    if not payload:
        return ""
        
    # If this part is text
    if 'body' in payload and 'data' in payload['body']:
        import base64
        from email.utils import parseaddr
        
        # Decode the base64 data
        text = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='replace')
        return text
        
    # If this is multipart, process each part
    if 'parts' in payload:
        text_parts = []
        for part in payload['parts']:
            text_parts.append(extract_body_from_payload(part))
        return "\n".join(text_parts)
        
    return ""

def is_important_email(email_data):
    """Determine if an email is important based on content"""
    if not email_data:
        return False
        
    subject = email_data.get('subject', '').lower()
    sender = email_data.get('sender', '').lower()
    body = email_data.get('body', '').lower()
    
    # We now know IMPORTANCE_KEYWORDS is a list from our test
    # No need to split it
    keywords = [k.lower() for k in settings.IMPORTANCE_KEYWORDS]
    
    for keyword in keywords:
        if keyword in subject or keyword in body:
            logger.info(f"Found important keyword: '{keyword}' in email from {sender}")
            return True
    
    # Additional logic for determining importance can be added here
    # For example, checking for specific senders, urgency indicators, etc.
    
    return False
