import re
import base64
from datetime import datetime
import config.settings as settings
from transformers import pipeline

# Initialize the text classification pipeline
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

def extract_job_details(text):
    """Extract job-related details using basic pattern matching"""
    job_details = {
        'job_title': '',
        'company': '',
        'location': '',
        'deadline': ''
    }
    
    # Simple pattern matching for job titles (customize based on your needs)
    job_title_patterns = ['job title:', 'position:', 'role:']
    for pattern in job_title_patterns:
        match = re.search(f'{pattern}\s*([^\n]*)', text, re.IGNORECASE)
        if match:
            job_details['job_title'] = match.group(1).strip()
            break
    
    # Simple pattern matching for company
    company_patterns = ['company:', 'organization:', 'employer:']
    for pattern in company_patterns:
        match = re.search(f'{pattern}\s*([^\n]*)', text, re.IGNORECASE)
        if match:
            job_details['company'] = match.group(1).strip()
            break
    
    # Simple pattern matching for location
    location_patterns = ['location:', 'place:', 'city:']
    for pattern in location_patterns:
        match = re.search(f'{pattern}\s*([^\n]*)', text, re.IGNORECASE)
        if match:
            job_details['location'] = match.group(1).strip()
            break
    
    # Simple pattern matching for deadline
    deadline_patterns = ['deadline:', 'due by:', 'apply by:']
    for pattern in deadline_patterns:
        match = re.search(f'{pattern}\s*([^\n]*)', text, re.IGNORECASE)
        if match:
            job_details['deadline'] = match.group(1).strip()
            break
    
    return job_details

def is_important_email(email_data):
    """Determine if an email is important using extracted job details"""
    subject = email_data.get('subject', '')
    sender = email_data.get('sender', '')
    body = email_data.get('body', '')

    job_details = extract_job_details(body)
    return any(job_details.values())  # Check if any job-related details are found

def extract_email_data(message):
    """Extract relevant data from an email message"""
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
